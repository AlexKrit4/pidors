using ParrotSlots.Core;
using ParrotSlots.Core.Animation;

namespace ParrotSlots;

public sealed class AnimatedSpinSession
{
    internal AnimatedSpinSession(SlotMachine machine, SpinPlan plan, int bet)
    {
        Machine = machine;
        Plan = plan;
        Bet = bet;
    }

    public SlotMachine Machine { get; }
    public SpinPlan Plan { get; }
    public int Bet { get; }
    public int TotalWin => Plan.TotalWin;
    public GameBoard FinalBoard => Plan.FinalBoard;
    public IReadOnlyList<string> Messages => Plan.Messages;
    public bool Completed { get; private set; }

    public void MarkCompleted()
    {
        if (Completed)
        {
            return;
        }

        Completed = true;
        Machine.CompleteAnimatedSpin(this);
    }
}
