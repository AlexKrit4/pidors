using ParrotSlots.Core;

namespace ParrotSlots.Rules;

public sealed class CrystalCollectionRule : IPayoutRule
{
    private readonly CollectionEngine _engine = new();

    public string Name => "Crystal Collection";

    public PayoutResult Evaluate(PayoutContext context)
    {
        var result = _engine.Run(context.Board, context.Bet, context.PayTable, context.Symbols, context.Random);
        context.RunningTotal += result.WinAmount;
        context.Messages.AddRange(result.Messages);
        return new PayoutResult(result.WinAmount, result.Messages);
    }
}
