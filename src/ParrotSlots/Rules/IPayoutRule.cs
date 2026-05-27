namespace ParrotSlots.Rules;

public interface IPayoutRule
{
    string Name { get; }
    PayoutResult Evaluate(PayoutContext context);
}
