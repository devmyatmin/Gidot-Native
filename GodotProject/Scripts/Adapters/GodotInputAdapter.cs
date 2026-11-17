using Godot;

namespace StrandedDeep.Adapters;

/// <summary>
/// Thin input facade for gameplay code migrated from the original input layer.
/// The action names are logical identifiers; bind them in Godot Input Map after
/// the original Rewired action map has been audited.
/// </summary>
public static class GodotInputAdapter
{
    public static readonly StringName MoveLeft = "move_left";
    public static readonly StringName MoveRight = "move_right";
    public static readonly StringName MoveForward = "move_forward";
    public static readonly StringName MoveBackward = "move_backward";
    public static readonly StringName Jump = "jump";
    public static readonly StringName Interact = "interact";
    public static readonly StringName Crouch = "crouch";
    public static readonly StringName Sprint = "sprint";
    public static readonly StringName Inventory = "inventory";
    public static readonly StringName Pause = "pause";

    /// <summary>Returns a normalized 2D movement vector (forward is negative Y).</summary>
    public static Vector2 GetMoveVector(float deadzone = -1.0f)
    {
        return Input.GetVector(
            MoveLeft,
            MoveRight,
            MoveForward,
            MoveBackward,
            deadzone);
    }

    public static bool IsPressed(StringName action)
    {
        return Input.IsActionPressed(action);
    }

    public static bool IsJustPressed(StringName action)
    {
        return Input.IsActionJustPressed(action);
    }

    public static bool IsJustReleased(StringName action)
    {
        return Input.IsActionJustReleased(action);
    }
}
