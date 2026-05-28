using ParrotSlots.Graphics;

namespace ParrotSlots.Terminal;

public sealed class ChafaConsoleLayout
{
    public const int MinWidth = 40;
    public const int MinHeight = 20;
    private const int TerminalColumnsPerCell = 3;

    public int Width { get; init; }
    public int Height { get; init; }
    public int HeaderRows { get; init; }
    public int BoardTop { get; init; }
    public int BoardLeft { get; init; }
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

        var statsRows = 9; // Reserve more for toilet
        var statsTop = Math.Max(0, height - statsRows);

        var availableBoardHeight = Math.Max(1, statsTop - 1); // Extra 1 line gap
        var (boardWidth, measuredBoardHeight) = MeasureBoardSize(width, availableBoardHeight);
        var boardHeight = measuredBoardHeight;

        var maxBoardTop = Math.Max(0, statsTop - 1 - boardHeight);
        var boardTop = Math.Max(0, maxBoardTop / 2);

        return new ChafaConsoleLayout
        {
            Width = width,
            Height = height,
            HeaderRows = 0,
            BoardTop = boardTop,
            BoardLeft = Math.Max(0, (width - boardWidth) / 2),
            BoardWidth = boardWidth,
            BoardHeight = boardHeight,
            LogTop = 0,
            LogRows = 0,
            StatsTop = statsTop,
            StatsRows = statsRows,
            StatusTop = 0,
            StatusRows = 0,
            HelpTop = -1,
            HelpRows = 0
        };
    }

    public static (int Width, int Height) MeasureBoardSize(int maxWidth, int maxHeight)
    {
        maxWidth = Math.Max(1, maxWidth);
        maxHeight = Math.Max(1, maxHeight);

        var cellRows = Math.Min(
            maxWidth / (GameConstants.GridCols * TerminalColumnsPerCell),
            maxHeight / GameConstants.GridRows);

        if (cellRows <= 0)
        {
            return (maxWidth, maxHeight);
        }

        var width = GameConstants.GridCols * TerminalColumnsPerCell * cellRows;
        var height = GameConstants.GridRows * cellRows;

        return (width, height);
    }

    private static int ChooseBottomRows(int width, int height, int headerRows, int preferredBottomRows)
    {
        var minBottomRows = Math.Min(3, Math.Max(1, height - headerRows - 8));
        var maxBottomRows = Math.Clamp(preferredBottomRows, minBottomRows, Math.Max(minBottomRows, height - headerRows - 8));
        var bestRows = maxBottomRows;
        var bestCellRows = -1;

        for (var rows = maxBottomRows; rows >= minBottomRows; rows--)
        {
            var boardRows = Math.Max(1, height - headerRows - rows);
            var cellRows = Math.Min(
                width / (GameConstants.GridCols * TerminalColumnsPerCell),
                boardRows / GameConstants.GridRows);

            if (cellRows > bestCellRows)
            {
                bestCellRows = cellRows;
                bestRows = rows;
            }
        }

        return bestRows;
    }

    public bool Matches(ChafaConsoleLayout other) =>
        Width == other.Width &&
        Height == other.Height &&
        BoardTop == other.BoardTop &&
        BoardLeft == other.BoardLeft &&
        BoardWidth == other.BoardWidth &&
        BoardHeight == other.BoardHeight &&
        StatsRows == other.StatsRows;
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
