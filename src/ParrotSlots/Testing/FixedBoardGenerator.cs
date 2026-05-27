using ParrotSlots.Core;

namespace ParrotSlots.Testing;

public sealed class FixedBoardGenerator : IBoardGenerator
{
    private readonly GameBoard _board;

    public FixedBoardGenerator(GameBoard board, string themeName = "Test")
    {
        _board = board;
        ThemeName = themeName;
    }

    public string ThemeName { get; }

    public GameBoard CreateBoard(IRandomSource random) => _board.Clone();
}
