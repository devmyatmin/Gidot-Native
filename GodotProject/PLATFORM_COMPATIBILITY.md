# Godot platform compatibility

## Target

- Engine: Godot 4.7 .NET edition
- Runtime target: .NET 9.0 for Android export
- Primary platform: Android ARM64
- Project folder: this directory

Godot 4.7 documentation notes that C# Android support is experimental. It also documents .NET 9 as the Android target requirement following newer Google Play target requirements. Keep the Godot .NET editor/export templates and .NET SDK versions aligned.

## Native and engine-specific dependencies

The original DLL inventory under `../Libraries/` is retained as reference material. It is not automatically included in this Godot project.

| Original dependency | Godot-side treatment |
|---|---|
| `Rewired_DirectInput.dll` | Windows/DirectInput backend; do not package for Android. Use `GodotInputAdapter` and Godot Input Map. |
| `Rewired_Windows.dll`, `Rewired_Windows_Functions.dll` | Windows-only Rewired backends; do not package for Android. |
| `Rewired_Core.dll` | Keep as reference until actual API usage and compatibility are audited; do not assume it can be dropped or loaded unchanged. |
| `steam_api64.dll` | Windows x64 native library; never package for Android ARM64. Steam integration remains disabled until a platform-appropriate implementation is selected. |
| `com.rlabrecque.steamworks.net.dll` | Managed Steamworks wrapper; do not reference until its native dependency and target-platform compatibility are resolved. |
| `UnityEngine.*.dll` | Unity engine API assemblies; not Godot runtime dependencies. Replace calls through adapters while preserving gameplay semantics. |
| `Assembly-CSharp*.dll` | Original compiled gameplay assemblies; reference/audit inputs, not automatically copied into the Godot runtime. |

## Input migration

`Scripts/Adapters/GodotInputAdapter.cs` defines logical actions only. The exact action list, names, axes, deadzones, and controller bindings must be populated from the original Rewired configuration or verified gameplay call sites. Do not treat the provisional action names as a recovered original mapping.

Use Godot Project Settings -> Input Map to bind keyboard, gamepad, and touch UI actions. Touch controls should be implemented as Godot UI controls and emit the same logical actions; do not hard-code desktop-only input into gameplay logic.

## Build boundary

The `GodotProject/` project does not reference the archived `../Libraries/` directory. Add only dependencies that are proven to support the target platform and are actually used by the migrated code. Keep Windows native libraries out of Android export filters.

## Current status

- Godot project metadata exists.
- Platform and input facade scaffolding exists.
- Original Rewired action map has not yet been recovered from the repository's available text files.
- Steam integration is intentionally disabled.
- No gameplay source has been added to this project yet.
- No Android APK build or device runtime test has been claimed.
