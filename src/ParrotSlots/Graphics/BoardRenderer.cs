using ParrotSlots.Core;
using ParrotSlots.Core.Animation;
using Raylib_cs;

namespace ParrotSlots.Graphics;

public sealed class BoardRenderer
{
    private readonly TextureCatalog _textures;

    public BoardRenderer(TextureCatalog textures) => _textures = textures;

    public (int OffsetX, int OffsetY) GetGridOrigin(int windowWidth, int windowHeight)
    {
        var gridWidth = GameConstants.GridCols * GameConstants.CellSize;
        var gridHeight = GameConstants.GridRows * GameConstants.CellSize;
        var offsetX = (windowWidth - gridWidth) / 2;
        var offsetY = (windowHeight - gridHeight - GameConstants.InfoPanelHeight) / 2;
        return (offsetX, offsetY);
    }

    public void Draw(
        GameBoard board,
        float[,]? cellOffsetY = null,
        (int Row, int Col)? movingParrotFrom = null,
        (int Row, int Col)? movingParrotTo = null,
        float movingParrotT = 1f,
        ParrotColor? movingParrotColor = null)
    {
        var (originX, originY) = GetGridOrigin(GameConstants.WindowWidth, GameConstants.WindowHeight);
        DrawGrid(originX, originY);

        for (var row = 0; row < board.Rows; row++)
        {
            for (var col = 0; col < board.Cols; col++)
            {
                if (movingParrotFrom is not null &&
                    movingParrotTo is not null &&
                    movingParrotColor is not null &&
                    row == movingParrotTo.Value.Row &&
                    col == movingParrotTo.Value.Col)
                {
                    continue;
                }

                var cell = board.Get(row, col);
                if (cell.IsEmpty)
                {
                    continue;
                }

                if (movingParrotFrom is not null &&
                    row == movingParrotFrom.Value.Row &&
                    col == movingParrotFrom.Value.Col)
                {
                    continue;
                }

                var offsetY = cellOffsetY?[row, col] ?? 0f;
                DrawCell(cell, originX, originY, row, col, offsetY);
            }
        }

        if (movingParrotFrom is not null &&
            movingParrotTo is not null &&
            movingParrotColor is not null)
        {
            var display = board.Get(movingParrotTo.Value.Row, movingParrotTo.Value.Col).Display;
            var parrotCell = Cell.Parrot(movingParrotColor.Value, display);
            var fromX = originX + movingParrotFrom.Value.Col * GameConstants.CellSize + GameConstants.CellSize / 2f;
            var fromY = originY + movingParrotFrom.Value.Row * GameConstants.CellSize + GameConstants.CellSize / 2f;
            var toX = originX + movingParrotTo.Value.Col * GameConstants.CellSize + GameConstants.CellSize / 2f;
            var toY = originY + movingParrotTo.Value.Row * GameConstants.CellSize + GameConstants.CellSize / 2f;
            var t = Math.Clamp(movingParrotT, 0f, 1f);
            var x = fromX + (toX - fromX) * t;
            var y = fromY + (toY - fromY) * t;
            DrawCellAt(parrotCell, x, y);
        }
    }

    private static void DrawGrid(int originX, int originY)
    {
        var color = new Color(255, 255, 255, 72);
        var border = new Color(255, 255, 255, 120);
        var gridWidth = GameConstants.GridCols * GameConstants.CellSize;
        var gridHeight = GameConstants.GridRows * GameConstants.CellSize;

        for (var col = 0; col <= GameConstants.GridCols; col++)
        {
            var x = originX + col * GameConstants.CellSize;
            Raylib.DrawLine(x, originY, x, originY + gridHeight, col is 0 or GameConstants.GridCols ? border : color);
        }

        for (var row = 0; row <= GameConstants.GridRows; row++)
        {
            var y = originY + row * GameConstants.CellSize;
            Raylib.DrawLine(originX, y, originX + gridWidth, y, row is 0 or GameConstants.GridRows ? border : color);
        }
    }

    private void DrawCell(Cell cell, int originX, int originY, int row, int col, float offsetY)
    {
        var x = originX + col * GameConstants.CellSize + GameConstants.CellSize / 2f;
        var y = originY + row * GameConstants.CellSize + GameConstants.CellSize / 2f + offsetY;
        DrawCellAt(cell, x, y);
    }

    private void DrawCellAt(Cell cell, float centerX, float centerY)
    {
        var texture = _textures.Get(cell);
        if (texture.Id == 0)
        {
            Raylib.DrawText(cell.Display, (int)centerX - 12, (int)centerY - 8, 16, Color.White);
            return;
        }

        var scale = GameConstants.ImageScale * GameConstants.CellSize / Math.Max(texture.Width, texture.Height);
        var width = texture.Width * scale;
        var height = texture.Height * scale;
        var pos = new System.Numerics.Vector2(centerX - width / 2f, centerY - height / 2f);
        Raylib.DrawTextureEx(texture, pos, 0f, scale, Color.White);
    }
}

public sealed class HudRenderer
{
    public void Draw(SlotMachine game, string status, IReadOnlyList<string> logLines)
    {
        Raylib.DrawText($"Balance: {game.Balance}   Bet: {game.CurrentBet}", 20, GameConstants.WindowHeight - GameConstants.InfoPanelHeight + 10, 20, Color.White);
        Raylib.DrawText(status, 20, GameConstants.WindowHeight - GameConstants.InfoPanelHeight + 35, 18, Color.Gold);

        var y = 20;
        foreach (var line in logLines.TakeLast(4))
        {
            Raylib.DrawText(line, 20, y, 16, Color.LightGray);
            y += 18;
        }

        DrawButton(new Rectangle(20, GameConstants.WindowHeight - 55, 100, 40), "BET -", false);
        DrawButton(new Rectangle(130, GameConstants.WindowHeight - 55, 100, 40), "BET +", false);
        DrawButton(new Rectangle(GameConstants.WindowWidth / 2f - 60, GameConstants.WindowHeight - 60, 120, 50), "SPIN", true);
        DrawButton(new Rectangle(GameConstants.WindowWidth - 120, GameConstants.WindowHeight - 55, 100, 40), "QUIT", false);
    }

    public bool IsSpinClicked() => Raylib.CheckCollisionPointRec(Raylib.GetMousePosition(), new Rectangle(GameConstants.WindowWidth / 2f - 60, GameConstants.WindowHeight - 60, 120, 50)) && Raylib.IsMouseButtonReleased(MouseButton.Left);

    public bool IsBetDownClicked() => Raylib.CheckCollisionPointRec(Raylib.GetMousePosition(), new Rectangle(20, GameConstants.WindowHeight - 55, 100, 40)) && Raylib.IsMouseButtonReleased(MouseButton.Left);

    public bool IsBetUpClicked() => Raylib.CheckCollisionPointRec(Raylib.GetMousePosition(), new Rectangle(130, GameConstants.WindowHeight - 55, 100, 40)) && Raylib.IsMouseButtonReleased(MouseButton.Left);

    public bool IsQuitClicked() => Raylib.CheckCollisionPointRec(Raylib.GetMousePosition(), new Rectangle(GameConstants.WindowWidth - 120, GameConstants.WindowHeight - 55, 100, 40)) && Raylib.IsMouseButtonReleased(MouseButton.Left);

    private static void DrawButton(Rectangle rect, string label, bool primary)
    {
        Raylib.DrawRectangleRec(rect, primary ? new Color(0, 180, 0, 255) : new Color(80, 80, 80, 255));
        var textWidth = Raylib.MeasureText(label, 20);
        Raylib.DrawText(label, (int)(rect.X + rect.Width / 2 - textWidth / 2), (int)(rect.Y + rect.Height / 2 - 10), 20, Color.White);
    }
}
