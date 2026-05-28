namespace ParrotSlots.Core;

public sealed class SpinResult
{
    public SpinResult(GameBoard board, int bet, int winAmount, IReadOnlyList<string> messages)
    {
        Board = board;
        Bet = bet;
        WinAmount = winAmount;
        Messages = messages;
    }

    public GameBoard Board { get; }
    public int Bet { get; }
    public int WinAmount { get; }
    public IReadOnlyList<string> Messages { get; }
    public int NetResult => WinAmount - Bet;
}
