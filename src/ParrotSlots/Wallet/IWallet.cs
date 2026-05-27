namespace ParrotSlots.Wallet;

public interface IWallet
{
    int Balance { get; }
    int CurrentBet { get; }
    bool TrySetBet(int amount, out string? error);
    bool TryDeductBet(out string? error);
    void AddWin(int amount);
}
