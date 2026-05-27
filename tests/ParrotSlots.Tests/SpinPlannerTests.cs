using ParrotSlots.Core;
using ParrotSlots.Core.Animation;
using ParrotSlots.Themes;

namespace ParrotSlots.Tests;

public class SpinPlannerTests
{
    [Fact]
    public void Build_AdjacentCrystal_ProducesParrotStep()
    {
        var factory = new PirateParrotThemeFactory();
        var symbols = factory.CreateSymbolSet();
        var payTable = factory.CreatePayTable();
        var board = CreateAdjacentBoard(symbols);

        var plan = SpinPlanner.Build(board, bet: 10, payTable, symbols, new SeededRandomSource(1));

        Assert.Contains(plan.Phases, phase => phase is ParrotStepPhase);
        Assert.True(plan.TotalWin > 0);
    }

    private static GameBoard CreateAdjacentBoard(ISymbolSet symbols)
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
