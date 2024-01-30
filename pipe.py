import pygame

class Pipe(pygame.sprite.Sprite):

  def __init__(self, is_top, x_pos, y_pos):
    super().__init__()
    if is_top:
      pipe = pygame.image.load("assets/graphics/pipe/top_pipe.png").convert_alpha()
    else:
      pipe = pygame.image.load("assets/graphics/pipe/bottom_pipe.png").convert_alpha()
    
    self.image = pygame.transform.rotozoom(pipe, 0, 3.0)
    self.rect = self.image.get_rect(center=(x_pos, y_pos))
    self.rect.width = 250
    self.rect.height = 375

    self.passed = False

  def move_pipe(self):
    """
    : set the moving speed of spawning pipes
    """
    self.rect.x -= 4

  def destroy(self):
    """
    : destroy pipes
    : when it is off the screen
    """
    if self.rect.right <= -100:
      self.kill()
  
  def update(self):
    self.move_pipe()
    self.destroy()

