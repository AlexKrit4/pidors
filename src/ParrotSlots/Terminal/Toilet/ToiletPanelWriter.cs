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

        IReadOnlyList<string> lines;
        try
        {
            lines = ToiletCli.IsAvailable()
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
            Console.Write("\x1b[49m"); // default transparent background
            Console.Write(line);
            Console.Write("\x1b[0m");
        }
    }

}
