namespace ParrotSlots.Interpreter;

public enum CommandResultType
{
    Continue,
    ShowRules,
    ShowBalance,
    Quit
}

public sealed class CommandResult
{
    public CommandResult(CommandResultType type, string? message = null)
    {
        Type = type;
        Message = message;
    }

    public CommandResultType Type { get; }
    public string? Message { get; }
}
