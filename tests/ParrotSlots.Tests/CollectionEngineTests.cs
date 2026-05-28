using ParrotSlots.Builder;
using ParrotSlots.Core;
using ParrotSlots.Rules;
using ParrotSlots.Testing;
using ParrotSlots.Themes;
using ParrotSlots.Wallet;

namespace ParrotSlots.Tests;

public class CollectionEngineTests
{
    [Fact]
    public void AdjacentRedCrystal_IsCollectedByRedParrot()
    {
        var factory = new PirateParrotThemeFactory();
        var symbols = factory.CreateSymbolSet();
        var payTable = factory.CreatePayTable();
        var board = CreateAdjacentCollectionBoard(symbols);

        var game = new SlotMachineBuilder()
            .WithTheme(factory)
            .WithWallet(new PlayerWallet(100, 10))
            .WithPayoutRules(new CrystalCollectionRule())
            .WithBoardGenerator(new FixedBoardGenerator(board))
            .WithRandom(new SeededRandomSource(123))
            .Build();

        var result = game.EvaluateBoard(board, bet: 10);

        Assert.True(result.WinAmount > 0);
        Assert.Contains(result.Messages, message => message.Contains("Red parrot collected"));
    }

    [Fact]
    public void SeededBoardGeneration_IsRepeatable()
    {
        var factory = new PirateParrotThemeFactory();
        var generator = factory.CreateBoardGenerator();
        var random = new SeededRandomSource(999);

        var first = generator.CreateBoard(random);
        random = new SeededRandomSource(999);
        var second = generator.CreateBoard(random);

        Assert.Equal(first.ToString(), second.ToString());
    }

    [Fact]
    public void GetReachableCrystals_FindsOrthogonalNeighbor()
    {
        var symbols = new PirateParrotThemeFactory().CreateSymbolSet();
        var board = CreateAdjacentCollectionBoard(symbols);
        var owners = new ParrotColor?[board.Rows, board.Cols];

        var targets = CollectionEngine.GetReachableCrystals(board, owners, (1, 1), ParrotColor.Red);

        Assert.Contains((1, 2), targets);
    }

    private static GameBoard CreateAdjacentCollectionBoard(ISymbolSet symbols)
    {
        var cells = new Cell[3, 4];
        for (var row = 0; row < cells.GetLength(0); row++)
        {
            for (var col = 0; col < cells.GetLength(1); col++)
            {
                cells[row, col] = Cell.Crystal(ParrotColor.Blue, 1, symbols.GetCrystalDisplay(ParrotColor.Blue, 1));
            }
        }

        cells[1, 1] = Cell.Parrot(ParrotColor.Red, symbols.GetParrotDisplay(ParrotColor.Red));
        cells[1, 2] = Cell.Crystal(ParrotColor.Red, 1, symbols.GetCrystalDisplay(ParrotColor.Red, 1));
        return new GameBoard(cells);
    }
}
