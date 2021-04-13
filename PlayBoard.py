import pygame as pg
import sys, os
from pygame.compat import geterror
import math
import maze_map_generator
from maze_map_generator import MazeMapGenerator
from pygame.locals import *
from random import seed

seed(0)

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

    def move(self, speed):
        self.rect = self.rect.move(speed)

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
    def __init__(self):
        self.CUBE_WIDTH = 100  # 每个方块大小
        self.CUBE_HEIGHT = 100
        self.WIDTH = 10
        self.HEIGHT = 10
        self.absolute_speed = 10
        self.speed = [0, 0]
        self.block_group = []
        self.speed = [0, 0]
        # self.play()

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

    def play(self):
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
        wallsprites = pg.sprite.Group()
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
                    wallsprites.add(wall)
                elif maze_map[j][i] == 0:
                    if cnt == 0:  # 左上的第一个非墙标记为起点
                        begin_x = i
                        begin_y = j
                    cnt = cnt + 1
                    end_x = i  # 右下的最后一个标记为终点
                    end_y = j
        player = Player(begin_x, begin_y, self.CUBE_WIDTH, self.CUBE_HEIGHT)
        endpoint = EndPoint(end_x, end_y, self.CUBE_WIDTH, self.CUBE_HEIGHT)
        print("the start point is:", "(", begin_x, ",", begin_y, ")")
        print("the start point is:", "(", end_x, ",", end_y, ")")

        # Main Loop
        going = True
        while going:
            self.watch_keyboard()
            clock.tick(20)
            # check end

            if pg.sprite.spritecollideany(player, wallsprites):
                print("Got a collision")
                break
            elif player.compute_dis(endpoint.rect.centerx, endpoint.rect.centery) < 5:
                print("Successfully reached the end")
                break

            # Handle Input Events
            #
            # for event in pg.event.get():
            #     if event.type in (pg.QUIT, pg.KEYDOWN):
            #         sys.exit()

            wallsprites.update()

            # Draw Everything
            screen.blit(background, (0, 0))
            wallsprites.draw(screen)
            screen.blit(player.image, player.rect)
            screen.blit(endpoint.image, endpoint.rect)
            pg.display.update()
            pg.display.flip()
            # self.get_speed()
            print(self.speed)
            player.move(self.speed)


if __name__ == '__main__':
    p = PlayBoard()
    p.play()

