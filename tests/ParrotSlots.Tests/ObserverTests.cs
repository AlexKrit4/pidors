using ParrotSlots.Core;
using ParrotSlots.Observer;
using ParrotSlots.Settings;
using ParrotSlots.Wallet;

namespace ParrotSlots.Tests;

public class ObserverTests
{
    [Fact]
    public void Observers_ReceiveSpinAndBalanceEvents()
    {
        var hub = new GameEventHub();
        var spy = new TestObserver();
        hub.Subscribe(spy);

        var wallet = new WalletProxy(new PlayerWallet(100, 10), hub);
        wallet.TryDeductBet(out _);
        hub.NotifySpinFinished(new SpinResult(CreateSampleBoard(), 10, 30, ["collected crystal"]));

        Assert.Contains(GameEventType.BalanceChanged, spy.Types);
        Assert.Contains(GameEventType.SpinFinished, spy.Types);
    }

    [Fact]
    public void StatisticsTracker_CountsSpinsAndWins()
    {
        var tracker = new StatisticsTracker();
        tracker.OnGameEvent(new GameEvent(GameEventType.SpinFinished, "done",
            new SpinResult(CreateSampleBoard(), 10, 25, [])));

        Assert.Equal(1, tracker.SpinCount);
        Assert.Equal(10, tracker.TotalWagered);
        Assert.Equal(25, tracker.TotalWon);
    }

    private static GameBoard CreateSampleBoard()
    {
        var cells = new Cell[2, 2];
        for (var row = 0; row < 2; row++)
        {
            for (var col = 0; col < 2; col++)
            {
                cells[row, col] = Cell.Crystal(ParrotColor.Green, 1, "G1");
            }
        }

        return new GameBoard(cells);
    }

    private sealed class TestObserver : IGameObserver
    {
        public List<GameEventType> Types { get; } = [];

        public void OnGameEvent(GameEvent gameEvent) => Types.Add(gameEvent.Type);
    }
}
