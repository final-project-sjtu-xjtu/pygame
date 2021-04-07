import pygame as pg
import sys, os
from pygame.compat import geterror
import math
import maze_generator

BLACK = 0, 0, 0
WHITE = 255, 255, 255
RED = 255, 0, 0
width = height = 30
block_group = []
speed = [2, 0]


def get_speed():
    '''

    :return:
    '''


# functions to create our resources
def load_image(name, colorkey=None):
    try:
        image = pg.image.load(name)
    except pg.error:
        print("Cannot load image: player.jpg")
        raise SystemExit(str(geterror()))
    image = image.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pg.RLEACCEL)
    return image, image.get_rect()


class Player(pg.sprite.Sprite):

    def __init__(self, begin_x, begin_y):
        pg.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.image = pg.image.load("Player.png")
        # self.image, self.rect = load_image("Player.png")
        self.rect = self.image.get_rect().move(begin_x * width + width/2 - 7, begin_y * height + height/2 - 6)

    def move(self, speed):
        self.rect = self.rect.move(speed)

    def compute_dis(self,end_x, end_y):
        dis_x = abs(self.rect.centerx - end_x)
        dis_y = abs(self.rect.centery - end_y)
        return math.sqrt((dis_x**2)+(dis_y**2))


class WallUnit(pg.sprite.Sprite):

    def __init__(self, wall_x, wall_y):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface([width, height])
        self.image.fill(BLACK)
        self.rect = self.image.get_rect().move(wall_x * width, wall_y * height)


class EndPoint(pg.sprite.Sprite):

    def __init__(self, end_x, end_y):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface([width, height])
        self.image.fill(RED)
        self.rect = self.image.get_rect().move(end_x * width, end_y * height)

def play():
    """this function is called when the program starts.
       it initializes everything it needs, then runs in
       a loop until the function returns."""
    # Initialize Everything
    pg.init()
    screen = pg.display.set_mode((930, 630))

    # Get the maze
    background_group = maze_generator.run()

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
    # print(type(background_group))
    cnt = 0
    for i in range(len(background_group[0])):
        for j in range(len(background_group)):
            if background_group[j][i] == 1:
                wall = WallUnit(i, j)
                block_group.append(wall)
                wallsprites.add(wall)
            elif background_group[j][i] == 0:
                if cnt == 0:
                    beginpos_x = i
                    beginpos_y = j
                cnt = cnt + 1
                end_x = i
                end_y = j
    player = Player(beginpos_x, beginpos_y)
    endpoint = EndPoint(end_x, end_y)
    print("the start point is:", "(", beginpos_x, ",", beginpos_y, ")")
    print("the start point is:", "(", end_x, ",", end_y, ")")


    # Main Loop
    going = True
    while going:
        clock.tick(60)
        # check end

        if pg.sprite.spritecollideany(player, wallsprites):
            print("Got a collision")
            break
        elif player.compute_dis(endpoint.rect.centerx,endpoint.rect.centery) < 5:
            print("Successfully reached the end")
            break

        # Handle Input Events

        for event in pg.event.get():
            if event.type in (pg.QUIT, pg.KEYDOWN):
                sys.exit()

        wallsprites.update()

        # Draw Everything
        screen.blit(background, (0, 0))
        wallsprites.draw(screen)
        screen.blit(player.image, player.rect)
        screen.blit(endpoint.image, endpoint.rect)
        pg.display.update()
        pg.display.flip()
        get_speed()
        player.move(speed)


    pg.quit()


# Game Over
if __name__ == "__main__":
    play()