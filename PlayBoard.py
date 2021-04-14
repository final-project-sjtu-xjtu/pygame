import pygame as pg
import sys, os
from pygame.compat import geterror
import math
import maze_map_generator
from maze_map_generator import MazeMapGenerator
from pygame.locals import *
import random
from typing import Tuple
import time
from RRT.RRT import RRT

BLACK = 0, 0, 0
WHITE = 255, 255, 255
RED = 255, 0, 0


# functions to create our resources
def load_image(name, colorkey=None):
    image = pg.image.load(name)
    image = image.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pg.RLEACCEL)
    return image, image.get_rect()


class Player(pg.sprite.Sprite):
    def __init__(self, begin_x, begin_y, width, height):
        pg.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.image = pg.image.load("Player.png")
        # self.image, self.rect = load_image("Player.png")
        self.rect = self.image.get_rect().move(begin_x * width + width / 2 - 7, begin_y * height + height / 2 - 6)

    def coord(self):
        return self.rect.centerx, self.rect.centery

    def move(self, speed):
        self.rect = self.rect.move(speed)

    def flash_at_specified_position(self, x2, y2):
        x1, y1 = self.coord()
        self.rect = self.rect.move((x2-x1, y2-y1))

    def compute_dis(self, end_x, end_y):
        dis_x = abs(self.rect.centerx - end_x)
        dis_y = abs(self.rect.centery - end_y)
        return math.sqrt((dis_x ** 2) + (dis_y ** 2))


class WallUnit(pg.sprite.Sprite):
    def __init__(self, wall_x, wall_y, width, height):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface([width, height])
        self.image.fill(BLACK)
        self.rect = self.image.get_rect().move(wall_x * width, wall_y * height)


class EndPoint(pg.sprite.Sprite):
    def __init__(self, end_x, end_y, width, height):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface([width, height])
        self.image.fill(RED)
        self.rect = self.image.get_rect().move(end_x * width, end_y * height)


class PlayBoard:
    def __init__(self, seed: int = 1):
        random.seed(seed)
        self.CUBE_WIDTH = 100  # 每个方块大小
        self.CUBE_HEIGHT = 100
        self.WIDTH = 10  # 有几个方块
        self.HEIGHT = 10
        self.WHOLE_WIDTH = self.CUBE_WIDTH * self.WIDTH
        self.WHOLE_HEIGHT = self.CUBE_HEIGHT * self.HEIGHT
        self.absolute_speed = 10
        self.speed = [0, 0]
        self.block_group = []
        self.speed = [0, 0]
        self.player = Player(0, 0, self.CUBE_WIDTH, self.CUBE_HEIGHT)
        self.wallsprites = pg.sprite.Group()

        # Get the maze map
        self.maze_map = maze_map_generator.get_a_maze_map(self.WIDTH, self.HEIGHT)
        end_x = end_y = 0
        begin_x = begin_y = 0
        # print(type(background_group))
        cnt = 0
        for i in range(len(self.maze_map[0])):
            for j in range(len(self.maze_map)):
                if self.maze_map[j][i] == 1:
                    wall = WallUnit(i, j, self.CUBE_WIDTH, self.CUBE_HEIGHT)
                    self.block_group.append(wall)
                    self.wallsprites.add(wall)
                elif self.maze_map[j][i] == 0:
                    if cnt == 0:  # 左上的第一个非墙标记为起点
                        begin_x = i
                        begin_y = j
                    cnt = cnt + 1
                    end_x = i  # 右下的最后一个标记为终点
                    end_y = j
        self.player = Player(begin_x, begin_y, self.CUBE_WIDTH, self.CUBE_HEIGHT)
        self.endpoint = EndPoint(end_x, end_y, self.CUBE_WIDTH, self.CUBE_HEIGHT)
        print("the start point is:", "(", self.player.rect.centerx, ",", self.player.rect.centery, ")")
        print("the start point is:", "(", self.endpoint.rect.centerx, ",", self.endpoint.rect.centery, ")")
        pg.init()
        self.screen = pg.display.set_mode((1000, 1000))  # 屏幕大小
        self.background = pg.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((250, 250, 250))
        self.screen.blit(self.background, (0, 0))
        self.wallsprites.update()
        self.wallsprites.draw(self.screen)
        self.screen.blit(self.player.image, self.player.rect)
        self.screen.blit(self.endpoint.image, self.endpoint.rect)
        pg.display.flip()
        self.pg_clock = pg.time.Clock()

        self.rrt = RRT(boundary=(0, 0, self.WHOLE_WIDTH, self.WHOLE_HEIGHT),
                       goal=(self.endpoint.rect.centerx, self.endpoint.rect.centery),
                       start_point=(self.player.rect.centerx, self.player.rect.centery),
                       seed=seed)

    def watch_keyboard(self):
        self.speed = [0, 0]
        events = pg.event.get()
        print("events", events)
        for event in events:
            if event.type == KEYDOWN:
                if event.key in (K_q, ):
                    exit(0)
                if event.key == K_w:
                    self.speed = [0, -1 * self.absolute_speed]
                elif event.key == K_s:
                    self.speed = [0, 1 * self.absolute_speed]
                elif event.key == K_a:
                    self.speed = [-1 * self.absolute_speed, 0]
                elif event.key == K_d:
                    self.speed = [1 * self.absolute_speed, 0]

    @staticmethod
    def compute_trace(x1, y1, x2, y2):
        trace = []
        k = (y2 - y1) / (x2 - x1)
        if abs(k) < 1:  # 使用x轴为index
            if x2 > x1:
                for x in range(x1 + 1, x2):
                    y_float = k * (x - x1) + y1
                    y_int = round(y_float)
                    trace.append((x, y_int))
            else:
                for x in range(x1 - 1, x2, -1):
                    y_float = k * (x - x1) + y1
                    y_int = round(y_float)
                    trace.append((x, y_int))
        else:  # 使用y轴为index
            if y2 > y1:
                for y in range(y1 + 1, y2):
                    x_float = 1 / k * (y - y1) + x1
                    x_int = round(x_float)
                    trace.append((x_int, y))
            else:
                for y in range(y1 - 1, y2, -1):
                    x_float = 1 / k * (y - y1) + x1
                    x_int = round(x_float)
                    trace.append((x_int, y))
        trace.append((x2, y2))
        return trace

    def move_player_2_specific_position(self, x2, y2, draw_trace=True) -> bool:
        """将车从目前位置，按照最接近直线的方式移动到[x2, y2]，移动成功返回True，否则返回False
        如果draw trace 是 True，会将移动的轨迹绘制出，并暂停一秒给你看看。
        后续的一个优化方向可以是把希望移动的函数传入，in the future."""
        x1, y1 = self.player.coord()
        trace = self.compute_trace(x1, y1, x2, y2)

        last_coord = (x1, y1)
        result = True
        for coord in trace:
            self.player.rect = self.player.rect.move((coord[0]-last_coord[0], coord[1] - last_coord[1]))
            if pg.sprite.spritecollideany(self.player, self.wallsprites):
                result = False
            if draw_trace:
                self.screen.blit(self.player.image, self.player.rect)
                pg.display.update(self.player.rect)
            last_coord = coord
        if draw_trace:
            time.sleep(1)  # 暂停一秒给你看看trace。
        return result

    def collision_detect(self, x1, y1, x2, y2) -> bool:
        """Move the car from (x1, y1) to (x2, y2), find out if there are any collisions"""
        if x1 == x2 and y1 == y2:
            return False
        self.player.flash_at_specified_position(x1, y1)
        result = self.move_player_2_specific_position(x2, y2)
        return not result

    def algo(self) -> Tuple[int, int, int, int, RRT.Node]:
        """返回车要去的点"""
        x1, y1, x2, y2, nearest_node = self.rrt.get_a_point()
        return x1, y1, x2, y2, nearest_node

    def play(self):
        """正式使用的函数"""
        going = True
        while going:
            self.pg_clock.tick(2)  # 每秒钟最多多少帧
            if self.player.compute_dis(self.endpoint.rect.centerx, self.endpoint.rect.centery) < 5:
                print("Successfully reached the end")
                break


            # pg.display.update()  # only update specified contents; but update the entire display passing no arguments.
            pg.display.flip()  # update the contents of the entire display
            # self.get_speed()
            # self.player.flash_at_specified_position(*[int(i) for i in input("with format [x,y]").split(',')])
            # self.flash_player_at_position(*[int(i) for i in input("with format [x,y]").split(',')])
            x1, y1, x2, y2, nearest_node = self.algo()
            collide = self.collision_detect(x1, y1, x2, y2)
            self.rrt.update(x2, y2, nearest_node, collide)

    def play_4_fun(self):
        """仅仅拿来测试，正式不使用。"""
        pg.init()
        screen = pg.display.set_mode((1000, 1000))

        # Get the maze map
        maze_map = maze_map_generator.get_a_maze_map(self.WIDTH, self.HEIGHT)

        # Create The Background
        background = pg.Surface(screen.get_size())
        background = background.convert()
        background.fill((250, 250, 250))

        # Display The Background
        screen.blit(background, (0, 0))
        pg.display.flip()
        # Prepare Game Objects
        clock = pg.time.Clock()
        end_x = end_y = 0
        begin_x = begin_y = 0
        # print(type(background_group))
        cnt = 0
        for i in range(len(maze_map[0])):
            for j in range(len(maze_map)):
                if maze_map[j][i] == 1:
                    wall = WallUnit(i, j, self.CUBE_WIDTH, self.CUBE_HEIGHT)
                    self.block_group.append(wall)
                    self.wallsprites.add(wall)
                elif maze_map[j][i] == 0:
                    if cnt == 0:  # 左上的第一个非墙标记为起点
                        begin_x = i
                        begin_y = j
                    cnt = cnt + 1
                    end_x = i  # 右下的最后一个标记为终点
                    end_y = j
        self.player = Player(begin_x, begin_y, self.CUBE_WIDTH, self.CUBE_HEIGHT)
        endpoint = EndPoint(end_x, end_y, self.CUBE_WIDTH, self.CUBE_HEIGHT)
        print("the start point is:", "(", begin_x, ",", begin_y, ")")
        print("the start point is:", "(", end_x, ",", end_y, ")")

        # Main Loop
        going = True
        while going:
            self.watch_keyboard()
            clock.tick(20)  # 每秒钟最多多少帧
            # check end

            if pg.sprite.spritecollideany(self.player, self.wallsprites):
                print("Got a collision")
                break
            elif self.player.compute_dis(endpoint.rect.centerx, endpoint.rect.centery) < 5:
                print("Successfully reached the end")
                break

            # Handle Input Events
            #
            # for event in pg.event.get():
            #     if event.type in (pg.QUIT, pg.KEYDOWN):
            #         sys.exit()

            self.wallsprites.update()

            # Draw Everything
            screen.blit(background, (0, 0))
            self.wallsprites.draw(screen)
            screen.blit(self.player.image, self.player.rect)
            screen.blit(endpoint.image, endpoint.rect)
            pg.display.update()
            pg.display.flip()
            # self.get_speed()
            print(self.speed)
            self.player.move(self.speed)


if __name__ == '__main__':
    p = PlayBoard()
    p.play()
