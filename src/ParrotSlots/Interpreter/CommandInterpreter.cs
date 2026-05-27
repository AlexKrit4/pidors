namespace ParrotSlots.Interpreter;

public sealed class CommandInterpreter
{
    public CommandResult Execute(string input, SlotMachine game)
    {
        if (string.IsNullOrWhiteSpace(input))
        {
            return new CommandResult(CommandResultType.Continue, "Empty command.");
        }

        var parts = input.Split(';', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
        var expressions = parts.Select(ParseCommand).ToList();
        var program = expressions.Count == 1 ? expressions[0] : new SequenceExpression(expressions);
        return program.Execute(game);
    }

    private static ICommandExpression ParseCommand(string token)
    {
        var pieces = token.Split(' ', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
        if (pieces.Length == 0)
        {
            throw new InvalidOperationException("Invalid command.");
        }

        return pieces[0].ToLowerInvariant() switch
        {
            "spin" => new SpinExpression(),
            "auto" => new AutoSpinExpression(ParseInt(pieces, 1, "auto")),
            "bet" => new BetExpression(ParseInt(pieces, 1, "bet")),
            "balance" => new BalanceExpression(),
            "rules" => new RulesExpression(),
            "quit" => new QuitExpression(),
            _ => throw new InvalidOperationException($"Unknown command: {pieces[0]}")
        };
    }

    private static int ParseInt(string[] pieces, int index, string commandName)
    {
        if (pieces.Length <= index || !int.TryParse(pieces[index], out var value))
        {
            throw new InvalidOperationException($"{commandName} requires an integer argument.");
        }

        return value;
    }
}
