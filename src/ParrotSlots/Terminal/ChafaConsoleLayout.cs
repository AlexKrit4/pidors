namespace ParrotSlots.Terminal;

public sealed class ChafaConsoleLayout
{
    public const int MinWidth = 40;
    public const int MinHeight = 20;

    public int Width { get; init; }
    public int Height { get; init; }
    public int HeaderRows { get; init; }
    public int BoardTop { get; init; }
    public int BoardWidth { get; init; }
    public int BoardHeight { get; init; }
    public int LogTop { get; init; }
    public int LogRows { get; init; }
    public int StatsTop { get; init; }
    public int StatsRows { get; init; }
    public int StatusTop { get; init; }
    public int StatusRows { get; init; }
    public int HelpTop { get; init; } = -1;
    public int HelpRows { get; init; }
    public bool UseToilet { get; init; }

    public static ChafaConsoleLayout Measure(int width, int height, bool useToilet = false) =>
        useToilet ? MeasureWithToilet(width, height) : MeasurePlain(width, height);

    private static ChafaConsoleLayout MeasurePlain(int width, int height)
    {
        width = Math.Max(MinWidth, width);
        height = Math.Max(MinHeight, height);

        var headerRows = width >= 110 ? 2 : width >= 70 ? 3 : 4;
        var statusRows = 1;
        var helpRows = height >= 30 ? 1 : 0;
        var minBoardRows = Math.Clamp(height / 3, 10, 24);
        var minLogRows = height >= 26 ? 3 : 2;

        var reservedBottom = statusRows + helpRows + minLogRows;
        var boardHeight = height - headerRows - reservedBottom;
        if (boardHeight < minBoardRows)
        {
            boardHeight = Math.Max(8, height - headerRows - statusRows - helpRows - minLogRows);
        }

        var logRows = height - headerRows - boardHeight - statusRows - helpRows;
        logRows = Math.Clamp(logRows, minLogRows, 8);

        boardHeight = Math.Max(8, height - headerRows - logRows - statusRows - helpRows);
        var boardTop = headerRows;
        var logTop = boardTop + boardHeight;
        var statusTop = logTop + logRows;
        var helpTop = helpRows > 0 ? statusTop + statusRows : -1;

        return new ChafaConsoleLayout
        {
            Width = width,
            Height = height,
            HeaderRows = headerRows,
            BoardTop = boardTop,
            BoardWidth = width,
            BoardHeight = boardHeight,
            LogTop = logTop,
            LogRows = logRows,
            StatsTop = -1,
            StatsRows = 0,
            StatusTop = statusTop,
            StatusRows = statusRows,
            HelpTop = helpTop,
            HelpRows = helpRows,
            UseToilet = false
        };
    }

    private static ChafaConsoleLayout MeasureWithToilet(int width, int height)
    {
        width = Math.Max(MinWidth, width);
        height = Math.Max(MinHeight, height);

        var headerRows = 1;
        var statsRows = width >= 110 ? 6 : width >= 80 ? 5 : 4;
        var statusRows = width >= 100 ? 5 : width >= 70 ? 4 : 3;
        var helpRows = height >= 36 ? 3 : height >= 30 ? 2 : 0;
        var logRows = width >= 100 ? 4 : 3;

        var bottomRows = statsRows + statusRows + logRows + helpRows;
        var boardHeight = Math.Max(8, height - headerRows - bottomRows);
        if (boardHeight < 10 && height >= 24)
        {
            var overflow = 10 - boardHeight;
            logRows = Math.Max(2, logRows - overflow);
            bottomRows = statsRows + statusRows + logRows + helpRows;
            boardHeight = Math.Max(8, height - headerRows - bottomRows);
        }

        var boardTop = headerRows;
        var logTop = boardTop + boardHeight;
        var statsTop = logTop + logRows;
        var statusTop = statsTop + statsRows;
        var helpTop = helpRows > 0 ? statusTop + statusRows : -1;

        return new ChafaConsoleLayout
        {
            Width = width,
            Height = height,
            HeaderRows = headerRows,
            BoardTop = boardTop,
            BoardWidth = width,
            BoardHeight = boardHeight,
            LogTop = logTop,
            LogRows = logRows,
            StatsTop = statsTop,
            StatsRows = statsRows,
            StatusTop = statusTop,
            StatusRows = statusRows,
            HelpTop = helpTop,
            HelpRows = helpRows,
            UseToilet = true
        };
    }

    public bool Matches(ChafaConsoleLayout other) =>
        Width == other.Width &&
        Height == other.Height &&
        HeaderRows == other.HeaderRows &&
        BoardTop == other.BoardTop &&
        BoardHeight == other.BoardHeight &&
        LogRows == other.LogRows &&
        StatsRows == other.StatsRows &&
        StatusRows == other.StatusRows &&
        HelpRows == other.HelpRows &&
        UseToilet == other.UseToilet;
}

internal static class ConsoleTextLayout
{
    public static string Fit(string text, int width)
    {
        if (width <= 0)
        {
            return string.Empty;
        }

        if (text.Length <= width)
        {
            return text;
        }

        if (width <= 3)
        {
            return text[..width];
        }

        return text[..(width - 3)] + "...";
    }

    public static IReadOnlyList<string> Wrap(string text, int width, int maxLines)
    {
        if (width <= 0 || maxLines <= 0)
        {
            return [];
        }

        if (string.IsNullOrEmpty(text))
        {
            return [string.Empty];
        }

        var lines = new List<string>();
        var start = 0;
        while (start < text.Length && lines.Count < maxLines)
        {
            if (text.Length - start <= width)
            {
                lines.Add(text[start..]);
                break;
            }

            var slice = text.AsSpan(start, width);
            var breakAt = slice.LastIndexOf(' ');
            if (breakAt <= 0)
            {
                lines.Add(text.Substring(start, width));
                start += width;
                continue;
            }

            lines.Add(text.Substring(start, breakAt));
            start += breakAt + 1;
        }

        if (lines.Count == maxLines && start < text.Length)
        {
            lines[^1] = Fit(lines[^1], width);
        }

        while (lines.Count < maxLines)
        {
            lines.Add(string.Empty);
        }

        return lines;
    }
}
