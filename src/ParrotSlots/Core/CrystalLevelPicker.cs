using ParrotSlots.Settings;

namespace ParrotSlots.Core;

internal static class CrystalLevelPicker
{
    public static int NextLevel(IRandomSource random)
    {
        var roll = random.Next(1000);
        var level = roll switch
        {
            < 720 => 1,
            < 880 => 2,
            < 955 => 3,
            < 985 => 4,
            < 995 => 5,
            < 999 => 6,
            _ => 7
        };

        return Math.Min(level, GameSettings.Instance.MaxCrystalLevel);
    }
}
