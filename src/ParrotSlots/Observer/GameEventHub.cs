using ParrotSlots.Core;

namespace ParrotSlots.Observer;

public sealed class GameEventHub : IGameObservable
{
    private readonly List<IGameObserver> _observers = [];

    public void Subscribe(IGameObserver observer)
    {
        if (!_observers.Contains(observer))
        {
            _observers.Add(observer);
        }
    }

    public void NotifySpinStarted(int bet) =>
        Publish(new GameEvent(GameEventType.SpinStarted, $"Spin started. Bet: {bet}.", bet: bet));

    public void NotifySpinFinished(SpinResult result) =>
        Publish(new GameEvent(GameEventType.SpinFinished,
            $"Spin finished. Win: {result.WinAmount}.",
            result));

    public void NotifyBalanceChanged(int balance, int bet) =>
        Publish(new GameEvent(GameEventType.BalanceChanged,
            $"Balance: {balance}, Bet: {bet}.",
            balance: balance,
            bet: bet));

    public void NotifyModifierTriggered(string modifierName, string details) =>
        Publish(new GameEvent(GameEventType.ModifierTriggered, $"{modifierName}: {details}"));

    public void NotifyCommandFailed(string reason) =>
        Publish(new GameEvent(GameEventType.CommandFailed, reason));

    public void NotifyGameOver(bool won, string message) =>
        Publish(new GameEvent(GameEventType.GameOver, message, won: won));

    private void Publish(GameEvent gameEvent)
    {
        foreach (var observer in _observers)
        {
            observer.OnGameEvent(gameEvent);
        }
    }
}
