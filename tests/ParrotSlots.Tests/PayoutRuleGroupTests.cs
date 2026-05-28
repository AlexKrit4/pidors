using ParrotSlots.Core;
using ParrotSlots.Rules;
using ParrotSlots.Themes;

namespace ParrotSlots.Tests;

public class PayoutRuleGroupTests
{
    [Fact]
    public void Evaluate_SumsChildRuleWins()
    {
        var factory = new PirateParrotThemeFactory();
        var payTable = factory.CreatePayTable();
        var symbols = factory.CreateSymbolSet();
        var board = CreateAdjacentRedCrystalBoard(symbols);

        var single = new CrystalCollectionRule().Evaluate(
            new PayoutContext(board.Clone(), bet: 10, payTable, symbols, new SeededRandomSource(7)));

        var combined = new PayoutRuleGroup("test", [new CrystalCollectionRule()]).Evaluate(
            new PayoutContext(board.Clone(), bet: 10, payTable, symbols, new SeededRandomSource(7)));

        Assert.Equal(single.WinAmount, combined.WinAmount);
        Assert.True(combined.WinAmount > 0);
    }

    private static GameBoard CreateAdjacentRedCrystalBoard(ISymbolSet symbols)
    {
        var cells = new Cell[3, 3];
        for (var row = 0; row < 3; row++)
        {
            for (var col = 0; col < 3; col++)
            {
                cells[row, col] = Cell.Crystal(ParrotColor.Blue, 1, symbols.GetCrystalDisplay(ParrotColor.Blue, 1));
            }
        }

        cells[1, 1] = Cell.Parrot(ParrotColor.Red, symbols.GetParrotDisplay(ParrotColor.Red));
        cells[1, 2] = Cell.Crystal(ParrotColor.Red, 1, symbols.GetCrystalDisplay(ParrotColor.Red, 1));
        return new GameBoard(cells);
    }
}
