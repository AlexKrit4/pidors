using ParrotSlots.Core;

namespace ParrotSlots.Rules;

public sealed class PayoutContext
{
    public PayoutContext(GameBoard board, int bet, IPayTable payTable, ISymbolSet symbols, IRandomSource random)
    {
        Board = board;
        Bet = bet;
        PayTable = payTable;
        Symbols = symbols;
        Random = random;
    }

    public GameBoard Board { get; }
    public int Bet { get; }
    public IPayTable PayTable { get; }
    public ISymbolSet Symbols { get; }
    public IRandomSource Random { get; }
    public int RunningTotal { get; set; }
    public List<string> Messages { get; } = [];
}
