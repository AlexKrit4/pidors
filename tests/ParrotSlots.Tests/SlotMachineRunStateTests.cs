using ParrotSlots;
using ParrotSlots.Builder;
using ParrotSlots.Core;
using ParrotSlots.Rules;
using ParrotSlots.Settings;
using ParrotSlots.Testing;
using ParrotSlots.Themes;
using ParrotSlots.Wallet;

namespace ParrotSlots.Tests;

public class SlotMachineRunStateTests
{
    [Fact]
    public void Spin_LosesWhenSpinLimitExpiresBeforeTarget()
    {
        var factory = new PirateParrotThemeFactory();
        var game = CreateGame(factory, CreateNoWinBoard(factory.CreateSymbolSet()), startingBalance: 1000, initialBet: 10);

        var firstSpin = game.Spin();
        Assert.NotNull(firstSpin);
        Assert.True(firstSpin.NetResult < 0);

        for (var i = 1; i < GameSettings.Instance.SpinLimit; i++)
        {
            Assert.NotNull(game.Spin());
        }

        Assert.Equal(GameRunState.Lost, game.RunState);
        Assert.True(game.IsGameOver);
        Assert.Equal(0, game.SpinsLeft);
        Assert.False(game.CanSpin());
    }

    [Fact]
    public void Spin_WinsWhenTargetBalanceIsReached()
    {
        var factory = new PirateParrotThemeFactory();
        var game = CreateGame(factory, CreateJackpotBoard(factory.CreateSymbolSet()), startingBalance: 1000, initialBet: 100);

        var result = game.Spin();

        Assert.NotNull(result);
        Assert.True(game.Balance >= game.TargetBalance);
        Assert.Equal(GameRunState.Won, game.RunState);
        Assert.True(game.IsGameOver);
    }

    private static SlotMachine CreateGame(PirateParrotThemeFactory factory, GameBoard board, int startingBalance, int initialBet) =>
        new SlotMachineBuilder()
            .WithTheme(factory)
            .WithWallet(new WalletProxy(new PlayerWallet(startingBalance, initialBet)))
            .WithPayoutRules(new CrystalCollectionRule())
            .WithBoardGenerator(new FixedBoardGenerator(board))
            .WithRandom(new SeededRandomSource(1))
            .Build();

    private static GameBoard CreateNoWinBoard(ISymbolSet symbols)
    {
        var cells = CreateFilledBoard(symbols, ParrotColor.Blue);
        cells[1, 1] = Cell.Parrot(ParrotColor.Red, symbols.GetParrotDisplay(ParrotColor.Red));
        return new GameBoard(cells);
    }

    private static GameBoard CreateJackpotBoard(ISymbolSet symbols)
    {
        var cells = CreateFilledBoard(symbols, ParrotColor.Blue);
        cells[1, 1] = Cell.Parrot(ParrotColor.Red, symbols.GetParrotDisplay(ParrotColor.Red));
        cells[1, 2] = Cell.Crystal(ParrotColor.Red, 7, symbols.GetCrystalDisplay(ParrotColor.Red, 7));
        return new GameBoard(cells);
    }

    private static Cell[,] CreateFilledBoard(ISymbolSet symbols, ParrotColor color)
    {
        var cells = new Cell[3, 3];
        for (var row = 0; row < 3; row++)
        {
            for (var col = 0; col < 3; col++)
            {
                cells[row, col] = Cell.Crystal(color, 1, symbols.GetCrystalDisplay(color, 1));
            }
        }

        return cells;
    }
}
