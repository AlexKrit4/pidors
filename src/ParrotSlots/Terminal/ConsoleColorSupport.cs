using System.Runtime.InteropServices;
using System.Runtime.Versioning;

namespace ParrotSlots.Terminal;

internal static class ConsoleColorSupport
{
    private const int StdOutputHandle = -11;
    private const uint EnableVirtualTerminalProcessing = 0x0004;

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern IntPtr GetStdHandle(int nStdHandle);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool GetConsoleMode(IntPtr hConsoleHandle, out uint lpMode);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool SetConsoleMode(IntPtr hConsoleHandle, uint dwMode);

    [SupportedOSPlatform("windows")]
    public static void EnableWindowsVirtualTerminalProcessing()
    {
        if (!OperatingSystem.IsWindows())
        {
            return;
        }

        var handle = GetStdHandle(StdOutputHandle);
        if (handle == IntPtr.Zero || !GetConsoleMode(handle, out var mode))
        {
            return;
        }

        SetConsoleMode(handle, mode | EnableVirtualTerminalProcessing);
    }
}
