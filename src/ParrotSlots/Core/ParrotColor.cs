namespace ParrotSlots.Core;

public enum ParrotColor
{
    Red = 1,
    Purple = 2,
    Green = 3,
    Blue = 4
}

public static class ParrotColors
{
    public static IReadOnlyList<ParrotColor> All { get; } =
        [ParrotColor.Red, ParrotColor.Purple, ParrotColor.Green, ParrotColor.Blue];
}
