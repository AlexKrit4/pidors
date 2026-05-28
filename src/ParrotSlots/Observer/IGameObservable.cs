using ParrotSlots.Core;

namespace ParrotSlots.Observer;

public interface IGameObservable
{
    void Subscribe(IGameObserver observer);
    void NotifySpinStarted(int bet);
    void NotifySpinFinished(SpinResult result);
    void NotifyBalanceChanged(int balance, int bet);
    void NotifyModifierTriggered(string modifierName, string details);
    void NotifyCommandFailed(string reason);
}
