namespace ParrotSlots.Wallet;

public sealed class PlayerWallet : IWallet
{
    public PlayerWallet(int startingBalance, int initialBet)
    {
        Balance = startingBalance;
        CurrentBet = initialBet;
    }

    public int Balance { get; private set; }
    public int CurrentBet { get; private set; }

    public bool TrySetBet(int amount, out string? error)
    {
        CurrentBet = amount;
        error = null;
        return true;
    }

    public bool TryDeductBet(out string? error)
    {
        Balance -= CurrentBet;
        error = null;
        return true;
    }

    public void AddWin(int amount) => Balance += amount;
}
