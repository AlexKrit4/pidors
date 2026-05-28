namespace ParrotSlots.Core;

public interface IRandomSource
{
    int Next(int maxExclusive);
    int Next(int minInclusive, int maxExclusive);
}
