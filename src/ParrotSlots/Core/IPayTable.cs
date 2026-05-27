namespace ParrotSlots.Core;

public interface IPayTable
{
    string ThemeName { get; }
    int GetCrystalPayout(ParrotColor color, int level, int bet);
}
