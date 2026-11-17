using Godot;

namespace StrandedDeep.Adapters;

public enum RuntimePlatform
{
    Unknown,
    Android,
    Windows,
    Linux,
    MacOS,
    IOS
}

/// <summary>
/// Centralizes platform checks so gameplay logic does not call Windows-only
/// native APIs directly. Platform integrations must be explicitly registered.
/// </summary>
public static class PlatformAdapter
{
    public static RuntimePlatform Current => OS.GetName() switch
    {
        "Android" => RuntimePlatform.Android,
        "Windows" => RuntimePlatform.Windows,
        "Linux" => RuntimePlatform.Linux,
        "macOS" => RuntimePlatform.MacOS,
        "iOS" => RuntimePlatform.IOS,
        _ => RuntimePlatform.Unknown
    };

    public static bool IsAndroid => Current == RuntimePlatform.Android;

    // No Steam native backend is configured in this project yet.
    // In particular, Libraries/Platform/steam_api64.dll is Windows x64 only.
    public static bool IsSteamIntegrationAvailable => false;
}
