namespace ParrotSlots.Rules;

public sealed class PayoutRuleGroup : IPayoutRule
{
    private readonly List<IPayoutRule> _children = [];

    public PayoutRuleGroup(string name, IEnumerable<IPayoutRule>? children = null)
    {
        Name = name;
        if (children is not null)
        {
            _children.AddRange(children);
        }
    }

    public string Name { get; }

    public void Add(IPayoutRule rule) => _children.Add(rule);

    public PayoutResult Evaluate(PayoutContext context)
    {
        var total = 0;
        var messages = new List<string>();

        foreach (var rule in _children)
        {
            var result = rule.Evaluate(context);
            total += result.WinAmount;
            messages.AddRange(result.Messages);
        }

        return new PayoutResult(total, messages);
    }
}
