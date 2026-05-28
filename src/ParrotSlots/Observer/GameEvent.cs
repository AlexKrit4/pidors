using ParrotSlots.Core;

namespace ParrotSlots.Observer;

public enum GameEventType
{
    SpinStarted,
    SpinFinished,
    BalanceChanged,
    ModifierTriggered,
    CommandFailed
}

public sealed class GameEvent
{
    public GameEvent(GameEventType type, string message, SpinResult? spinResult = null, int balance = 0, int bet = 0)
    {
        Type = type;
        Message = message;
        SpinResult = spinResult;
        Balance = balance;
        Bet = bet;
    }

    public GameEventType Type { get; }
    public string Message { get; }
    public SpinResult? SpinResult { get; }
    public int Balance { get; }
    public int Bet { get; }
}
