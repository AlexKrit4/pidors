namespace ParrotSlots.Rules;

public sealed class PayoutResult
{
    public PayoutResult(int winAmount, IEnumerable<string>? messages = null)
    {
        WinAmount = winAmount;
        Messages = messages?.ToList() ?? [];
    }

    public int WinAmount { get; }
    public IReadOnlyList<string> Messages { get; }
}
