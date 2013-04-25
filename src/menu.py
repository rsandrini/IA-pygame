from pygame.locals import *  # NOQA
import pygame


class Option:

    hovered = False
    clicked = False

    def __init__(self, text, pos, gameState, screen):
        self.text = text
        self.pos = pos
        self.menu_font = pygame.font.Font("../res/Jet Set.ttf", 36)
        self.screen = screen
        self.gameState = gameState

        self.set_rect()
        self.draw()

    def draw(self):
        self.set_rend()
        self.screen.blit(self.rend, self.rect)

    def set_rend(self):
        self.rend = self.menu_font.render(self.text, True, self.get_color())

    def get_color(self):
        if self.hovered:
            if self.clicked:
                return (255, 0, 0)
            else:
                return (228, 25, 25)
        else:
            return (100, 100, 100)

    def set_rect(self):
        self.set_rend()
        self.rect = self.rend.get_rect()
        self.rect.topleft = self.pos

    def new_window(self):
        if self.clicked:
            #self.screen.fill((159, 182, 205))
            return self.gameState
        else:
            pass
