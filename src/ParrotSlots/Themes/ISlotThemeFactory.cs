using ParrotSlots.Core;

namespace ParrotSlots.Themes;

public interface ISlotThemeFactory
{
    string ThemeName { get; }
    ISymbolSet CreateSymbolSet();
    IPayTable CreatePayTable();
    IBoardGenerator CreateBoardGenerator();
}
