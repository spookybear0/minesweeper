import threading
import pyglet
import random
import time
import os

os.chdir(os.path.dirname(os.path.realpath(__file__)))

window = pyglet.window.Window(600, 600)

img_0 = pyglet.image.load("resources/0.png")
img_1 = pyglet.image.load("resources/1.png")
img_2 = pyglet.image.load("resources/2.png")
img_3 = pyglet.image.load("resources/3.png")
img_4 = pyglet.image.load("resources/4.png")
img_5 = pyglet.image.load("resources/5.png")
img_6 = pyglet.image.load("resources/6.png")
img_7 = pyglet.image.load("resources/7.png")
img_8 = pyglet.image.load("resources/8.png")

numbers = {1: img_1, 2: img_2, 3: img_3, 4: img_4, 5: img_5, 6: img_6, 7: img_7, 8: img_8}

img_flag = pyglet.image.load("resources/flag.png")
img_tile = pyglet.image.load("resources/tile.png")
img_mine = pyglet.image.load("resources/mine.png")
img_mine_hit = pyglet.image.load("resources/mine_hit.png")
img_mine_incorrect = pyglet.image.load("resources/mine_incorrect.png")

class Tile:
    def __init__(self, board, x, y):
        self.board = board

        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False

        self.x = x
        self.y = y

        scale_factor = window.width / (self.board.width*16)
        self.sprite = pyglet.sprite.Sprite(img_tile, self.x*16*scale_factor, self.y*16*scale_factor)
        self.sprite.scale = scale_factor
    
    @property
    def mines_around(self):
        tiles_around = self.board.get_tiles_around(self.x, self.y)

        num_mines = 0
        for tile in tiles_around:
            if tile.is_mine:
                num_mines += 1

        return num_mines

    @property
    def flags_around(self):
        tiles_around = self.board.get_tiles_around(self.x, self.y)

        num_flags = 0
        for tile in tiles_around:
            if tile.is_flagged:
                num_flags += 1

        return num_flags

    def reveal(self):
        self.is_revealed = True
        self.sprite.image = img_0
        tiles_around = self.board.get_tiles_around(self.x, self.y)

        num_mines = 0
        for tile in tiles_around:
            if tile.is_mine:
                num_mines += 1
            
        if num_mines > 0:
            self.sprite.image = numbers[num_mines]
            return

        for tile in tiles_around:    
            if not tile.is_revealed:
                tile.reveal()

    def flag(self):
        self.is_flagged = True
        self.sprite.image = img_flag

        if self.is_mine:
            self.board.num_mines -= 1

    def unflag(self):
        self.is_flagged = False
        self.sprite.image = img_tile

        if self.is_mine:
            self.board.num_mines += 1

    def reveal_mine(self):
        self.sprite.image = img_mine

    def hit_mine(self):
        self.sprite.image = img_mine_hit

    def mine_incorrect(self):
        self.sprite.image = img_mine_incorrect

    def update(self):
        self.sprite.draw()

    def __repr__(self) -> str:
        return f"Tile({self.x}, {self.y}, {self.is_mine=}, {self.is_revealed=}, {self.is_flagged=})"

    def __str__(self) -> str:
        return f"Tile({self.x}, {self.y}, {self.is_mine=}, {self.is_revealed=}, {self.is_flagged=})"

class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.starting_mines = width * height // 6

        self.board = [[Tile(self, x, y) for x in range(width)] for y in range(height)]

        self.first_click = True
        self.lost = False
        self.won = False
        self.num_mines = self.starting_mines

        # place mines
        for _ in range(self.starting_mines):
            placed_mine = False
            while not placed_mine:
                rand_x, rand_y = random.randint(0, width-1), random.randint(0, height-1)
                if not self.board[rand_x][rand_y].is_mine:
                    self.board[rand_x][rand_y].is_mine = True
                    placed_mine = True

    def get_tile_at(self, x, y):
        scale_factor = window.width / (self.width*16)
        return self.board[int(y/16/scale_factor)][int(x/16/scale_factor)]
    
    def get_tiles_around(self, x, y):
        tiles = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue

                if 0 <= x+i < self.width and 0 <= y+j < self.height:
                    tiles.append(self.board[y+j][x+i])

        return set(tiles)

    def mine_hit(self, x, y):
        for row in self.board:
            for tile in row:
                if not tile.is_mine and tile.is_flagged:
                    tile.mine_incorrect()
                if tile.is_mine:
                    tile.reveal_mine()
        self.board[y][x].hit_mine()

    def update(self, dt):
        for row in self.board:
            for tile in row:
                tile.update()

        only_mines_left = True
        for row in self.board:
            for tile in row:
                if not tile.is_revealed and not tile.is_flagged and not tile.is_mine:
                    only_mines_left = False

        if self.num_mines == 0 or only_mines_left:
            for row in self.board:
                for tile in row:
                    if not tile.is_mine and not tile.is_revealed:
                        tile.reveal()
                    if tile.is_mine and not tile.is_flagged:
                        tile.flag()

            self.won = True
            # text with outline
            pyglet.text.Label("You won!", font_size=36, x=window.width//2, y=window.height//2, anchor_x="center", anchor_y="center", color=(0, 0, 0, 255)).draw()
            pyglet.text.Label("You won!", font_size=37, x=window.width//2, y=window.height//2, anchor_x="center", anchor_y="center", color=(255, 255, 255, 255)).draw()

board = Board(16, 16)

def update(dt):
    window.clear()
    board.update(dt)

pyglet.clock.schedule(update)

@window.event
def on_mouse_press(x, y, button, modifiers):
    global board

    tile = board.get_tile_at(x, y)

    flagging = False

    if button == pyglet.window.mouse.RIGHT or (button == pyglet.window.mouse.LEFT and modifiers & pyglet.window.key.MOD_CTRL):
        flagging = True
        

    if board.lost:
        return

    tile = board.get_tile_at(x, y)
    if not flagging:
        if tile.is_flagged:
            return

        if board.first_click:
            while tile.is_mine or tile.mines_around > 0:
                board = Board(16, 16)
                tile = board.get_tile_at(x, y)
            board.first_click = False

        if tile.is_mine:
            board.mine_hit(tile.x, tile.y)
            board.lost = True
        else:
            tile.reveal()
    elif flagging:
        if not tile.is_revealed:
            if tile.is_flagged:
                tile.unflag()
            else:
                tile.flag()

class Bot:
    def __init__(self, board):
        self.board = board
        self.running = False
    
    def reveal(self, tile):
        if tile.is_mine:
            board.mine_hit(tile.x, tile.y)
            board.lost = True
        else:
            tile.reveal()

    def schedule(self, func, delay=0, *args, **kwargs):
        pyglet.clock.schedule_once(lambda x: func(*args, **kwargs), delay)

    def play(self):
        first_click = True
        self.running = True
        while first_click:
            # pick a random tile near the center of the board (not exactly the center, but close) RANDOMLY
            x, y = random.randint(board.width//2-2, board.width//2+2), random.randint(board.height//2-2, board.height//2+2)
            tile = board.board[y][x]

            if tile.is_mine or tile.mines_around > 0:
                continue
            first_click = False

        self.schedule(lambda: self.reveal(tile))

        while self.running:
            for row in self.board.board:
                for tile in row:
                    if tile.is_mine:
                        continue

                    tiles_around = board.get_tiles_around(tile.x, tile.y)
                    mines_around = tile.mines_around
                    flags_around = tile.flags_around

                    if self.board.won:
                        for row in board.board:
                            for tile in row:
                                if not tile.is_revealed and not tile.is_flagged and tile.is_mine:
                                    self.schedule(tile.flag)
                        return

                    if self.board.lost:
                        #self.restart()
                        return

                    non_revealed_tiles = 0

                    for tile in tiles_around:
                        if not tile.is_revealed and not tile.is_flagged:
                            non_revealed_tiles += 1

                    if non_revealed_tiles == mines_around-flags_around:
                        for tile in tiles_around:
                            if not tile.is_revealed and not tile.is_flagged:
                                self.schedule(tile.flag)
                    elif mines_around == flags_around:
                        for tile in tiles_around:
                            if not tile.is_revealed and not tile.is_flagged:
                                if tile.is_mine:
                                    print("Program is revealing a mine?", non_revealed_tiles, mines_around-flags_around)
                                    self.board.lost = True
                                self.schedule(tile.reveal)

                time.sleep(0.1)

    def solve(self):
        self.thread = threading.Thread(target=self.play, daemon=True)
        self.thread.start()

    def restart(self):
        global board
        self.running = False
        self.board.won = False
        self.board.lost = False
        def restart():
            global board
            board = Board(16, 16)
        self.schedule(restart, 0)
        self.board = board
        self.solve()

bot = Bot(board)

@window.event
def on_key_press(symbol, modifiers):
    global board
    if symbol == pyglet.window.key.F1:
        def restart():
            global board
            board = Board(16, 16)

            if bot.running:
                bot.solve()
        pyglet.clock.schedule_once(lambda _: restart(), 0)

    if symbol == pyglet.window.key.F2:
        if not bot.running:
            bot.solve()

pyglet.app.run()