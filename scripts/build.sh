#!/usr/bin/env bash
# Builds build/Detour.app. With a Developer ID in the keychain it is signed with it
# (the audio-capture permission is tied to that identity, so it survives updates);
# NOTARY_PROFILE=<notarytool profile> also notarizes and makes build/Detour.dmg.
set -euo pipefail
cd "$(dirname "$0")/.."
APP="build/Detour.app"

SIGN_IDENTITY="${SIGN_IDENTITY:-$(security find-identity -v -p codesigning 2>/dev/null \
    | grep "Developer ID Application" | head -1 | sed -E 's/.*"(.*)".*/\1/')}"

swift build -c release -Xswiftc -target -Xswiftc arm64-apple-macos14.2
rm -rf "$APP" && mkdir -p "$APP/Contents/MacOS"
cp .build/release/Detour "$APP/Contents/MacOS/Detour"
cp Resources/Info.plist "$APP/Contents/Info.plist"

# The icon is an Icon Composer document: actool renders it into Assets.car (Liquid Glass on
# macOS 26+) plus an AppIcon.icns fallback. actool ships with Xcode 26, not the Command Line Tools.
if xcrun --find actool >/dev/null 2>&1; then
    mkdir -p "$APP/Contents/Resources"
    xcrun actool Resources/AppIcon.icon --compile "$APP/Contents/Resources" \
        --platform macosx --minimum-deployment-target 14.2 --app-icon AppIcon \
        --output-partial-info-plist build/icon-partial.plist >/dev/null
else
    echo "warning: actool not found (it comes with Xcode 26), building without an icon"
fi

if [ -n "$SIGN_IDENTITY" ]; then
    codesign --force --options runtime --timestamp --sign "$SIGN_IDENTITY" "$APP"
else
    echo "warning: no Developer ID found, ad-hoc signing (macOS will ask for the permission again after each build)"
    codesign --force --sign - "$APP"
fi
codesign --verify --strict "$APP"

if [ -n "${NOTARY_PROFILE:-}" ]; then
    KEYCHAIN=(--keychain "$HOME/Library/Keychains/login.keychain-db")
    ditto -c -k --keepParent "$APP" build/Detour.zip
    xcrun notarytool submit build/Detour.zip --keychain-profile "$NOTARY_PROFILE" "${KEYCHAIN[@]}" --wait
    xcrun stapler staple "$APP"
    rm -f build/Detour.dmg build/Detour.zip
    hdiutil create -volname Detour -srcfolder "$APP" -ov -format UDZO build/Detour.dmg
    codesign --force --timestamp --sign "$SIGN_IDENTITY" build/Detour.dmg
    xcrun notarytool submit build/Detour.dmg --keychain-profile "$NOTARY_PROFILE" "${KEYCHAIN[@]}" --wait
    xcrun stapler staple build/Detour.dmg
    spctl --assess --type open --context context:primary-signature -v build/Detour.dmg
fi
echo "built $APP"
