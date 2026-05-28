namespace ParrotSlots.Core;

public interface ISymbolSet
{
    string ThemeName { get; }
    string GetParrotDisplay(ParrotColor color);
    string GetCrystalDisplay(ParrotColor color, int level);
}
