# Plume TV Chill — instructions for Codex, Cowork and other agents

The user wants you to set up their Fire TV from this repository. Act on that request: run the installer and finish its verification, rather than only explaining commands.

## User-facing language and scope

Use the user's language, concise progress updates, and the visible name **Plume TV Chill**. The package remains `dev.plume.salah` solely for update compatibility with existing installs; never change that identifier during routine setup. It does not display on the TV as the application name.

## Installation workflow

1. Read `README.md` and `apps.lock.json`. Do not compile Android unless the user asks to modify the app: the signed, tested APK is in `dist/`.
2. Find Python 3.9+ and Android Platform Tools (`adb`). Install missing tools using the environment's supported dependency workflow. Do not claim connectivity until `adb devices` confirms an authorized device.
3. Ask only for information you cannot infer: the Fire TV IP if no appropriate device is connected, or which device to use if more than one is connected. The user must enable ADB on the TV and accept its first authorization prompt. You cannot bypass that physical prompt.
4. Run `python3 scripts/install.py --dry-run`, then `python3 scripts/install.py --device IP_DU_FIRE_TV --clean-downloads`. Windows can use `py -3` instead of `python3`.
5. The default installer installs Plume TV Chill and downloads the pinned, verified official versions of SmartTube (32-bit ARM), Zen IPTV Fire OS, and Home on Fire. Already-installed third-party apps are kept intact by default. Use `--update-existing` only if the user asks to update them.
6. The installer grants Home on Fire its required permission and configures its visible UI: target Plume TV Chill, accessibility, Home redirect, startup and lightweight black loading screen on Fire OS 7. It then performs an actual Home-button return test. Check `.logs/install-report.json`: only report success if `home_verified` is true and the requested app installations are confirmed.
7. On UI automation failure, inspect the saved XML in `.logs/` and the current foreground before acting. Use the current visible UI and package names; never blindly replay coordinates from another device. Keep all unrelated accessibility services and system packages unchanged. Finish the setup through supported device UI if the version differs, then rerun the Home verification.
8. No automatic cleanup of unrelated apps. `--clean-downloads` removes only this repository's download cache. If the user explicitly asks to remove the old `dev.plume`, use `scripts/cleanup.py --device IP --apply --remove-old-plume` after the Home test has succeeded. It must not remove `dev.plume.salah` or any Amazon component.
9. Netflix and Crunchyroll are not redistributed here: use their official Appstore installation as requested, checking for account/region prompts. IBO Player needs the exact edition's official download or a user-supplied authorized APK. Extra APKs can be installed with `--apk /path/to/app.apk`. Do not claim these apps are installed if only a store page has been opened. Never copy another person's logins, playlists or subscriptions.
10. Summarize what was installed, what Home points to, and any remaining user action. Fire OS 7 can impose about 5 seconds of system delay; the black screen masks it, it does not remove it. Do not promise zero delay or risk-free removal of system apps.

## Privacy and publishing

Do not publish `.logs`, `.downloads`, local APKs from a user's device, signing keys, credentials, playlists, device IPs, personal screenshots or wallpapers. These are ignored. Never add them with `git add -f`. Keep upstream GPL licensing and attribution. The third-party APKs are fetched from their publishers; only the launcher APK is in `dist/`.

## Code changes

Keep native Android Views and the low-memory constraints (AFTSS, Fire OS 7, API 28, armeabi-v7a, 1 GB RAM). No heavy runtime dependencies. App artwork is extracted automatically from installed apps, not added by hand. Keep the text-colour setting, D-pad and wallpaper support.

Run `python3 -m unittest discover -s tests -v`, `python3 scripts/install.py --dry-run`, and for Android changes `./gradlew testDebugUnitTest assembleRelease lintRelease`. Preserve the signing key for launcher updates. A CI build is not a replacement for the published personal APK's signing identity.
