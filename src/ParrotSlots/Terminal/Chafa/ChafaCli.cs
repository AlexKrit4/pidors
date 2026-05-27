using System.Diagnostics;
using System.Text;

namespace ParrotSlots.Terminal.Chafa;

public sealed class ChafaCli
{
    private static bool? _isAvailable;
    private static string? _executablePath;
    private static readonly string SharedTempPath = Path.Combine(Path.GetTempPath(), "parrot-slots-chafa.png");

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

    public static string RenderPng(ReadOnlySpan<byte> pngBytes, int columns, int rows, string symbols = "block+space+braille")
    {
        var executable = ExecutablePath;
        if (executable is null)
        {
            throw new InvalidOperationException(
                "Chafa is not installed. Install it from https://hpjansson.org/chafa/ " +
                "(Windows: scoop install chafa, or MSYS2: pacman -S chafa).");
        }

        columns = Math.Max(20, columns);
        rows = Math.Max(10, rows);

        var arguments = new StringBuilder();
        arguments.Append("--format symbols ");
        arguments.Append("--symbols ").Append(symbols).Append(' ');
        arguments.Append("--colors full ");
        arguments.Append("--color-space rgb ");
        arguments.Append("--font-ratio 1/2 ");
        arguments.Append("--stretch ");
        arguments.Append("--polite on ");
        arguments.Append("--animate off ");
        arguments.Append("-w 1 ");
        arguments.Append("-O 0 ");
        arguments.Append("-s ").Append(columns).Append('x').Append(rows).Append(' ');

        try
        {
            File.WriteAllBytes(SharedTempPath, pngBytes);
            arguments.Append('"').Append(SharedTempPath).Append('"');

            using var process = new Process();
            process.StartInfo = new ProcessStartInfo
            {
                FileName = executable,
                Arguments = arguments.ToString(),
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                StandardOutputEncoding = Encoding.UTF8,
                CreateNoWindow = true
            };

            process.Start();
            var output = process.StandardOutput.ReadToEnd();
            var error = process.StandardError.ReadToEnd();
            process.WaitForExit(5000);

            if (process.ExitCode != 0)
            {
                throw new InvalidOperationException($"Chafa failed ({process.ExitCode}): {error}".Trim());
            }

            return output;
        }
        catch (IOException ex)
        {
            throw new InvalidOperationException($"Chafa temp file failed: {ex.Message}", ex);
        }
    }

    private static string? FindExecutable()
    {
        foreach (var name in new[] { "chafa", "chafa.exe", "Chafa.exe" })
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
