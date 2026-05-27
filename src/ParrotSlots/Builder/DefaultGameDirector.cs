using ParrotSlots.Interpreter;
using ParrotSlots.Observer;
using ParrotSlots.Rules;
using ParrotSlots.Settings;
using ParrotSlots.Themes;
using ParrotSlots.Wallet;

namespace ParrotSlots.Builder;

public sealed class DefaultGameDirector
{
    public SlotMachine CreateStandardGame(
        TextWriter? output = null,
        ISlotThemeFactory? themeFactory = null,
        int? randomSeed = null)
    {
        var settings = GameSettings.Instance;
        var hub = new GameEventHub();
        var stats = new StatisticsTracker();

        var wallet = new WalletProxy(
            new PlayerWallet(settings.StartingBalance, settings.DefaultBet),
            hub);

        var rules = new PayoutRuleGroup("All Rules", [new CrystalCollectionRule()]);

        var builder = new SlotMachineBuilder()
            .WithTheme(themeFactory ?? new PirateParrotThemeFactory())
            .WithWallet(wallet)
            .WithPayoutRules(rules)
            .WithObservable(hub)
            .WithInterpreter(new CommandInterpreter())
            .AddObserver(new ConsoleRenderer(output))
            .AddObserver(stats)
            .AddObserver(new GameLogger());

        if (randomSeed.HasValue)
        {
            builder.WithRandom(new Core.SeededRandomSource(randomSeed.Value));
        }

        return builder.Build();
    }
}
