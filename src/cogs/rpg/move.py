from discord.ext import commands
from math import floor


MAX_DIST = 3

class GameAction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mapping = {
            0: 'EMPTY',
            1: 'EMPTY',
            2: 'EMPTY',
            3: 'WALL',
            4: 'PLAYER'
        }
        self.board = [
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 3, 0],
            [0, 0, 0, 3, 0, 0],
            [4, 0, 0, 3, 0, 0],
        ]

    def print_board(self) -> str:
        _r = ''
        for col in self.board:
            for tile in col:
                if tile == 0:
                    _r += '🟫'
                elif tile == 3:
                    _r += '⬛'
                elif tile == 4:
                    _r += '🟦'
            _r += '\n'
        return _r
    
    @commands.command()
    async def show_board(self, ctx) -> None:
        '''Test command?'''
        await ctx.send(f'{self.print_board()}')

    @commands.command()
    async def move(self, ctx, delta_x: int, delta_y: int) -> None:
        '''First attempt at a movement command. The player will
        move in a straight line with a coordinate change of
        (delta_x, delta_y). This does attempt to include diagonals
        as it also checks for out-of-bounds movements and wall
        collision'''
        def find_player(board):
            for y in range(len(board)):
                for x in range(len(board[y])):
                    if board[y][x] == 4:
                        return x, y

        # So up is +y
        delta_y = -delta_y
        # Postitions are top-left corner
        ox, oy = find_player(self.board)
        distance = (delta_x ** 2 + delta_y ** 2) ** 0.5
        dx, dy = delta_x / distance / 100, delta_y / distance / 100

        t = 0
        x, y = ox, oy
        # 0 = success; 1 = collision; 2 = out of bounds
        code = 0
        while t < distance and t < MAX_DIST:
            # Move a bit at a time
            dd = (dx ** 2 + dy ** 2) ** 0.5
            x, y = round(x + dx, 3), round(y + dy, 3)
            tx = round(x)
            ty = round(y)
            # Check out of bounds
            if ty >= len(self.board) or ty < 0 or tx >= len(self.board[0]) or tx < 0:
                x, y = x - dx, y - dy
                code = 2
                break
            # Check collision of 8 surrounding tiles from (tx, ty)
            c = [(1, 0), (1, 1), (1, -1), (0, 0), (0, 1), (0, -1), (-1, 0), (-1, 1), (-1, -1)]
            for fx, fy in c:
                try:
                    wx = tx + fx
                    wy = ty + fy
                    if self.board[wy][wx] == 3:  # 'WALL'
                        # Do a collision check:
                        s = 1
                        if all([
                            wx < x + s,
                            wx + s > x,
                            
                            wy < y + s,
                            wy + s > y
                        ]):
                            code = 1
                            break
                except IndexError:  
                    # Out of bounds check: no matter
                    pass
            if code == 1:
                x, y = x - dx, y - dx
                break
            # Check distance
            t += dd
        # If out of bounds or collision, cancel movement and round player
        # position.
        tx, ty = round(x), round(y)
        self.board[oy][ox] = 0
        self.board[ty][tx] = 4
        # Act on code: send a message if collision or out of bounds
        if code == 1:
            await ctx.send('Collision')
        if code == 2:
            await ctx.send('Out of bounds')
        # Also add in the distance
        await ctx.send(t)
        await ctx.send(f'{self.print_board()}')


def setup(bot):
    bot.add_cog(GameAction(bot))