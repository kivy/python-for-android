#!/bin/bash
set -euxo pipefail

# Find the built APK file
APK_FILE=$(find dist -name "*.apk" -print -quit)

if [ -z "$APK_FILE" ]; then
    echo "Error: No APK file found in dist/"
    exit 1
fi

echo "Installing $APK_FILE..."
adb install "$APK_FILE"

# Extract package and activity names
AAPT2_PATH=$(find ${ANDROID_HOME}/build-tools/ -name aapt2 | sort -r | head -n 1)
APP_PACKAGE=$(${AAPT2_PATH} dump badging "${APK_FILE}" | awk -F"'" '/package: name=/{print $2}')
APP_ACTIVITY=$(${AAPT2_PATH} dump badging "${APK_FILE}" | awk -F"'" '/launchable-activity/ {print $2}')

echo "Launching $APP_PACKAGE/$APP_ACTIVITY..."
adb shell am start -n "$APP_PACKAGE/$APP_ACTIVITY" -a android.intent.action.MAIN -c android.intent.category.LAUNCHER

# Poll for test completion with timeout
MAX_WAIT=300
POLL_INTERVAL=5
elapsed=0

echo "Waiting for tests to complete (max ${MAX_WAIT}s)..."

while [ $elapsed -lt $MAX_WAIT ]; do
    # Dump current logs
    adb logcat -d -s python:I *:S > app_logs.txt

    # Check if all success patterns are present
    if grep --extended-regexp --quiet "I python[ ]+: Initialized python" app_logs.txt && \
       grep --extended-regexp --quiet "I python[ ]+: Ran 14 tests in" app_logs.txt && \
       grep --extended-regexp --quiet "I python[ ]+: OK" app_logs.txt; then
        echo "✅ SUCCESS: App launched and all unit tests passed in ${elapsed}s."
        exit 0
    fi

    # Check for early failure indicators
    if grep --extended-regexp --quiet "I python[ ]+: FAILED" app_logs.txt; then
        echo "❌ FAILURE: Tests failed after ${elapsed}s."
        echo "--- Full Logs ---"
        cat app_logs.txt
        echo "-----------------"
        exit 1
    fi

    sleep $POLL_INTERVAL
    elapsed=$((elapsed + POLL_INTERVAL))
    echo "Still waiting... (${elapsed}s elapsed)"
done

echo "❌ TIMEOUT: Tests did not complete within ${MAX_WAIT}s."
echo "--- Full Logs ---"
cat app_logs.txt
echo "-----------------"
exit 1
