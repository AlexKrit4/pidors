using ParrotSlots.Settings;
using ParrotSlots.Wallet;

namespace ParrotSlots.Tests;

public class WalletProxyTests
{
    [Fact]
    public void TrySetBet_RejectsAmountGreaterThanBalance()
    {
        var wallet = new WalletProxy(new PlayerWallet(50, 10));

        var success = wallet.TrySetBet(100, out var error);

        Assert.False(success);
        Assert.Equal("Bet exceeds current balance.", error);
        Assert.Equal(10, wallet.CurrentBet);
    }

    [Fact]
    public void TrySetBet_RejectsBelowMinimum()
    {
        var wallet = new WalletProxy(new PlayerWallet(100, 10));

        var success = wallet.TrySetBet(0, out var error);

        Assert.False(success);
        Assert.Contains("at least", error);
    }

    [Fact]
    public void TryDeductBet_RejectsWhenBalanceTooLow()
    {
        var inner = new PlayerWallet(5, 10);
        var wallet = new WalletProxy(inner);

        var success = wallet.TryDeductBet(out var error);

        Assert.False(success);
        Assert.Equal("Insufficient balance for spin.", error);
        Assert.Equal(5, wallet.Balance);
    }
}
