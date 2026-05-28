# Pirate Parrots Slots — Docs

Документация по архитектуре и паттернам проекта.

## Файлы

| Файл | Назначение |
|------|------------|
| [pattern-map.md](pattern-map.md) | Краткая карта паттернов и ключевых классов |
| [patterns.md](patterns.md) | Подробное описание применения паттернов |
| [uml.puml](uml.puml) | PlantUML-версия диаграммы |

## Паттерны

| Паттерн | Основные классы |
|---------|-----------------|
| Abstract Factory | `ISlotThemeFactory`, `PirateParrotThemeFactory`, `JungleParrotThemeFactory` |
| Singleton | `GameSettings` |
| Builder | `SlotMachineBuilder`, `DefaultGameDirector` |
| Composite | `IPayoutRule`, `CrystalCollectionRule`, `PayoutRuleGroup` |
| Proxy | `IWallet`, `PlayerWallet`, `WalletProxy` |
| Interpreter | `CommandInterpreter`, `ICommandExpression`, `*Expression` |
| Observer | `IGameObservable`, `IGameObserver`, `GameEventHub`, observers |

## Mermaid Diagram

```mermaid
classDiagram
direction LR

namespace Core {
    class GameBoard
    class Cell
    class ParrotColor
    class IPayTable {
        <<interface>>
    }
    class IBoardGenerator {
        <<interface>>
    }
    class ISymbolSet {
        <<interface>>
    }
    class CollectionEngine
    class BoardGenerator
}

namespace Settings {
    class GameSettings {
        <<Singleton>>
    }
}

namespace Themes {
    class ISlotThemeFactory {
        <<interface>>
        +CreateSymbolSet()
        +CreatePayTable()
        +CreateBoardGenerator()
    }
    class PirateParrotThemeFactory
    class JungleParrotThemeFactory
}

namespace Builder {
    class SlotMachineBuilder
    class DefaultGameDirector
}

namespace Rules {
    class IPayoutRule {
        <<interface>>
        +Evaluate(PayoutContext)
    }
    class CrystalCollectionRule
    class PayoutRuleGroup
    class PayoutContext
}

namespace Wallet {
    class IWallet {
        <<interface>>
    }
    class PlayerWallet
    class WalletProxy
}

namespace Interpreter {
    class CommandInterpreter
    class ICommandExpression {
        <<interface>>
        +Execute(SlotMachine)
    }
    class SpinExpression
    class AutoSpinExpression
    class BetExpression
    class BalanceExpression
    class RulesExpression
    class QuitExpression
    class SequenceExpression
}

namespace Observer {
    class IGameObservable {
        <<interface>>
    }
    class IGameObserver {
        <<interface>>
        +OnGameEvent(GameEvent)
    }
    class GameEventHub
    class ConsoleRenderer
    class StatisticsTracker
    class GameLogger
    class TerminalUiObserver
}

class SlotMachine
class Program

ISlotThemeFactory <|.. PirateParrotThemeFactory
ISlotThemeFactory <|.. JungleParrotThemeFactory
ISlotThemeFactory ..> ISymbolSet
ISlotThemeFactory ..> IPayTable
ISlotThemeFactory ..> IBoardGenerator

DefaultGameDirector --> GameEventHub
DefaultGameDirector --> SlotMachineBuilder
SlotMachineBuilder --> SlotMachine
SlotMachineBuilder --> ISlotThemeFactory
SlotMachineBuilder --> IWallet
SlotMachineBuilder --> IPayoutRule
SlotMachineBuilder --> IGameObservable

SlotMachine --> IBoardGenerator
SlotMachine --> IPayoutRule
SlotMachine --> IWallet
SlotMachine --> IGameObservable
SlotMachine --> CollectionEngine : via rule

IPayoutRule <|.. CrystalCollectionRule
IPayoutRule <|.. PayoutRuleGroup
CrystalCollectionRule --> CollectionEngine
PayoutRuleGroup o-- IPayoutRule

IWallet <|.. PlayerWallet
IWallet <|.. WalletProxy
WalletProxy --> PlayerWallet

CommandInterpreter --> SlotMachine
CommandInterpreter --> ICommandExpression
ICommandExpression <|.. SpinExpression
ICommandExpression <|.. AutoSpinExpression
ICommandExpression <|.. BetExpression
ICommandExpression <|.. BalanceExpression
ICommandExpression <|.. RulesExpression
ICommandExpression <|.. QuitExpression
ICommandExpression <|.. SequenceExpression
SequenceExpression o-- ICommandExpression

IGameObservable <|.. GameEventHub
IGameObserver <|.. ConsoleRenderer
IGameObserver <|.. StatisticsTracker
IGameObserver <|.. GameLogger
IGameObserver <|.. TerminalUiObserver
GameEventHub o-- IGameObserver

Program --> DefaultGameDirector
```
