import pygame

class Background(pygame.sprite.Sprite):

  def __init__(self):
    self.i = 0
    self.image = pygame.image.load('assets/graphics/background/scenery.jpg').convert()
    self.rect = self.image.get_rect(topleft = (0,0))
  