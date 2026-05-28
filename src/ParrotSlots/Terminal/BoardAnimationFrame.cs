using ParrotSlots.Core;

namespace ParrotSlots.Terminal;

public sealed class BoardAnimationFrame
{
    public GameBoard? Board { get; init; }
    public float[,]? CellOffsetY { get; init; }
    public (int Row, int Col)? MovingParrotFrom { get; init; }
    public (int Row, int Col)? MovingParrotTo { get; init; }
    public float MovingParrotT { get; init; } = 1f;
    public ParrotColor? MovingParrotColor { get; init; }
}
