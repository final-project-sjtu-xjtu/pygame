from random import randint, choice
from enum import Enum
from random import seed


class MAP_ENTRY_TYPE(Enum):
    MAP_EMPTY = 0,
    MAP_BLOCK = 1,


class WALL_DIRECTION(Enum):
    WALL_LEFT = 0,
    WALL_UP = 1,
    WALL_RIGHT = 2,
    WALL_DOWN = 3,


class MazeMapGenerator:
    def __init__(self, width: int, height: int):
        self.WIDTH = width
        self.HEIGHT = height
        self.maze_map = [[0 for _ in range(self.WIDTH)] for _ in range(self.HEIGHT)]

    def reset_maze_map(self, value):
        """将maze map全部设为墙或者路。"""
        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                self.set_maze_map(x, y, value)

    def set_maze_map(self, x, y, value):
        if value == MAP_ENTRY_TYPE.MAP_EMPTY:
            self.maze_map[y][x] = 0
        elif value == MAP_ENTRY_TYPE.MAP_BLOCK:
            self.maze_map[y][x] = 1

    def is_visited(self, x, y):
        return self.maze_map[y][x] != 1

    def show_maze_map(self):
        """墙会显示为#，通路是0，错误是X。"""
        for row in self.maze_map:
            s = ''
            for entry in row:
                if entry == 0:
                    s += ' 0'
                elif entry == 1:
                    s += ' #'
                else:
                    s += ' X'
            print(s)

    def random_prim(self, width, height):
        """random prim algorithm, with the start point within [width, height]"""
        startX, startY = (randint(0, width - 1), randint(0, height - 1))
        print("start(%d, %d)" % (startX, startY))
        self.set_maze_map(2 * startX + 1, 2 * startY + 1, MAP_ENTRY_TYPE.MAP_EMPTY)
        checklist = [(startX, startY)]

        def check_adjacent_pos(x, y):
            """HELPER FUNC: find unvisited adjacent entries of four possible entris
            then add random one of them to checklist and mark it as visited"""
            directions = []
            if x > 0:
                if not self.is_visited(2 * (x - 1) + 1, 2 * y + 1):
                    directions.append(WALL_DIRECTION.WALL_LEFT)

            if y > 0:
                if not self.is_visited(2 * x + 1, 2 * (y - 1) + 1):
                    directions.append(WALL_DIRECTION.WALL_UP)

            if x < width - 1:
                if not self.is_visited(2 * (x + 1) + 1, 2 * y + 1):
                    directions.append(WALL_DIRECTION.WALL_RIGHT)

            if y < height - 1:
                if not self.is_visited(2 * x + 1, 2 * (y + 1) + 1):
                    directions.append(WALL_DIRECTION.WALL_DOWN)

            if len(directions):
                direction = choice(directions)
                # print("(%d, %d) => %s" % (x, y, str(direction)))
                if direction == WALL_DIRECTION.WALL_LEFT:
                    self.set_maze_map(2 * (x - 1) + 1, 2 * y + 1, MAP_ENTRY_TYPE.MAP_EMPTY)
                    self.set_maze_map(2 * x, 2 * y + 1, MAP_ENTRY_TYPE.MAP_EMPTY)
                    checklist.append((x - 1, y))
                elif direction == WALL_DIRECTION.WALL_UP:
                    self.set_maze_map(2 * x + 1, 2 * (y - 1) + 1, MAP_ENTRY_TYPE.MAP_EMPTY)
                    self.set_maze_map(2 * x + 1, 2 * y, MAP_ENTRY_TYPE.MAP_EMPTY)
                    checklist.append((x, y - 1))
                elif direction == WALL_DIRECTION.WALL_RIGHT:
                    self.set_maze_map(2 * (x + 1) + 1, 2 * y + 1, MAP_ENTRY_TYPE.MAP_EMPTY)
                    self.set_maze_map(2 * x + 2, 2 * y + 1, MAP_ENTRY_TYPE.MAP_EMPTY)
                    checklist.append((x + 1, y))
                elif direction == WALL_DIRECTION.WALL_DOWN:
                    self.set_maze_map(2 * x + 1, 2 * (y + 1) + 1, MAP_ENTRY_TYPE.MAP_EMPTY)
                    self.set_maze_map(2 * x + 1, 2 * y + 2, MAP_ENTRY_TYPE.MAP_EMPTY)
                    checklist.append((x, y + 1))
                return True
            else:
                # if not find any unvisited adjacent entry
                return False

        while len(checklist):
            # select a random entry from checklist
            entry = choice(checklist)
            if not check_adjacent_pos(entry[0], entry[1]):
                # the entry has no unvisited adjacent entry, so remove it from checklist
                checklist.remove(entry)
        return startX, startY

    def do_random_prim(self):
        """对random_prim的二次封装，可以指定生成的初识点所在的区域"""
        self.reset_maze_map(MAP_ENTRY_TYPE.MAP_BLOCK)  # 把maze map全部设为墙
        startX, startY = self.random_prim((self.WIDTH - 1) // 2, (self.HEIGHT - 1) // 2)  # 初始生成点一定在左上半边。
        return startX, startY



def get_a_maze_map(width: int = 55, height: int = 43):
    maze_map_con = MazeMapGenerator(width, height)
    startX, startY = maze_map_con.do_random_prim()
    maze_map_con.show_maze_map()
    # print(map.map[2][3])
    return maze_map_con.maze_map


if __name__ == "__main__":
    get_a_maze_map()
