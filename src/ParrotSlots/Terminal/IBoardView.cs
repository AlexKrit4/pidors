using ParrotSlots.Core;
using ParrotSlots.Graphics;

namespace ParrotSlots.Terminal;

internal interface IBoardView
{
    void SetFrame(BoardAnimationFrame frame);
    void SetBoard(GameBoard? board);
}
