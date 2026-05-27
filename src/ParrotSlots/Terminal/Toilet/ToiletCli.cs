using System.Diagnostics;
using System.Text;

namespace ParrotSlots.Terminal.Toilet;

public enum ToiletBlockKind
{
    Stats,
    Status,
    Log,
    Help
}

public sealed class ToiletCli
{
    private static bool? _isAvailable;
    private static string? _executablePath;

    public static bool IsAvailable()
    {
        if (_isAvailable is not null)
        {
            return _isAvailable.Value;
        }

        _executablePath = FindExecutable();
        _isAvailable = _executablePath is not null;
        return _isAvailable.Value;
    }

    public static string? ExecutablePath => _executablePath ??= FindExecutable();

    public static IReadOnlyList<string> RenderLines(string text, int width, ToiletBlockKind kind, int maxRows)
    {
        if (string.IsNullOrWhiteSpace(text))
        {
            return [string.Empty];
        }

        var executable = ExecutablePath;
        if (executable is null)
        {
            return [ParrotSlots.Terminal.ConsoleTextLayout.Fit(text, width)];
        }

        width = Math.Max(20, width);
        maxRows = Math.Max(1, maxRows);

        var font = PickFont(width, kind);
        var filter = PickFilter(kind);
        var arguments = new StringBuilder();
        arguments.Append("-f ").Append(font).Append(' ');
        arguments.Append("-w ").Append(width).Append(' ');
        if (!string.IsNullOrEmpty(filter))
        {
            arguments.Append("-F ").Append(filter).Append(' ');
        }

        using var process = new Process();
        process.StartInfo = new ProcessStartInfo
        {
            FileName = executable,
            Arguments = arguments.ToString().Trim(),
            UseShellExecute = false,
            RedirectStandardInput = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            StandardOutputEncoding = Encoding.UTF8,
            CreateNoWindow = true
        };

        process.Start();
        process.StandardInput.Write(text);
        process.StandardInput.Close();

        var output = process.StandardOutput.ReadToEnd();
        var error = process.StandardError.ReadToEnd();
        process.WaitForExit(5000);

        if (process.ExitCode != 0)
        {
            throw new InvalidOperationException($"Toilet failed ({process.ExitCode}): {error}".Trim());
        }

        return NormalizeLines(output, width, maxRows);
    }

    private static string PickFont(int width, ToiletBlockKind kind) =>
        kind switch
        {
            ToiletBlockKind.Stats when width >= 110 => "big",
            ToiletBlockKind.Stats when width >= 80 => "standard",
            ToiletBlockKind.Stats when width >= 60 => "term",
            ToiletBlockKind.Stats => "mono12",
            ToiletBlockKind.Status when width >= 100 => "standard",
            ToiletBlockKind.Status when width >= 70 => "term",
            ToiletBlockKind.Status => "mono12",
            ToiletBlockKind.Log when width >= 90 => "term",
            ToiletBlockKind.Log => "mono12",
            ToiletBlockKind.Help => "mono12",
            _ => "term"
        };

    private static string PickFilter(ToiletBlockKind kind) =>
        kind switch
        {
            ToiletBlockKind.Stats => "metal",
            ToiletBlockKind.Status => "border",
            _ => string.Empty
        };

    private static IReadOnlyList<string> NormalizeLines(string output, int width, int maxRows)
    {
        var lines = output
            .Replace("\r\n", "\n", StringComparison.Ordinal)
            .Split('\n')
            .Select(line => StripTrailingWhitespace(line))
            .Where(line => line.Length > 0)
            .Take(maxRows)
            .Select(line => TruncateVisible(line, width))
            .ToList();

        if (lines.Count == 0)
        {
            lines.Add(string.Empty);
        }

        return lines;
    }

    private static string StripTrailingWhitespace(string line) => line.TrimEnd();

    private static string TruncateVisible(string line, int width)
    {
        if (line.Length <= width)
        {
            return line;
        }

        return width <= 3 ? line[..width] : line[..(width - 3)] + "...";
    }

    private static string? FindExecutable()
    {
        foreach (var name in new[] { "toilet", "toilet.exe" })
        {
            var path = FindOnPath(name);
            if (path is not null)
            {
                return path;
            }
        }

        return null;
    }

    private static string? FindOnPath(string fileName)
    {
        var pathEnv = Environment.GetEnvironmentVariable("PATHEXT") ?? ".EXE;.CMD;.BAT;.COM";
        var extensions = pathEnv.Split(';', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
        if (extensions.Length == 0)
        {
            extensions = [".EXE", ".CMD", ".BAT", ".COM", ""];
        }

        var paths = (Environment.GetEnvironmentVariable("PATH") ?? string.Empty)
            .Split(Path.PathSeparator, StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);

        foreach (var directory in paths)
        {
            foreach (var extension in extensions)
            {
                var candidate = Path.Combine(directory, fileName);
                if (!fileName.Contains('.', StringComparison.Ordinal) && extension.Length > 0)
                {
                    candidate += extension;
                }

                if (File.Exists(candidate))
                {
                    return candidate;
                }
            }

            var direct = Path.Combine(directory, fileName);
            if (File.Exists(direct))
            {
                return direct;
            }
        }

        return null;
    }
}
