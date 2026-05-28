using ParrotSlots.Observer;
using ParrotSlots.Settings;

namespace ParrotSlots.Wallet;

public sealed class WalletProxy : IWallet
{
    private readonly PlayerWallet _wallet;
    private readonly IGameObservable? _observable;

    public WalletProxy(PlayerWallet wallet, IGameObservable? observable = null)
    {
        _wallet = wallet;
        _observable = observable;
    }

    public int Balance => _wallet.Balance;
    public int CurrentBet => _wallet.CurrentBet;

    public bool TrySetBet(int amount, out string? error)
    {
        var settings = GameSettings.Instance;

        if (amount < settings.MinBet)
        {
            error = $"Bet must be at least {settings.MinBet}.";
            NotifyCommandFailed(error);
            return false;
        }

        if (amount > settings.MaxBet)
        {
            error = $"Bet cannot exceed {settings.MaxBet}.";
            NotifyCommandFailed(error);
            return false;
        }

        if (amount > Balance)
        {
            error = "Bet exceeds current balance.";
            NotifyCommandFailed(error);
            return false;
        }

        if (!_wallet.TrySetBet(amount, out error))
        {
            NotifyCommandFailed(error ?? "Unable to set bet.");
            return false;
        }

        _observable?.NotifyBalanceChanged(Balance, CurrentBet);
        return true;
    }

    public bool TryDeductBet(out string? error)
    {
        if (CurrentBet > Balance)
        {
            error = "Insufficient balance for spin.";
            NotifyCommandFailed(error);
            return false;
        }

        var previous = Balance;
        if (!_wallet.TryDeductBet(out error))
        {
            NotifyCommandFailed(error ?? "Unable to deduct bet.");
            return false;
        }

        _observable?.NotifyBalanceChanged(Balance, CurrentBet);
        return true;
    }

    public void AddWin(int amount)
    {
        _wallet.AddWin(amount);
        _observable?.NotifyBalanceChanged(Balance, CurrentBet);
    }

    private void NotifyCommandFailed(string message) =>
        _observable?.NotifyCommandFailed(message);
}
