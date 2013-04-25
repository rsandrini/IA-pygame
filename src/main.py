import pygame
import random
import astar
import levels
import numpy as np
import kinematics as ai

from agent import Agent
from world import World
from pygame.locals import *  # NOQA
from menu import *  # NOQA


# Set these constants before starting the game.
FPS = 20
LEVEL = levels.EASY
MAX_PLAYER_SPEED = 30
MAX_ENEMY_SPEED = 20
MAX_ENEMYS = 5

MAX_VIEW_PLAYER = 180
MAX_VIEW_ENEMY = 100

LIFE_ENEMY = 4
LIFE_PLAYER = 10

RATE_ENEMY = 40
RATE_PLAYER = 70

DAMAGE_PLAYER = 1
DAMAGE_ENEMY = 1

TIME_NEXT_ATTACK = 1
TIME_NEXT_ATTACK_PLAYER = 0.8

GAME_STATE = 'menu'
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
    global action
    global world
    global points
    global apath

    showDialog = False  # NOQA
    # Startup code
    pygame.init()
    screen = pygame.display.set_mode((800, 700))
    pygame.display.set_caption("Majesty 0.1")
    images = loadImages()
    pygame.time.set_timer(USEREVENT + 1, 2000)

    level_change = False  # NOQA

    # The main game event loop.
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    exit()

        screenGame(GAME_STATE)


def loading():
    global clock, player, behavior, action, world
    global draw_vectors, level_change
    global enemys, target, points

    points = 0   # NOQA
    enemys = []
    target = None
    # Default behavior.
    behavior = 'stop'
    action = 'run'
    draw_vectors = True

    # The game world.
    world = World(images, LEVEL['level'])

    # Internal clock - used for computing velocities
    # We use time-based calculations rather than frame-based
    clock = pygame.time.Clock()

    player_pos = np.array(LEVEL['player'])
    player = Agent(world, 'wander', images["boy"], player_pos,
                   MAX_PLAYER_SPEED, LIFE_PLAYER, RATE_PLAYER, DAMAGE_PLAYER)

    addEnemy()

    # Initially, background music is playing.
    backgroundMusic()


def gameRun():
    global clock, player, action, world, points, tiles, enemys
    global level_change, draw_vectors, target, apath, behavior
    global MAX_VIEW_PLAYER, MAX_VIEW_ENEMY, screen

    # The main game event loop.
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            if event.type == USEREVENT + 1:
                restoreLifePlayer()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    exit()
                elif event.key == K_m:
                    backgroundMusic()
                elif event.key == K_d:
                    draw_vectors = not draw_vectors
                elif event.key == K_i:
                    addEnemy()
        # Compute the vector indicating the acceleration that the
        # player will experience.
        acceleration = np.array([0, 0])
        if not np.array_equal(acceleration, [0, 0]):
            # Using /= here breaks. NumPy issue?
            acceleration = acceleration / np.sqrt(
                np.dot(acceleration, acceleration))

        time_passed = clock.tick(FPS)
        time_passed_seconds = time_passed / 1000.0

        #player.update(acceleration, time_passed_seconds)
        manageStatus(time_passed_seconds)

        refreshBlit()

        if enemys.__len__() <= 0:
            addEnemy()

        if draw_vectors and target:
            if behavior == 'a*':
                drawLineTile(apath.path, tiles)
            else:
                line = [(player.position[0], player.position[1]),
                        (target.position[0], target.position[1])]
                drawLinePixel(line, tiles)

        # Intermediate buffer to screen.
        screen.blit(tiles, (0, 0))

        if draw_vectors:
            #Draw vision circle in player
            r = int(MAX_VIEW_PLAYER)
            pos = (int(player.position[0]), int(player.position[1]))
            cor = (255, 255, 255)
            pygame.draw.circle(screen, cor, pos, r, 1)

            #Draw vision circle in enemys
            p = int(MAX_VIEW_ENEMY)
            for i in enemys:
                pygame.draw.circle(screen, cor, (int(i.position[0]),
                                                 int(i.position[1])), p, 1)

        # Update the display, and loop again!
        pygame.display.update()

        if GAME_STATE == 'gameover':
            print "You final points: %s" % points
            break  # Break the gameLooping


def restoreLifePlayer():
    global behavior, player, action
    if behavior == 'stop' and action == 'stop' and player.life < LIFE_PLAYER:
        player.life += 1
        print 'Restore Life'


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


def attack(target1, target2, time_passed_seconds):
    '''
        the target1 try attack target2 using percent rate_attack
        in last_attack time (1 second) and verify if target's is dead
    '''
    global target, points, GAME_STATE
    target1.next_attack -= time_passed_seconds
    damage = False

    if target1.next_attack <= 0:
        atk = random.randint(0, 100)
        if target1.rate_attack > atk:
            target2.life -= target1.damage
            damage = True
        if target1.isNonPlayerCharacter:
            target1.next_attack = TIME_NEXT_ATTACK
        else:
            # is a Player
            target1.next_attack = TIME_NEXT_ATTACK_PLAYER

        if target1.isNonPlayerCharacter:
            if damage:
                print 'NPC cause damage in player'
            else:
                print 'NPC miss'
        else:
            if damage:
                print 'Player cause damage in NPC'
            else:
                print 'Player miss'

    if isDead(target2):
        if target2.isNonPlayerCharacter:
            target = None
            enemys.remove(target2)
            points += 1
            print 'Enemy elimined'
        else:
            GAME_STATE = 'gameover'  # NOQA


## manage status for player and enemies
def manageStatus(time_passed_seconds):
    global target, tiles, behavior, world, action

    #enemys
    # This is where the magic happens.
    for i in enemys:
        distance = getDistance(i, player)
        if distance <= MAX_VIEW_ENEMY:
            if distance <= 25:
                i.behavior = 'attack'
                attack(i, player, time_passed_seconds)
            else:
                i.behavior = 'seek'
        else:
            i.behavior = 'wander'
        executeAIBehavior(i.behavior, i, player, time_passed_seconds)

    #exec IA for player
    target = verify_target()
    if target:
        distance = getDistance(player, target)
        if player.life < 4:
            action = 'flee'
            if not player.can_move:
                action = 'run'
        elif distance <= 30:
            action = 'attack'
        else:
            action = 'hunter'
    else:
        action = 'stop'
        # Not target
        if player.life > 9:
            action = 'run'

    execAction(time_passed_seconds)


def execAction(time_passed_seconds):
    global action, target, behavior
    targetBeh = player

    if action == 'hunter':
        ''' run to target '''
        behavior = 'a*'
        targetBeh = target

    elif action == 'attack':
        attack(player, target, time_passed_seconds)
        behavior = 'stop'

    elif action == 'stop':
        behavior = 'stop'

    elif action == 'run':
        behavior = 'wander'

    elif action == 'flee':
        behavior = 'flee'
        targetBeh = target

    executeAIBehavior(behavior, player, targetBeh, time_passed_seconds)


def verify_target():
    global target

    if target:
        #distance_tuple is an array containing:
        #[x dist. to target, y dist. to target]
        distance_to_target = getDistance(target, player)
        if distance_to_target < MAX_VIEW_PLAYER:
            return target
        else:
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
        pos_level = np.array(LEVEL['enemy']).__len__()
        try:
            position = LEVEL['enemy'][random.randint(0, pos_level)]
            enemy_pos = np.array(position)
        except IndexError:
            enemy_pos = np.array(LEVEL['enemy'][0])

        enemys.append(Agent(world, 'wander', images["girl"], enemy_pos,
                      MAX_ENEMY_SPEED, LIFE_ENEMY, RATE_ENEMY,
                      DAMAGE_ENEMY, is_npc=True))


def executeAIBehavior(behavior, enemy, player, time_passed_seconds):
    global apath, world  # For drawing overlays.

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
    global screen, enemys, player, tiles, world, points, action

    tiles = world.renderWorld()
    screen.fill((0, 0, 0))

    # Display level, and display behavior.
    font = pygame.font.Font("../res/Jet Set.ttf", 36)

    text = font.render(LEVEL['name'], True, (255, 255, 255))
    tiles.blit(text, (0, 0))

    text = font.render(action.upper(), True, (255, 255, 255))
    tiles.blit(text, (400, 0))

    text = font.render(str(points), False, (0, 0, 0))
    tiles.blit(text, (630, 600))

    text = font.render('Life: %s' % str(player.life), False, (0, 0, 0))
    tiles.blit(text, (0, 600))

    for i in enemys:
        i.blitOn(tiles)
    player.blitOn(tiles)


def aboutScreen():
    global GAME_STATE
    print 'About screen not implemented'
    GAME_STATE = 'menu'


def gameOverScreen():
    global points, GAME_STATE

    background = pygame.image.load("../res/go.jpg")
    backgroundRect = background.get_rect()

    # Display level, and display behavior.
    font = pygame.font.Font("../res/Jet Set.ttf", 36)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
        key_press = pygame.key.get_pressed()
        if key_press[K_SPACE]:
            GAME_STATE = 'menu'
            break
        pygame.event.pump()
        screen.fill((0, 0, 0))
        screen.blit(background, backgroundRect)

        text = font.render('You has made %s points' % points,
                           True, (100, 100, 100))
        screen.blit(text, (200, 10))

        text = font.render('Press SPACE for continue', True, (100, 100, 100))
        screen.blit(text, (130, 630))

        pygame.display.update()


def menuScreen():
    global GAME_STATE

    background = pygame.image.load("../res/bc.jpg")
    backgroundRect = background.get_rect()
    #font = pygame.font.Font("../res/Jet Set.ttf", 36)

    options = [Option("New Game", (340, 110), 'gameRun', screen),
               Option("About", (340, 190), 'about', screen),
               Option("Quit", (340, 280), 'quit', screen)]

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
        pygame.event.pump()
        screen.fill((0, 0, 0))
        screen.blit(background, backgroundRect)

        for option in options:
            if option.rect.collidepoint(pygame.mouse.get_pos()):
                option.hovered = True

                if pygame.mouse.get_pressed() == (1, 0, 0):
                    option.clicked = True
                else:
                    option.clicked = False
            else:
                option.hovered = False
                option.clicked = False
            option.draw()
            if option.clicked:
                GAME_STATE = option.new_window()
        pygame.display.update()
        if not GAME_STATE is 'menu':
            break


def screenGame(GAME_STATE):
    if GAME_STATE == 'menu':
        menuScreen()
    elif GAME_STATE == 'gameRun':
        loading()
        gameRun()
    elif GAME_STATE == 'about':
        aboutScreen()
    elif GAME_STATE == 'gameover':
        gameOverScreen()
    elif GAME_STATE == 'quit':
        pygame.quit()
        exit()


if __name__ == '__main__':
    main()
