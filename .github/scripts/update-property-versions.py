#!/usr/bin/env python3
"""Update Maven <properties> versions from mvnrepository.com comment links.

For each property in any pom.xml that is associated with a preceding comment like:
  <!-- https://mvnrepository.com/artifact/group.id/artifact-id -->
  <some.version>1.2.3</some.version>

this script queries Maven Central for the newest stable release and rewrites the
property when a newer version is available.

Modes:
  --mode minor-patch  only minor/patch bumps (default; used by Dependency Upgrade)
  --mode latest       any newer release including majors (Latest Releases)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

MVN_LINK_RE = re.compile(
    r"https?://(?:www\.)?mvnrepository\.com/artifact/"
    r"(?P<group>[^/\s]+)/(?P<artifact>[^/\s#?]+)",
    re.IGNORECASE,
)

PROPERTY_LINE_RE = re.compile(
    r"^(?P<indent>\s*)<(?P<name>[A-Za-z0-9_.-]+)>(?P<current>[^<]+)</(?P=name)>\s*$"
)

VERSIONISH_NAME_RE = re.compile(r"(?i)(version|plugin|bom)")

UNSTABLE_RE = re.compile(
    r"(?i)(?:alpha|beta|rc|cr|m\d+|milestone|snapshot|preview|ea|dev|atlassian)",
)

CENTRAL_SEARCH = "https://search.maven.org/solrsearch/select"
USER_AGENT = (
    "m2-java-parent-property-updater/1.0 (+https://github.com/sajeth/m2-java-parent)"
)


def parse_semver_parts(version: str) -> tuple[int, ...] | None:
    core = version.split("-", 1)[0].split("_", 1)[0]
    parts: list[int] = []
    for piece in core.split("."):
        if piece.isdigit():
            parts.append(int(piece))
            continue
        # Stop at trailing qualifiers glued into the last segment (e.g. Final).
        m = re.match(r"(\d+)", piece)
        if m and parts:
            parts.append(int(m.group(1)))
            break
        return None if not parts else tuple(parts)
    return tuple(parts) if parts else None


def is_stable(version: str) -> bool:
    return UNSTABLE_RE.search(version) is None


def is_allowed_bump(current: str, candidate: str, mode: str) -> bool:
    if candidate == current:
        return False
    cur = parse_semver_parts(current)
    new = parse_semver_parts(candidate)
    if cur is None or new is None:
        return mode == "latest" and candidate != current
    width = max(len(cur), len(new), 3)
    cur_p = cur + (0,) * (width - len(cur))
    new_p = new + (0,) * (width - len(new))
    if new_p <= cur_p:
        return False
    if mode == "latest":
        return True
    return cur_p[0] == new_p[0]


def _http_get(url: str, timeout: int = 20) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _best_stable(versions: list[str]) -> str | None:
    stable = [v for v in versions if v and is_stable(v)]
    if not stable:
        return None

    def sort_key(v: str) -> tuple:
        parts = parse_semver_parts(v)
        return (parts or (0,), v)

    return sorted(stable, key=sort_key)[-1]


def fetch_latest_version(group: str, artifact: str, retries: int = 3) -> str | None:
    """Resolve newest stable release via repo1 metadata, then Maven Central search."""
    meta_url = (
        "https://repo1.maven.org/maven2/"
        f"{group.replace('.', '/')}/{artifact}/maven-metadata.xml"
    )
    query = f"g:{group} AND a:{artifact}"
    search_url = (
        f"{CENTRAL_SEARCH}?{urllib.parse.urlencode({'q': query, 'rows': '1', 'wt': 'json'})}"
    )
    last_error: Exception | None = None

    for attempt in range(retries):
        try:
            # 1) Prefer repo1 maven-metadata.xml (search index is often stale).
            try:
                xml = _http_get(meta_url).decode("utf-8", errors="replace")
                versions = re.findall(r"<version>([^<]+)</version>", xml)
                best = _best_stable(versions)
                if best:
                    return best
                release = re.search(r"<release>([^<]+)</release>", xml)
                latest_tag = re.search(r"<latest>([^<]+)</latest>", xml)
                for match in (release, latest_tag):
                    if match and is_stable(match.group(1)):
                        return match.group(1)
            except urllib.error.HTTPError as http_err:
                if http_err.code != 404:
                    raise

            # 2) Fallback: Maven Central search latestVersion.
            payload = json.loads(_http_get(search_url))
            docs = payload.get("response", {}).get("docs", [])
            if docs:
                latest = docs[0].get("latestVersion")
                if latest and is_stable(latest):
                    return latest
            return None
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            time.sleep(1.0 * (attempt + 1))
    print(f"  ! failed to query {group}:{artifact}: {last_error}", file=sys.stderr, flush=True)
    return None


def iter_pom_files(root: Path) -> list[Path]:
    return sorted(
        p
        for p in root.rglob("pom.xml")
        if "target" not in p.parts and "target.nosync" not in p.parts
    )


def update_pom(path: Path, mode: str) -> list[str]:
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines(keepends=True)
    changes: list[str] = []
    out: list[str] = []
    in_properties = False
    pending_ga: tuple[str, str] | None = None

    for line in lines:
        stripped = line.strip()

        if not in_properties:
            out.append(line)
            if re.match(r"<properties(\s|>|$)", stripped):
                in_properties = True
                pending_ga = None
            continue

        if stripped.startswith("</properties"):
            in_properties = False
            pending_ga = None
            out.append(line)
            continue

        link = MVN_LINK_RE.search(line)
        if link:
            pending_ga = (link.group("group"), link.group("artifact"))
            out.append(line)
            continue

        prop = PROPERTY_LINE_RE.match(line.rstrip("\n\r"))
        if prop and pending_ga:
            name = prop.group("name")
            current = prop.group("current").strip()
            indent = prop.group("indent")
            group, artifact = pending_ga
            # Consume the link after the first property that follows it.
            pending_ga = None

            if (
                current
                and not current.startswith("${")
                and VERSIONISH_NAME_RE.search(name)
            ):
                latest = fetch_latest_version(group, artifact)
                time.sleep(0.05)
                if latest and is_allowed_bump(current, latest, mode):
                    newline = "\n" if line.endswith("\n") else ""
                    out.append(f"{indent}<{name}>{latest}</{name}>{newline}")
                    changes.append(
                        f"{path}: {name}: {current} -> {latest} ({group}:{artifact})"
                    )
                    print(f"  ↑ {path}: {name}: {current} -> {latest}", flush=True)
                    continue
                print(
                    f"  = {path}: {name} {current} "
                    f"(latest {latest or 'n/a'}, mode={mode}) — skip",
                    flush=True,
                )

        out.append(line)

    new_text = "".join(out)
    if new_text != original:
        path.write_text(new_text, encoding="utf-8")
    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("minor-patch", "latest"),
        default="minor-patch",
        help="Bump policy",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repository root",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    poms = iter_pom_files(root)
    print(f"Scanning {len(poms)} pom.xml files (mode={args.mode})", flush=True)
    all_changes: list[str] = []
    for pom in poms:
        all_changes.extend(update_pom(pom, args.mode))

    summary_path = Path("property-version-updates.md")
    if all_changes:
        summary_path.write_text(
            "## Property version updates\n\n"
            + "\n".join(f"- `{c}`" for c in all_changes)
            + "\n",
            encoding="utf-8",
        )
        print(f"\nUpdated {len(all_changes)} propert(y/ies).", flush=True)
    else:
        summary_path.write_text(
            "No property version updates available.\n",
            encoding="utf-8",
        )
        print("\nNo property version updates available.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
