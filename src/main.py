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
from upgrade import Upgrade

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
RATE_PLAYER = 80

DAMAGE_PLAYER = 1
DAMAGE_ENEMY = 1

TIME_NEXT_ATTACK = 1
TIME_NEXT_ATTACK_PLAYER = 0.8

GAME_STATE = 'menu'
# Audio TRACKS; easy to implement. Get TRACKS at:
# http://www.nosoapradio.us/
TRACKS = [
    "Human_Blood.mp3"
]


def main():
    global screen, images
    global player
    global enemys
    global tiles, world
    global points
    global draw_vectors, draw_lifebar
    global behavior
    global target
    global LEVEL
    global action
    global world
    global points
    global apath
    global btnUpgrades
    global attempts_flee
    global score
    global min_enemys

    showDialog = False  # NOQA
    # Startup code

    # setup mixer to avoid sound lag
    pygame.mixer.pre_init(44100, -16, 2, 2048)

    pygame.init()
    screen = pygame.display.set_mode((800, 700))
    pygame.display.set_caption("Zombie Zone 0.1")

    images = loadImages()
    pygame.time.set_timer(pygame.USEREVENT + 1, 2000)

    level_change = False  # NOQA
    draw_lifebar = True

    # The main game event loop.
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    exit()

        screenGame(GAME_STATE)


def loading():
    global clock, player, behavior, action, world, min_enemys
    global draw_vectors, level_change, screen, score
    global enemys, target, points, btnUpgrades, attemps_flee
    global MAX_VIEW_PLAYER, LIFE_PLAYER, RATE_PLAYER
    global MAX_VIEW_ENEMY, LIFE_ENEMY, RATE_ENEMY
    MAX_VIEW_PLAYER = 180
    MAX_VIEW_ENEMY = 100

    LIFE_ENEMY = 4
    LIFE_PLAYER = 10

    RATE_ENEMY = 40
    RATE_PLAYER = 80
    score = 0
    points = 0   # NOQA
    enemys = []
    target = None
    # Default behavior.
    behavior = 'stop'
    action = 'run'
    draw_vectors = False
    btnUpgrades = []
    cost_up = 3
    attempts_flee = 0  # NOQA
    min_enemys = LEVEL['min_enemys']

    #Loading Upgrades
    btnUpgrades.append(Upgrade('Damage', images['icon damage'],
                               images['icon damage disabled'],
                               (715, 160), 'damage', 2, cost_up))
    btnUpgrades.append(Upgrade('Life', images['icon life'],
                               images['icon life disabled'],
                               (715, 300), 'life', 2, cost_up))
    btnUpgrades.append(Upgrade('Vision', images['icon vision'],
                               images['icon vision disabled'],
                               (715, 440), 'vision', 50, cost_up))

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
            if event.type == pygame.QUIT:
                exit()
            if event.type == USEREVENT + 1:
                restoreLifePlayer()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    exit()
                elif event.key == pygame.K_m:
                    backgroundMusic()
                elif event.key == pygame.K_d:
                    draw_vectors = not draw_vectors
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

        # manage the number of enemys
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
        # EXTRA DRAW AFTER FUNCTION

        if draw_lifebar:
            drawLifeBar(screen, int(player.position[0])-25,
                        int(player.position[1])-100, LIFE_PLAYER, player.life)

        if draw_vectors:
            #Draw vision circle in player
            r = int(MAX_VIEW_PLAYER)
            pos = (int(player.position[0]), int(player.position[1]))
            cor = (255, 255, 255)
            pygame.draw.circle(screen, cor, pos, r, 1)

            #Draw vision circle in enemys
            p = int(MAX_VIEW_ENEMY)
            for i in enemys:
                pos = (int(i.position[0]), int(i.position[1]))
                pygame.draw.circle(screen, cor, pos, p, 1)

        if draw_lifebar:
            for i in enemys:
                pos = (int(i.position[0]), int(i.position[1]))
                #adjust position in head of agent
                drawLifeBar(screen, pos[0]-25, pos[1]-100, LIFE_ENEMY, i.life)

        #Draw icons and logic for upgrades
        drawUpgrades(screen)

        # Update the display, and loop again!
        pygame.display.update()

        if GAME_STATE == 'gameover':
            break  # Break the gameLooping


def drawUpgrades(screen):
    global points
    # Display level, and display behavior.
    font = pygame.font.Font("../res/Jet Set.ttf", 12)

    for i in btnUpgrades:
        if points >= i.cost:
            icon = i.icon
        else:
            icon = i.icon_disabled
        screen.blit(icon, i.position)
        text = font.render('%s[%s] :%s' % (i.name, i.upgrade_level, i.cost),
                           True, (255, 255, 255))
        screen.blit(text, (i.position[0], i.position[1]+80))
        if i.rect.collidepoint(pygame.mouse.get_pos()):
            i.hovered = True
            if pygame.mouse.get_pressed() == (1, 0, 0):
                if points >= i.cost:
                    print('Added upgrade')
                    addUpgrade(i)
                    i.up()
        else:
            i.hovered = False


def addUpgrade(upgrade):
    global DAMAGE_PLAYER, LIFE_PLAYER, MAX_VIEW_PLAYER
    global points, player
    points -= upgrade.cost
    if upgrade.type_upgrade == 'damage':
        player.damage += upgrade.bonus
    elif upgrade.type_upgrade == 'life':
        LIFE_PLAYER += upgrade.bonus
    elif upgrade.type_upgrade == 'vision':
        MAX_VIEW_PLAYER += upgrade.bonus


def drawLifeBar(screen, x, y, life_full, life):
    try:
        cor = (128, 128, 128)
        cor100 = (0, 179, 21)
        cor75 = (171, 244, 67)
        cor50 = (241, 223, 18)
        cor25 = (241, 39, 18)

        # draw border in life bar
        pygame.draw.rect(screen, cor, pygame.Rect(
            x, y, 61, 12), 1)

        life_bar_perc = life*100/life_full
        life_bar = life_bar_perc*60/100
        if life_bar_perc > 75:
            cor2 = cor100
        elif life_bar_perc > 50:
            cor2 = cor75
        elif life_bar_perc > 25:
            cor2 = cor50
        else:
            cor2 = cor25

        # draw real life bar
        pygame.draw.rect(screen, cor2, pygame.Rect(
            x+1, y+1, int(life_bar), 10), 0)

    except Exception as ex:
        print(ex)


def restoreLifePlayer():
    global behavior, player, action
    if behavior == 'stop' and action == 'stop' and player.life < LIFE_PLAYER:
        player.life += 1
        print('Restore Life')


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
    global target, points, score, GAME_STATE
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
                print('NPC caused damage in player')
                ambientSound('attack')
            else:
                print('NPC miss')
        else:
            if damage:
                print('Player caused damage in NPC')
                ambientSound('zombie%s' % random.randint(1, 7))
            else:
                print('Player miss')

    if isDead(target2):
        if target2.isNonPlayerCharacter:
            target = None
            enemys.remove(target2)
            ambientSound('dead')
            points += 1
            score += 1
            print('Enemy elimined')
        else:
            GAME_STATE = 'gameover'  # NOQA


## manage status for player and enemies
def manageStatus(time_passed_seconds):
    global target, tiles, behavior, world, action, attempts_flee

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
        if player.life < 4:  # TODO: Create percent life 30%
            action = 'flee'
            if not player.can_move:
                if attempts_flee > 6:
                    action = 'attack'
                else:
                    action = 'run'
                    attempts_flee += 1
        elif distance <= 30:
            action = 'attack'
        else:
            action = 'hunter'
    else:
        action = 'stop'
        attempts_flee = 0
        # Not target
        if player.life == LIFE_PLAYER:
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
    global min_enemys
    while enemys.__len__() < min_enemys:
        if enemys.__len__() < MAX_ENEMYS:
            sprite = 'girl%s' % (random.randint(1, 3))
            pos_level = np.array(LEVEL['enemy']).__len__()
            try:
                position = LEVEL['enemy'][random.randint(0, pos_level)]
                enemy_pos = np.array(position)
            except IndexError:
                enemy_pos = np.array(LEVEL['enemy'][0])

            enemys.append(Agent(world, 'wander', images[sprite], enemy_pos,
                          MAX_ENEMY_SPEED, LIFE_ENEMY, RATE_ENEMY,
                          DAMAGE_ENEMY, is_npc=True))
        else:
            break


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
        "girl1": pygame.image.load("../res/Character Pink Girl.png"),
        "girl2": pygame.image.load("../res/Character Cat Girl.png"),
        "girl3": pygame.image.load("../res/Character Horn Girl.png"),
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

        "icon damage": pygame.image.load(
            "../res/Passive-heartofthegladiator.png"),
        "icon life": pygame.image.load("../res/Passive-trollsblood.png"),
        "icon vision": pygame.image.load("../res/Passive-blooddrinker.png"),

        "icon damage disabled": pygame.image.load(
            "../res/Passive-heartofthegladiatorOff.png"),
        "icon life disabled": pygame.image.load(
            "../res/Passive-trollsbloodOff.png"),
        "icon vision disabled": pygame.image.load(
            "../res/Passive-blooddrinkerOff.png"),

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

    print("Dialog box.")

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

    while pygame.event.wait().type != pygame.KEYDOWN:
        pass

    print("Dialog acknowledged.")


def backgroundMusic():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.fadeout(1000)
    else:
        pygame.mixer.music.load("../res/" + random.choice(TRACKS))
        pygame.mixer.music.set_volume(0.7)
        pygame.mixer.music.play(-1)


def introMusic():
    pygame.mixer.music.load("../res/sounds/introduction.wav")
    pygame.mixer.music.play(-1)


def gameOverMusic():
    pygame.mixer.music.load("../res/sounds/gameover.wav")
    pygame.mixer.music.play(-1)


def ambientSound(action=None):
    if action:
        if action == 'bite':
            sound = 'bite.wav'
        elif action == 'dead':
            sound = 'dead.wav'
        elif action == 'menu':
            sound = 'bite.wav'
        elif action == 'newGame':
            sound = 'come_here.wav'
        else:
            sound = '%s.wav' % action

        cn = pygame.mixer.find_channel()
        s = pygame.mixer.Sound("../res/sounds/%s" % sound)
        pygame.mixer.Sound.get_num_channels
        cn.queue(s)
    else:
        if random.randint(1, 10)/2 == 0:
            s = pygame.mixer.Sound("../res/sounds/zombie%.wav" % (
                random.randint(1, 7)))
            s.play()


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

    text = font.render('Points: %s' % str(points), False, (0, 0, 0))
    tiles.blit(text, (520, 600))

    text = font.render('Life: %s' % str(player.life), False, (0, 0, 0))
    tiles.blit(text, (0, 600))

    for i in enemys:
        i.blitOn(tiles)
    player.blitOn(tiles)


def aboutScreen():
    global GAME_STATE
    print('About screen not implemented')
    GAME_STATE = 'menu'


def gameOverScreen():
    global score, GAME_STATE

    background = pygame.image.load("../res/go.jpg")
    backgroundRect = background.get_rect()

    # Display level, and display behavior.
    font = pygame.font.Font("../res/Jet Set.ttf", 36)
    gameOverMusic()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
        key_press = pygame.key.get_pressed()
        if key_press[pygame.K_SPACE] or pygame.mouse.get_pressed() == (1, 0, 0):
            GAME_STATE = 'menu'
            break
        pygame.event.pump()
        screen.fill((0, 0, 0))
        screen.blit(background, backgroundRect)

        text = font.render('You has made %s points' % score,
                           True, (100, 100, 100))
        screen.blit(text, (200, 10))

        text = font.render('Press SPACE for continue', True, (100, 100, 100))
        screen.blit(text, (130, 630))

        pygame.display.update()


def menuScreen():
    global GAME_STATE, LEVEL

    background = pygame.image.load("../res/bc.jpg")
    backgroundRect = background.get_rect()
    #font = pygame.font.Font("../res/Jet Set.ttf", 36)

    options = [Option("New Game", (60, 60), 'newGame', screen),
               Option("About", (400, 60), 'about', screen),
               Option("Quit", (700, 60), 'quit', screen)]
    options_level = [Option("New Game", (60, 60), 'newGame', screen),
                     Option("About", (400, 60), 'about', screen),
                     Option("Quit", (700, 60), 'quit', screen),
                     Option("Easy", (70, 120), 'EASY', screen),
                     Option("Medium", (70, 180), 'MEDIUM', screen),
                     Option("Hard", (70, 240), 'HARD', screen)]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
        pygame.event.pump()
        screen.fill((0, 0, 0))
        screen.blit(background, backgroundRect)

        for option in options:
            if option.rect.collidepoint(pygame.mouse.get_pos()):
                option.hovered = True

                if pygame.mouse.get_pressed() == (1, 0, 0):
                    option.clicked = True
                    #ambientSound('menu')
                else:
                    option.clicked = False
            else:
                option.hovered = False
                option.clicked = False
            option.draw()
            if option.clicked:
                GAME_STATE = option.new_window()
                go = False
                if GAME_STATE == 'EASY':
                    LEVEL = levels.EASY
                    go = True
                elif GAME_STATE == 'MEDIUM':
                    LEVEL = levels.MEDIUM
                    go = True
                elif GAME_STATE == 'HARD':
                    LEVEL = levels.HARD
                    go = True
                if go:
                    ambientSound('newGame')
                    pygame.mixer.music.stop()
                    GAME_STATE = "gameRun"

        pygame.display.update()
        if GAME_STATE != 'menu':
            if GAME_STATE == 'newGame':
                options = options_level
            else:
                break


def screenGame(GAME_STATE):
    if GAME_STATE == 'menu':
        introMusic()
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
