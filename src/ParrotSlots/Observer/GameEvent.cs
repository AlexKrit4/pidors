using ParrotSlots.Core;

namespace ParrotSlots.Observer;

public enum GameEventType
{
    SpinStarted,
    SpinFinished,
    BalanceChanged,
    ModifierTriggered,
    CommandFailed,
    GameOver
}

public sealed class GameEvent
{
    public GameEvent(GameEventType type, string message, SpinResult? spinResult = null, int balance = 0, int bet = 0, bool? won = null)
    {
        Type = type;
        Message = message;
        SpinResult = spinResult;
        Balance = balance;
        Bet = bet;
        Won = won;
    }

    public GameEventType Type { get; }
    public string Message { get; }
    public SpinResult? SpinResult { get; }
    public int Balance { get; }
    public int Bet { get; }
    public bool? Won { get; }
}
