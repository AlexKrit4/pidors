namespace ParrotSlots.Core;

public interface IBoardGenerator
{
    string ThemeName { get; }
    GameBoard CreateBoard(IRandomSource random);
}
