import pygame
import random
import astar
import levels
import numpy as np
import kinematics as ai

from agent import Agent
from world import World
from pygame.locals import *  # NOQA

# Set these constants before starting the game.
FPS = 20
LEVEL = levels.EASY
MAX_PLAYER_SPEED = 30
MAX_ENEMY_SPEED = 20
MAX_ENEMYS = 5

MAX_VIEW_PLAYER = 150
MAX_VIEW_ENEMY = 100

LIFE_ENEMY = 6
LIFE_PLAYER = 10

RATE_ENEMY = 40
RATE_PLAYER = 70

DAMAGE_PLAYER = 1
DAMAGE_ENEMY = 1


GAME_STATUS = 'RUN'
# Audio TRACKS; easy to implement. Get TRACKS at:
# http://www.nosoapradio.us/
TRACKS = [
    "DST-Travel.mp3"
]


def main():
    global screen, images
    global player
    global enemys
    global tiles, world
    global points
    global draw_vectors
    global behavior
    global target
    global LEVEL

    points = 0   # NOQA
    enemys = []
    showDialog = False  # NOQA
    target = None
    # Startup code
    pygame.init()
    screen = pygame.display.set_mode((800, 700))
    pygame.display.set_caption("Majesty 0.1")
    images = loadImages()

    # The game world.
    world = World(images, LEVEL['level'])

    # Internal clock - used for computing velocities
    # We use time-based calculations rather than frame-based
    clock = pygame.time.Clock()

    player_pos = np.array(LEVEL['player'])
    player = Agent(world, 'wander', images["boy"], player_pos,
                   MAX_PLAYER_SPEED, LIFE_PLAYER, RATE_PLAYER, DAMAGE_PLAYER)

    #enemy_pos = np.array(LEVEL['enemy'])
    addEnemy()
    #enemys.append(Agent(world, 'wander', images["girl"], enemy_pos,
    #              MAX_ENEMY_SPEED, LIFE_ENEMY, RATE_ENEMY, DAMAGE_ENEMY,
    #              is_npc=True))

    # Initially, background music is playing.
    backgroundMusic()

    # Default behavior.
    behavior = 'wander'
    draw_vectors = False

    level_change = False

    # The main game event loop.
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    exit()
                elif event.key == K_m:
                    backgroundMusic()
                elif event.key == K_d:
                    draw_vectors = not draw_vectors
                    print "Toggled:", draw_vectors
                    # Magic keys to change in-game behavior.
                elif event.key == K_w:
                    behavior = 'wander'
                # Special case to close off left-most ramp
                # in hard map.
                #elif event.key == K_x:
                #    if LEVEL['level'][1][3] == 'ramp block':
                #        LEVEL['level'][1][3] = 'water block'
                #    else:
                #        LEVEL['level'][1][3] = 'ramp block'

                elif event.key == K_s:
                    behavior = 'seek'
                elif event.key == K_a:
                    behavior = 'a*'
                elif event.key == K_f:
                    behavior = 'flee'
                elif event.key == K_v:
                    behavior = 'avoid'
                elif event.key == K_r:
                    behavior = 'arrive'
                #elif event.key == K_1:
                #    LEVEL = levels.EASY
                #    level_change = True
                #elif event.key == K_2:
                #    LEVEL = levels.MEDIUM
                #    level_change = True
                #elif event.key == K_3:
                #    LEVEL = levels.HARD
                #    level_change = True
                elif event.key == K_i:
                    addEnemy()
        if GAME_STATUS == 'GAME OVER':
            print 'Game Over Man'
            break

        # If level change was indicated.
        if level_change:
            world = World(images, LEVEL['level'])

            player_pos = np.array(LEVEL['player'])
            player = Agent(world, images["boy"], player_pos, MAX_PLAYER_SPEED,
                           LIFE_PLAYER, RATE_PLAYER, DAMAGE_PLAYER)

            #enemy_pos = np.array(LEVEL['enemy'])
            addEnemy()
            #enemys.append(Agent(world, images["girl"], enemy_pos,
            #              MAX_ENEMY_SPEED, LIFE_ENEMY, RATE_ENEMY,
            #              DAMAGE_ENEMY, is_npc=True))

            level_change = False
            pass

        # Handle movement.
        #pressed_keys = pygame.key.get_pressed()

        # Compute the vector indicating the acceleration that the
        # player will experience.
        acceleration = np.array([0, 0])
        '''
        if pressed_keys[K_LEFT]:
            acceleration += [-1, 0]
        elif pressed_keys[K_RIGHT]:
            acceleration += [1, 0]

        if pressed_keys[K_UP]:
            acceleration += [0, -1]
        elif pressed_keys[K_DOWN]:
            acceleration += [0, 1]
        '''
        if not np.array_equal(acceleration, [0, 0]):
            # Using /= here breaks. NumPy issue?
            acceleration = acceleration / np.sqrt(
                np.dot(acceleration, acceleration))

        time_passed = clock.tick(FPS)
        time_passed_seconds = time_passed / 1000.0

        #player.update(acceleration, time_passed_seconds)
        manageStatus(time_passed_seconds)

        if enemys.__len__() <= 0:
            addEnemy()

        refreshBlit()
        # Intermediate buffer to screen.
        screen.blit(tiles, (0, 0))

        # Update the display, and loop again!
        pygame.display.update()


def isDead(target):
    global enemys

    if target.life <= 0:
        return True
    else:
        return False


def getDistance(target1, target2):
    distance_tuple = target1.position - target2.position
    distance_to_target = np.sqrt(np.dot(distance_tuple,
                                 distance_tuple))
    return distance_to_target


def attack(target1, target2):
    global target, points, GAME_STATUS

    atk = random.randint(0, 100)
    if target1.rate_attack < atk:
        target2.life -= target1.damage
        print 'DAMAGE'
    else:
        print 'MISS'

    if isDead(target2):
        if target2.isNonPlayerCharacter:
            target = None
            enemys.remove(target2)
            points += 1
        else:
            GAME_STATUS = 'GAME OVER'  # NOQA


## manage status for player and enemies
def manageStatus(time_passed_seconds):
    global target, tiles, behavior

    #enemys
    #for i in enemys:
    #    print i.position

    # This is where the magic happens.
    for i in enemys:
        distance = getDistance(i, player)
        if distance <= MAX_VIEW_ENEMY:
            if distance <= 10:
                i.behavior = 'attack'
                attack(i, player)
            else:
                i.behavior = 'seek'
        else:
            i.behavior = 'wander'
        executeAIBehavior(i.behavior, i, player, time_passed_seconds)

    #exec IA for player
    target = verify_target()
    if target:
        distance = getDistance(player, target)
        if distance <= 10:
            behavior = 'attack'
            attack(player, target)
        elif player.life < 3:
            behavior = 'flee'
        else:
            behavior = 'a*'
        executeAIBehavior(behavior, player, target, time_passed_seconds)
    else:
        behavior = 'wander'
        executeAIBehavior(behavior, player, player, time_passed_seconds)

    if draw_vectors is True and target:
        if behavior == 'a*':
            drawLineTile(apath.path, tiles)
        else:
            line = [(player.position[0], player.position[1]),
                    (target.position[0], target.position[1])]
            drawLinePixel(line, tiles)


def verify_target():
    global target

    if target:
        #distance_tuple is an array containing:
        #[x dist. to target, y dist. to target]
        distance_to_target = getDistance(target, player)
        if distance_to_target < MAX_VIEW_PLAYER:
            print 'IN VIEW'
            return target
        else:
            print 'NOT IN VIEW - REMOVED'
            target = None

    if not target:
        for i in enemys:
            distance_to_target = getDistance(i, player)
            if distance_to_target < MAX_VIEW_PLAYER:
                target = i
                break

    return target


def addEnemy():
    if enemys.__len__() < MAX_ENEMYS:
        enemy_pos = [random.randint(100, 650), random.randint(100, 650)]
        # np.array(LEVEL['enemy'])
        enemys.append(Agent(world, 'wander', images["girl"], enemy_pos,
                      MAX_ENEMY_SPEED, LIFE_ENEMY, RATE_ENEMY,
                      DAMAGE_ENEMY, is_npc=True))


def executeAIBehavior(behavior, enemy, player, time_passed_seconds):
    global apath  # For drawing overlays.

    if behavior == 'wander':
        ai.wander(enemy, time_passed_seconds)

    elif behavior == 'seek':
        ai.seek(enemy, player.position, time_passed_seconds)

    elif behavior == 'a*':
        apath = astar.go(enemy.position, player.position, world)
        waypoint = astar.goNext(apath, world)

        if waypoint is not None:
            ai.seek(enemy, waypoint, time_passed_seconds)

    elif behavior == 'flee':
        ai.flee(enemy, player.position, time_passed_seconds)

    elif behavior == 'avoid':
        ai.avoid(enemy, player.position, time_passed_seconds)

    elif behavior == 'arrive':
        ai.arrive(enemy, player.position, time_passed_seconds)
    elif behavior == 'stop':
        pass


def loadImages():
    images = {
        "boy": pygame.image.load("../res/Character Boy.png"),
        "girl": pygame.image.load("../res/Character Pink Girl.png"),
        "enemy": pygame.image.load("../res/Enemy Bug.png"),
        "heart": pygame.image.load("../res/Heart.png"),
        "chest closed": pygame.image.load("../res/Chest Closed.png"),
        "gem": pygame.image.load("../res/Gem Blue.png"),
        "key": pygame.image.load("../res/Gem Blue.png"),
        "dirt block": pygame.image.load("../res/Dirt Block.png"),
        "stone block": pygame.image.load("../res/Stone Block.png"),
        "plain block": pygame.image.load("../res/Plain Block.png"),
        "grass block": pygame.image.load("../res/Grass Block.png"),
        "ramp block": pygame.image.load("../res/Ramp South.png"),
        "water block": pygame.image.load("../res/Water Block.png"),
        "wall block": pygame.image.load("../res/Wall Block.png"),
        "wall block tall": pygame.image.load("../res/Wall Block Tall.png"),
        "ramp west": pygame.image.load("../res/Ramp West.png"),
        "tree short": pygame.image.load("../res/Tree Short.png"),
        "speech bubble": pygame.image.load("../res/SpeechBubble.png"),
        "stone block small": pygame.image.load("../res/Stone Block Small.png"),
    }

    # Key
    images["key"] = pygame.transform.scale(
        images["key"], (images["key"].get_width() / 2,
                        images["key"].get_height() / 2))

    # Heart
    images["heart"] = pygame.transform.scale(
        images["heart"], (images["heart"].get_width() / 2,
                          images["heart"].get_height() / 2))

    # Gem
    images["gem"] = pygame.transform.scale(
        images["gem"], (images["gem"].get_width() / 2,
                        images["gem"].get_height() / 2))

    return images


# Useful for didactic purposes.
def drawLineTile(path, tiles):
    global world

    to_draw = []

    for p in path:
        to_draw.append(world.getCenterForTile(p))

    if len(path) >= 2:
        pygame.draw.lines(tiles, (255, 0, 0), False, to_draw, 5)


def drawLinePixel(path, tiles):
    global world

    if len(path) >= 2:
        pygame.draw.lines(tiles, (255, 0, 0), False, path, 5)


def dialogBox(image, text):
    global screen, tiles, images

    print "Dialog box."

    # The mask is used to dim the screen.
    maskSurface = pygame.Surface(tiles.get_size())
    maskSurface.set_alpha(192)
    maskSurface.fill((0, 0, 0))

    tiles.blit(maskSurface, (0, 0))

    # Now display the dialog box.
    box = pygame.Surface((500, 150))
    box.fill((255, 255, 255))
    pygame.draw.rect(box, (0, 0, 0), (0, 0, 500, 10))
    # pygame.draw.rect(box, (0,0,0), (0,140,500,10))

    box.blit(image, (10, -30))

    font = pygame.font.Font("../res/Jet Set.ttf", 36)
    text = font.render(text, True, (0, 0, 0))
    box.blit(text, (150, 50))

    tiles.blit(box, (100, 200))

    screen.blit(tiles, (0, 0))

    pygame.display.update()

    while pygame.event.wait().type != KEYDOWN:
        pass

    print "Dialog acknowledged."


def backgroundMusic():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.fadeout(1000)
    else:
        pygame.mixer.music.load("../res/" + random.choice(TRACKS))
        pygame.mixer.music.play(-1)


def refreshBlit():
    global screen, enemys, player, tiles, world, points

    tiles = world.renderWorld()
    screen.fill((0, 0, 0))

    # Display level, and display behavior.
    font = pygame.font.Font("../res/Jet Set.ttf", 36)

    text = font.render(LEVEL['name'], True, (255, 255, 255))
    tiles.blit(text, (0, 0))

    text = font.render(behavior.upper(), True, (255, 255, 255))
    tiles.blit(text, (400, 0))

    text = font.render(str(points), False, (0, 0, 0))
    tiles.blit(text, (630, 600))

    text = font.render('Life: %s' % str(player.life), False, (0, 0, 0))
    tiles.blit(text, (0, 600))

    for i in enemys:
        i.blitOn(tiles)
    player.blitOn(tiles)


if __name__ == '__main__':
    main()
