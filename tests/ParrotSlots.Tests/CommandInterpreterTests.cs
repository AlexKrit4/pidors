using ParrotSlots.Builder;
using ParrotSlots.Interpreter;
using ParrotSlots.Rules;
using ParrotSlots.Settings;
using ParrotSlots.Testing;
using ParrotSlots.Themes;
using ParrotSlots.Wallet;

namespace ParrotSlots.Tests;

public class CommandInterpreterTests
{
    [Fact]
    public void Execute_BetThenSpin_UpdatesBetAndPerformsSpin()
    {
        var factory = new PirateParrotThemeFactory();
        var symbols = factory.CreateSymbolSet();
        var noWinBoard = CreateIsolatedParrotBoard(symbols);

        var wallet = new WalletProxy(new PlayerWallet(100, 10));
        var game = new SlotMachineBuilder()
            .WithTheme(factory)
            .WithWallet(wallet)
            .WithPayoutRules(new CrystalCollectionRule())
            .WithBoardGenerator(new FixedBoardGenerator(noWinBoard))
            .WithRandom(new Core.SeededRandomSource(42))
            .Build();

        var interpreter = new CommandInterpreter();
        var result = interpreter.Execute("bet 20; spin", game);

        Assert.Equal(CommandResultType.Continue, result.Type);
        Assert.Equal(20, game.CurrentBet);
        Assert.Equal(80, game.Balance);
    }

    private static Core.GameBoard CreateIsolatedParrotBoard(Core.ISymbolSet symbols)
    {
        var cells = new Core.Cell[3, 3];
        for (var row = 0; row < 3; row++)
        {
            for (var col = 0; col < 3; col++)
            {
                cells[row, col] = Core.Cell.Crystal(Core.ParrotColor.Blue, 1, symbols.GetCrystalDisplay(Core.ParrotColor.Blue, 1));
            }
        }

        cells[0, 0] = Core.Cell.Parrot(Core.ParrotColor.Red, symbols.GetParrotDisplay(Core.ParrotColor.Red));
        return new Core.GameBoard(cells);
    }

    [Fact]
    public void Execute_SequenceExpression_ParsesMultipleCommands()
    {
        var expression = new SequenceExpression([
            new BetExpression(15),
            new SpinExpression(),
            new BalanceExpression()
        ]);

        var game = new DefaultGameDirector().CreateStandardGame(randomSeed: 1);
        var result = expression.Execute(game);

        Assert.Equal(CommandResultType.ShowBalance, result.Type);
        Assert.Contains("Balance:", result.Message);
    }
}
