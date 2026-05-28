using ParrotSlots.Builder;
using ParrotSlots.Interpreter;
using ParrotSlots.Observer;
using ParrotSlots.Rules;
using ParrotSlots.Settings;
using ParrotSlots.Themes;
using ParrotSlots.Wallet;

namespace ParrotSlots.Terminal;

internal static class TerminalGameBootstrap
{
    public static SlotMachine CreateGame(TerminalUiObserver uiObserver)
    {
        var settings = GameSettings.Instance;
        var hub = new GameEventHub();

        var wallet = new WalletProxy(
            new PlayerWallet(settings.StartingBalance, settings.DefaultBet),
            hub);

        return new SlotMachineBuilder()
            .WithTheme(new PirateParrotThemeFactory())
            .WithWallet(wallet)
            .WithPayoutRules(new PayoutRuleGroup("All Rules", [new CrystalCollectionRule()]))
            .WithObservable(hub)
            .WithInterpreter(new CommandInterpreter())
            .AddObserver(uiObserver)
            .AddObserver(new StatisticsTracker())
            .Build();
    }
}
