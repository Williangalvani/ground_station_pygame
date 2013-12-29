__author__ = 'Will'
import pygame
from pygame.locals import *
from os.path import abspath, dirname, join
WHERE_AM_I = abspath(dirname(__file__))

from random import randrange

import os

def load_image(name, colorkey=None):
    fullname = os.path.join('name for images folder here', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()


class FrameSprite(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(join(WHERE_AM_I,"horizon_frame_with_arrow_small.png"))
        self.image.convert_alpha()
        self.rect = self.image.get_rect()


def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

class Horizon():

    def __init__(self):
        self.roll = 45
        self.tilt = 0
        self.yaw = 0


        self.frame = FrameSprite()
        self.background = pygame.image.load(join(WHERE_AM_I,"horizon_interior_small.png"))
        self.background_mask, notused = load_image(join(WHERE_AM_I,"interior_alpha_small.png"),-1)
        self.tilted_background = pygame.Surface(self.frame.rect.size,HWSURFACE)
        #self.background_mask.convert_alpha()

        self.img_surface = pygame.Surface(self.frame.rect.size,HWSURFACE)
        self.mask_surface = pygame.Surface(self.frame.rect.size,HWSURFACE)
        self.surface = pygame.Surface(self.frame.rect.size)

        #self.frame.blit(self.img_surface)

        self.mask_surface.blit(self.background_mask,(0,0))

        self.sprite_group = pygame.sprite.Group()
        self.frame.add(self.sprite_group)

        self.newsurf=pygame.Surface(self.frame.rect.size,HWSURFACE)
        self.update()


    def set_attitude(self,roll,pitch):
        self.roll = roll
        self.tilt = pitch
        self.update()


    def update(self):
        tilt = self.tilt * 1.425
        # self.roll+=randrange(-2,1)
        # self.tilt+=randrange(-2,1)
        self.tilted_background.blit(self.background,(0,tilt))
        rolled_background = rot_center(self.tilted_background,self.roll)
        self.img_surface.blit(rolled_background,(0,0))

        self.newsurf.blit(self.img_surface,(0,0))
        self.newsurf.blit(self.mask_surface  ,(0,0),None,pygame.BLEND_RGBA_MIN)
        self.newsurf.convert()
        colorkey = self.newsurf.get_at((0,0))
        self.newsurf.set_colorkey(colorkey, RLEACCEL)
        self.sprite_group.draw(self.newsurf)

