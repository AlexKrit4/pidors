namespace ParrotSlots.Interpreter;

public sealed class SpinExpression : ICommandExpression
{
    public CommandResult Execute(SlotMachine game)
    {
        game.Spin();
        return new CommandResult(CommandResultType.Continue);
    }
}

public sealed class AutoSpinExpression : ICommandExpression
{
    public AutoSpinExpression(int count) => Count = count;

    public int Count { get; }

    public CommandResult Execute(SlotMachine game)
    {
        for (var i = 0; i < Count; i++)
        {
            if (!game.CanSpin())
            {
                return new CommandResult(CommandResultType.Continue, "Auto spin stopped: insufficient balance.");
            }

            game.Spin();
        }

        return new CommandResult(CommandResultType.Continue);
    }
}

public sealed class BetExpression : ICommandExpression
{
    public BetExpression(int amount) => Amount = amount;

    public int Amount { get; }

    public CommandResult Execute(SlotMachine game)
    {
        game.SetBet(Amount);
        return new CommandResult(CommandResultType.Continue);
    }
}

public sealed class BalanceExpression : ICommandExpression
{
    public CommandResult Execute(SlotMachine game) =>
        new(CommandResultType.ShowBalance, $"Balance: {game.Balance}, Bet: {game.CurrentBet}");
}

public sealed class RulesExpression : ICommandExpression
{
    public CommandResult Execute(SlotMachine game) =>
        new(CommandResultType.ShowRules, game.GetRulesText());
}

public sealed class QuitExpression : ICommandExpression
{
    public CommandResult Execute(SlotMachine _) => new(CommandResultType.Quit);
}

public sealed class SequenceExpression : ICommandExpression
{
    public SequenceExpression(IEnumerable<ICommandExpression> commands) =>
        Commands = commands.ToList();

    public IReadOnlyList<ICommandExpression> Commands { get; }

    public CommandResult Execute(SlotMachine game)
    {
        CommandResult? last = null;

        foreach (var command in Commands)
        {
            last = command.Execute(game);
            if (last.Type is CommandResultType.Quit or CommandResultType.ShowRules or CommandResultType.ShowBalance)
            {
                return last;
            }
        }

        return last ?? new CommandResult(CommandResultType.Continue);
    }
}
