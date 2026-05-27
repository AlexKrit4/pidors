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

    public static ChafaConsoleLayout Measure(int width, int height) => MeasureCompact(width, height);

    private static ChafaConsoleLayout MeasureCompact(int width, int height)
    {
        width = Math.Max(MinWidth, width);
        height = Math.Max(MinHeight, height);

        var headerRows = width >= 100 ? 2 : 1;
        var bottomRows = height >= 34 ? 5 : height >= 28 ? 4 : 3;
        bottomRows = Math.Min(bottomRows, height - headerRows - 8);

        var bottomTop = height - bottomRows;
        var boardTop = headerRows;
        var boardHeight = Math.Max(8, bottomTop - boardTop);

        if (boardTop + boardHeight + bottomRows > height)
        {
            boardHeight = Math.Max(8, height - headerRows - bottomRows);
            bottomTop = boardTop + boardHeight;
            bottomRows = height - bottomTop;
        }

        var statusRows = 1;
        var statsRows = 1;
        var helpRows = bottomRows >= 5 && width < 90 ? 1 : 0;
        var logRows = Math.Max(1, bottomRows - statusRows - statsRows - helpRows);

        var logTop = bottomTop;
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
            HelpRows = helpRows
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
        HelpRows == other.HelpRows;
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
