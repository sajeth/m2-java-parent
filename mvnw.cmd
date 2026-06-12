@REM Licensed to the Apache Software Foundation (ASF) under one
@REM or more contributor license agreements.  See the NOTICE file
@REM distributed with this work for additional information
@REM regarding copyright ownership.  The ASF licenses this file
@REM to you under the Apache License, Version 2.0 (the
@REM "License"); you may not use this file except in compliance
@REM with the License.  You may obtain a copy of the License at
@REM
@REM   http://www.apache.org/licenses/LICENSE-2.0
@REM
@REM Unless required by applicable law or agreed to in writing,
@REM software distributed under the License is distributed on an
@REM "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
@REM KIND, either express or implied.  See the License for the
@REM specific language governing permissions and limitations
@REM under the License.
@REM
@REM Apache Maven Wrapper — https://maven.apache.org/wrapper/
@REM

@echo off
setlocal enabledelayedexpansion

set PROPERTIES=%~dp0.mvn\wrapper\maven-wrapper.properties
if not exist "%PROPERTIES%" (
    echo ERROR: %PROPERTIES% not found.
    exit /b 1
)

@REM Read distributionUrl
for /f "tokens=2 delims==" %%A in ('findstr /b "distributionUrl" "%PROPERTIES%"') do (
    set DISTRIBUTION_URL=%%A
)
if "%DISTRIBUTION_URL%"=="" (
    echo ERROR: distributionUrl not found in %PROPERTIES%.
    exit /b 1
)

@REM Extract filename from URL
for %%F in (%DISTRIBUTION_URL%) do set DISTRIBUTION_FILE=%%~nxF

@REM Strip -bin.zip suffix to get directory name
set DISTRIBUTION_NAME=%DISTRIBUTION_FILE:-bin.zip=%

if "%MAVEN_USER_HOME%"=="" set MAVEN_USER_HOME=%USERPROFILE%\.m2
set WRAPPER_DIR=%MAVEN_USER_HOME%\wrapper\dists\%DISTRIBUTION_NAME%

@REM Find extracted Maven home
set MAVEN_HOME=
for /d %%D in ("%WRAPPER_DIR%\apache-maven-*") do (
    if exist "%%D\bin\mvn.cmd" set MAVEN_HOME=%%D
)

if "%MAVEN_HOME%"=="" (
    mkdir "%WRAPPER_DIR%" 2>nul
    set TMP_ZIP=%WRAPPER_DIR%\%DISTRIBUTION_FILE%
    echo Downloading Apache Maven: %DISTRIBUTION_URL%
    powershell -Command "Invoke-WebRequest -Uri '%DISTRIBUTION_URL%' -OutFile '%TMP_ZIP%'"
    powershell -Command "Expand-Archive -Path '%TMP_ZIP%' -DestinationPath '%WRAPPER_DIR%' -Force"
    del "%TMP_ZIP%" 2>nul
    for /d %%D in ("%WRAPPER_DIR%\apache-maven-*") do (
        if exist "%%D\bin\mvn.cmd" set MAVEN_HOME=%%D
    )
)

if "%MAVEN_HOME%"=="" (
    echo ERROR: Failed to locate Maven executable after extraction.
    exit /b 1
)

"%MAVEN_HOME%\bin\mvn.cmd" %*
