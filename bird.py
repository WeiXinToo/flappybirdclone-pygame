import pygame
class Bird(pygame.sprite.Sprite):
  def __init__(self):
    super().__init__()
    image1 = pygame.image.load("assets/graphics/bird/bird1.png").convert_alpha()
    image2 = pygame.image.load("assets/graphics/bird/bird2.png").convert_alpha()
    bird_frame1 = pygame.transform.rotozoom(image1, 0, 1)
    bird_frame2 = pygame.transform.rotozoom(image2, 0, 1)

    self.bird_index = 0
    self.bird_move = [bird_frame1, bird_frame2]

    self.image= self.bird_move[self.bird_index]
    self.rect = self.image.get_rect(center = (800, 450))

    self.rect.width = 120
    self.rect.height = 90

    self.gravity = 0
    self.is_jumping = False

    self.jump_sound = pygame.mixer.Sound("assets/audio/jump.mp3")
  
  def animate_bird(self):
      """
      : animate birds 
      """
      self.bird_index += 0.1
      if self.bird_index >= len(self.bird_move):
        self.bird_index = 0
      self.image = self.bird_move[int(self.bird_index)]

  def apply_gravity(self):
    """
    : simulate gravity of player - falling mechanism
    """
    self.gravity += 1
    self.rect.y += self.gravity

  def player_jump(self):
    """
    : press space to jump
    : jump control - one jump per space pressed
    """
    keys= pygame.key.get_pressed()

    if keys[pygame.K_SPACE] and self.rect.bottom >= 0 and not self.is_jumping:
      self.gravity = -18
      self.jump_sound.play()
      self.jump_sound.set_volume(0.5)
      self.is_jumping = True
      
    if keys[pygame.K_SPACE] == False:
      self.is_jumping = False
      
  
  def trigger_game_over(self):
      """
      : check if the bird fly outside the screen
      : [1] refers to y coordinate
      """
      return self.rect.midbottom[1] <= -50 or self.rect.midtop[1] >= 850  
    

  def reset(self):
    """
    : reset player position
    : use during game over
    """
    self.rect.center = (800, 450)
    self.gravity = 0

  
  def update(self):
    self.player_jump()
    self.animate_bird()
    self.apply_gravity()
    
    