# Pattern Map — Pirate Parrots Slots

Краткая карта паттернов проектирования в коде игры.

## Abstract Factory

**Где:** `Themes/ISlotThemeFactory.cs`, `PirateParrotThemeFactory`, `JungleParrotThemeFactory`

Фабрика тем создаёт согласованное семейство: `ISymbolSet`, `IPayTable`, `IBoardGenerator`.

## Singleton

**Где:** `Settings/GameSettings.cs`

`GameSettings.Instance` — размер поля 7×6, 4 попугая, лимиты ставок. Реализован через `Lazy<GameSettings>`.

## Builder

**Где:** `Builder/SlotMachineBuilder.cs`, `Builder/DefaultGameDirector.cs`

Пошаговая сборка `SlotMachine`: тема, кошелёк, правила сбора, наблюдатели, RNG.

## Composite

**Где:** `Rules/IPayoutRule.cs`, `CrystalCollectionRule`, `PayoutRuleGroup`

`CrystalCollectionRule` запускает `CollectionEngine`. `PayoutRuleGroup` объединяет правила и суммирует выигрыш.

## Proxy

**Где:** `Wallet/IWallet.cs`, `PlayerWallet`, `WalletProxy`

Проверка min/max ставки и баланса, уведомления наблюдателей.

## Interpreter

**Где:** `Interpreter/CommandInterpreter.cs`, `CommandExpressions.cs`

Разбор команд `spin`, `bet N`, `auto N`, цепочки через `;`.

## Observer

**Где:** `Observer/GameEventHub`, `ConsoleRenderer`, `StatisticsTracker`, `GameLogger`

События спина, баланса и ошибок команд.

## Игровой цикл

```
spin → BoardGenerator (7×6, 4 попугая)
     → CrystalCollectionRule / CollectionEngine
         → каждый попугай собирает достижимые кристаллы своего цвета
         → каскад (падение + новые кристаллы)
     → начисление выигрыша
```
