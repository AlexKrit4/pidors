using System.Globalization;
using Terminal.Gui;
using TuiAttribute = Terminal.Gui.Attribute;
using TuiColor = Terminal.Gui.Color;

namespace ParrotSlots.Terminal.Chafa;

public static class AnsiTerminalWriter
{
    private static readonly (TuiColor Color, byte R, byte G, byte B)[] Palette =
    [
        (TuiColor.Black, 0, 0, 0),
        (TuiColor.Red, 170, 0, 0),
        (TuiColor.Green, 0, 170, 0),
        (TuiColor.Brown, 170, 170, 0),
        (TuiColor.Blue, 0, 0, 170),
        (TuiColor.Magenta, 170, 0, 170),
        (TuiColor.Cyan, 0, 170, 170),
        (TuiColor.White, 170, 170, 170),
        (TuiColor.Gray, 85, 85, 85),
        (TuiColor.BrightRed, 255, 85, 85),
        (TuiColor.BrightGreen, 85, 255, 85),
        (TuiColor.BrightYellow, 255, 255, 85),
        (TuiColor.BrightBlue, 85, 85, 255),
        (TuiColor.BrightMagenta, 255, 85, 255),
        (TuiColor.BrightCyan, 85, 255, 255),
        (TuiColor.White, 255, 255, 255)
    ];

    public static void Draw(View view, Rect bounds, string ansiText, TuiColor defaultForeground, TuiColor defaultBackground)
    {
        var fg = defaultForeground;
        var bg = defaultBackground;
        var reverse = false;
        var x = 0;
        var y = 0;
        TuiColor? currentFg = null;
        TuiColor? currentBg = null;

        for (var i = 0; i < ansiText.Length; i++)
        {
            var ch = ansiText[i];
            if (ch == '\x1b' && i + 1 < ansiText.Length)
            {
                if (ansiText[i + 1] == '[' && TryConsumeCsi(ansiText, ref i, ref fg, ref bg, ref reverse, defaultForeground, defaultBackground))
                {
                    continue;
                }

                if (TryConsumeSimpleEscape(ansiText, ref i))
                {
                    continue;
                }

                continue;
            }

            if (ch == '\r')
            {
                continue;
            }

            if (ch == '\n')
            {
                x = 0;
                y++;
                if (y >= bounds.Height)
                {
                    return;
                }

                continue;
            }

            if (ch == '\t' || ch == '\a' || ch == '\b')
            {
                continue;
            }

            if (x >= bounds.Width)
            {
                continue;
            }

            var effFg = reverse ? bg : fg;
            var effBg = reverse ? fg : bg;
            if (currentFg != effFg || currentBg != effBg)
            {
                Application.Driver.SetAttribute(new TuiAttribute(effFg, effBg));
                currentFg = effFg;
                currentBg = effBg;
            }

            view.Move(x, y);
            Application.Driver.AddRune(new Rune(ch));
            x++;
        }
    }

    private static bool TryConsumeCsi(
        string text,
        ref int index,
        ref TuiColor fg,
        ref TuiColor bg,
        ref bool reverse,
        TuiColor defaultForeground,
        TuiColor defaultBackground)
    {
        var start = index + 2;
        var i = start;
        while (i < text.Length)
        {
            var ch = text[i];
            if (ch >= 0x40 && ch <= 0x7E)
            {
                if (ch == 'm')
                {
                    ApplySgr(text.AsSpan(start, i - start), ref fg, ref bg, ref reverse, defaultForeground, defaultBackground);
                }

                index = i;
                return true;
            }

            i++;
        }

        index = text.Length - 1;
        return true;
    }

    private static bool TryConsumeSimpleEscape(string text, ref int index)
    {
        if (index + 1 >= text.Length)
        {
            return true;
        }

        switch (text[index + 1])
        {
            case '(':
            case ')':
            case '*':
            case '+':
            case '-':
            case '.':
            case '/':
                index += 2;
                return true;
            case ']':
                var end = text.IndexOf('\x07', index + 2);
                if (end >= 0)
                {
                    index = end;
                    return true;
                }

                var st = text.IndexOf("\x1b\\", index + 2, StringComparison.Ordinal);
                if (st >= 0)
                {
                    index = st + 1;
                    return true;
                }

                index = text.Length - 1;
                return true;
            default:
                index++;
                return true;
        }
    }

    private static void ApplySgr(
        ReadOnlySpan<char> code,
        ref TuiColor fg,
        ref TuiColor bg,
        ref bool reverse,
        TuiColor defaultForeground,
        TuiColor defaultBackground)
    {
        if (code.IsEmpty || (code.Length == 1 && code[0] == '0'))
        {
            fg = defaultForeground;
            bg = defaultBackground;
            reverse = false;
            return;
        }

        var parts = code.ToString().Split(';', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
        for (var i = 0; i < parts.Length; i++)
        {
            if (!int.TryParse(parts[i], NumberStyles.Integer, CultureInfo.InvariantCulture, out var value))
            {
                continue;
            }

            switch (value)
            {
                case 0:
                    fg = defaultForeground;
                    bg = defaultBackground;
                    reverse = false;
                    break;
                case 1:
                    break;
                case 7:
                    reverse = true;
                    break;
                case 22:
                case 27:
                    reverse = false;
                    break;
                case 38 when i + 4 < parts.Length && parts[i + 1] == "2":
                    fg = MapRgb(ParseByte(parts[i + 2]), ParseByte(parts[i + 3]), ParseByte(parts[i + 4]));
                    i += 4;
                    break;
                case 48 when i + 4 < parts.Length && parts[i + 1] == "2":
                    bg = MapRgb(ParseByte(parts[i + 2]), ParseByte(parts[i + 3]), ParseByte(parts[i + 4]));
                    i += 4;
                    break;
                case >= 30 and <= 37:
                    fg = MapAnsi(value - 30, bright: false);
                    break;
                case >= 90 and <= 97:
                    fg = MapAnsi(value - 90, bright: true);
                    break;
                case >= 40 and <= 47:
                    bg = MapAnsi(value - 40, bright: false);
                    break;
                case >= 100 and <= 107:
                    bg = MapAnsi(value - 100, bright: true);
                    break;
            }
        }
    }

    private static byte ParseByte(string value) =>
        byte.TryParse(value, NumberStyles.Integer, CultureInfo.InvariantCulture, out var parsed) ? parsed : (byte)0;

    private static TuiColor MapAnsi(int index, bool bright)
    {
        TuiColor[] colors = bright
            ? [TuiColor.DarkGray, TuiColor.BrightRed, TuiColor.BrightGreen, TuiColor.BrightYellow,
                TuiColor.BrightBlue, TuiColor.BrightMagenta, TuiColor.BrightCyan, TuiColor.White]
            : [TuiColor.Black, TuiColor.Red, TuiColor.Green, TuiColor.Brown,
                TuiColor.Blue, TuiColor.Magenta, TuiColor.Cyan, TuiColor.White];

        return colors[Math.Clamp(index, 0, colors.Length - 1)];
    }

    private static TuiColor MapRgb(byte r, byte g, byte b)
    {
        var best = TuiColor.White;
        var bestDistance = int.MaxValue;

        foreach (var (color, pr, pg, pb) in Palette)
        {
            var distance = (r - pr) * (r - pr) + (g - pg) * (g - pg) + (b - pb) * (b - pb);
            if (distance < bestDistance)
            {
                bestDistance = distance;
                best = color;
            }
        }

        return best;
    }
}
