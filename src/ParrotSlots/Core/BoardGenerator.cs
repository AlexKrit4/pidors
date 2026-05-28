using ParrotSlots.Settings;

namespace ParrotSlots.Core;

public sealed class BoardGenerator : IBoardGenerator
{
    private readonly ISymbolSet _symbols;

    public BoardGenerator(string themeName, ISymbolSet symbols)
    {
        ThemeName = themeName;
        _symbols = symbols;
    }

    public string ThemeName { get; }

    public GameBoard CreateBoard(IRandomSource random)
    {
        var settings = GameSettings.Instance;
        var cells = new Cell[settings.RowCount, settings.ColCount];

        for (var row = 0; row < settings.RowCount; row++)
        {
            for (var col = 0; col < settings.ColCount; col++)
            {
                var color = ParrotColors.All[random.Next(ParrotColors.All.Count)];
                cells[row, col] = CreateCrystal(color, 1);
            }
        }

        PlaceParrots(cells, random, settings, _symbols);
        return new GameBoard(cells);
    }

    internal Cell CreateCrystal(ParrotColor color, int level) =>
        Cell.Crystal(color, level, _symbols.GetCrystalDisplay(color, level));

    internal Cell CreateParrot(ParrotColor color) =>
        Cell.Parrot(color, _symbols.GetParrotDisplay(color));

    private static void PlaceParrots(Cell[,] cells, IRandomSource random, GameSettings settings, ISymbolSet symbols)
    {
        var positions = new List<(int Row, int Col)>();
        var attempts = 0;

        while (positions.Count < settings.ParrotCount && attempts < 500)
        {
            attempts++;
            var candidate = (random.Next(settings.RowCount), random.Next(settings.ColCount));
            if (positions.Any(existing => IsAdjacent(existing, candidate)))
            {
                continue;
            }

            positions.Add(candidate);
        }

        if (positions.Count < settings.ParrotCount)
        {
            throw new InvalidOperationException("Unable to place parrots without adjacency.");
        }

        for (var i = 0; i < ParrotColors.All.Count; i++)
        {
            var color = ParrotColors.All[i];
            var (row, col) = positions[i];
            cells[row, col] = Cell.Parrot(color, symbols.GetParrotDisplay(color));
        }
    }

    private static bool IsAdjacent((int Row, int Col) first, (int Row, int Col) second) =>
        Math.Abs(first.Row - second.Row) + Math.Abs(first.Col - second.Col) == 1;
}
