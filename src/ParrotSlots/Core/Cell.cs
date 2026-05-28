namespace ParrotSlots.Core;

public sealed record Cell(CellKind Kind, ParrotColor Color, int Level, string Display)
{
    public static Cell Empty { get; } = new(CellKind.Empty, default, 0, " · ");

    public bool IsEmpty => Kind == CellKind.Empty;
    public bool IsParrot => Kind == CellKind.Parrot;
    public bool IsCrystal => Kind == CellKind.Crystal;

    public static Cell Parrot(ParrotColor color, string display) =>
        new(CellKind.Parrot, color, 0, display);

    public static Cell Crystal(ParrotColor color, int level, string display) =>
        new(CellKind.Crystal, color, level, display);
}
