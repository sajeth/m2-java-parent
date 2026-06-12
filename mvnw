#!/bin/sh
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# Apache Maven Wrapper — https://maven.apache.org/wrapper/
#

set -e

# Locate the project base directory (first ancestor containing .mvn/)
find_basedir() {
    WD="$(pwd)"
    while true; do
        if [ -d "$WD/.mvn" ]; then
            echo "$WD"
            return
        fi
        PARENT=$(dirname "$WD")
        if [ "$PARENT" = "$WD" ]; then
            # Reached filesystem root; fall back to cwd
            echo "$(pwd)"
            return
        fi
        WD="$PARENT"
    done
}

BASE_DIR=$(find_basedir)
PROPERTIES="$BASE_DIR/.mvn/wrapper/maven-wrapper.properties"

if [ ! -f "$PROPERTIES" ]; then
    echo "ERROR: $PROPERTIES not found." >&2
    exit 1
fi

# Read the distribution URL
DISTRIBUTION_URL=$(grep "^distributionUrl=" "$PROPERTIES" | cut -d'=' -f2-)
if [ -z "$DISTRIBUTION_URL" ]; then
    echo "ERROR: distributionUrl not found in $PROPERTIES." >&2
    exit 1
fi

DISTRIBUTION_FILE=$(basename "$DISTRIBUTION_URL")
# Strip -bin.zip or .zip suffix to get the directory name
DISTRIBUTION_NAME=$(echo "$DISTRIBUTION_FILE" | sed 's/-bin\.zip$//' | sed 's/\.zip$//')

MAVEN_USER_HOME="${MAVEN_USER_HOME:-$HOME/.m2}"
WRAPPER_DIR="$MAVEN_USER_HOME/wrapper/dists/$DISTRIBUTION_NAME"

# Locate the extracted Maven home inside the wrapper dir
MAVEN_HOME=""
if [ -d "$WRAPPER_DIR" ]; then
    MAVEN_HOME=$(find "$WRAPPER_DIR" -maxdepth 1 -type d -name 'apache-maven-*' 2>/dev/null | head -1)
fi

if [ -z "$MAVEN_HOME" ] || [ ! -f "$MAVEN_HOME/bin/mvn" ]; then
    mkdir -p "$WRAPPER_DIR"
    TMP_ZIP="$WRAPPER_DIR/$DISTRIBUTION_FILE"
    echo "Downloading Apache Maven: $DISTRIBUTION_URL"
    if command -v curl > /dev/null 2>&1; then
        curl -fsSL -o "$TMP_ZIP" "$DISTRIBUTION_URL"
    elif command -v wget > /dev/null 2>&1; then
        wget -q -O "$TMP_ZIP" "$DISTRIBUTION_URL"
    else
        echo "ERROR: curl or wget is required to download Maven." >&2
        exit 1
    fi
    unzip -q "$TMP_ZIP" -d "$WRAPPER_DIR"
    rm -f "$TMP_ZIP"
    MAVEN_HOME=$(find "$WRAPPER_DIR" -maxdepth 1 -type d -name 'apache-maven-*' | head -1)
fi

if [ -z "$MAVEN_HOME" ] || [ ! -f "$MAVEN_HOME/bin/mvn" ]; then
    echo "ERROR: Failed to locate Maven executable after extraction." >&2
    exit 1
fi

exec "$MAVEN_HOME/bin/mvn" "$@"
