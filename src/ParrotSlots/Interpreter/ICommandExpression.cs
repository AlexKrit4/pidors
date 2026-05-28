namespace ParrotSlots.Interpreter;

public interface ICommandExpression
{
    CommandResult Execute(SlotMachine game);
}
