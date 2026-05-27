using ParrotSlots.Terminal.Toilet;

namespace ParrotSlots.Terminal;

internal static class ToiletPanelWriter
{
    public static void WriteBlock(ChafaConsoleLayout layout, int topRow, int rowCount, string text, ToiletBlockKind kind)
    {
        if (rowCount <= 0 || topRow >= layout.Height)
        {
            return;
        }

        ClearBlock(layout.Width, topRow, rowCount);

        IReadOnlyList<string> lines;
        try
        {
            lines = layout.UseToilet
                ? ToiletCli.RenderLines(text, layout.Width, kind, rowCount)
                : [ConsoleTextLayout.Fit(text, layout.Width)];
        }
        catch
        {
            lines = [ConsoleTextLayout.Fit(text, layout.Width)];
        }

        for (var i = 0; i < rowCount; i++)
        {
            var row = topRow + i;
            if (row >= layout.Height)
            {
                break;
            }

            var line = i < lines.Count ? lines[i] : string.Empty;
            Console.SetCursorPosition(0, row);
            Console.Write("\x1b[48;5;236m");
            Console.Write(line);
            if (line.Length < layout.Width)
            {
                Console.Write(new string(' ', layout.Width - line.Length));
            }

            Console.Write("\x1b[0m");
        }
    }

    private static void ClearBlock(int width, int topRow, int rowCount)
    {
        for (var i = 0; i < rowCount; i++)
        {
            Console.SetCursorPosition(0, topRow + i);
            Console.Write("\x1b[2K");
            Console.Write("\x1b[48;5;236m");
            Console.Write(new string(' ', width));
            Console.Write("\x1b[0m");
        }
    }
}
