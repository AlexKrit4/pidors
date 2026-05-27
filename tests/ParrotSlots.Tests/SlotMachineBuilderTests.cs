using ParrotSlots.Builder;
using ParrotSlots.Rules;
using ParrotSlots.Settings;
using ParrotSlots.Themes;
using ParrotSlots.Wallet;

namespace ParrotSlots.Tests;

public class SlotMachineBuilderTests
{
    [Fact]
    public void Build_WithoutTheme_Throws()
    {
        var builder = new SlotMachineBuilder()
            .WithWallet(new PlayerWallet(100, 10))
            .WithPayoutRules(new CrystalCollectionRule());

        Assert.Throws<InvalidOperationException>(() => builder.Build());
    }

    [Fact]
    public void Build_WithoutWallet_Throws()
    {
        var builder = new SlotMachineBuilder()
            .WithTheme(new PirateParrotThemeFactory())
            .WithPayoutRules(new CrystalCollectionRule());

        Assert.Throws<InvalidOperationException>(() => builder.Build());
    }

    [Fact]
    public void Build_WithoutRules_Throws()
    {
        var builder = new SlotMachineBuilder()
            .WithTheme(new PirateParrotThemeFactory())
            .WithWallet(new PlayerWallet(100, 10));

        Assert.Throws<InvalidOperationException>(() => builder.Build());
    }

    [Fact]
    public void Build_WithRequiredParts_CreatesGame()
    {
        var game = new SlotMachineBuilder()
            .WithTheme(new PirateParrotThemeFactory())
            .WithWallet(new PlayerWallet(GameSettings.Instance.StartingBalance, 10))
            .WithPayoutRules(new CrystalCollectionRule())
            .Build();

        Assert.Equal("Pirate Parrots", game.ThemeName);
    }
}
