import pygame, sys
from bird import Bird
from background import Background
from pipe import Pipe
from random import randint
import json
from time import sleep

# Constants
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 800
DISPLAY_CAPTION = "Flappy Bird"
FPS = 60

TITLE_FONT_SIZE = 150
MESSAGE_FONT_SIZE = 50

BACKGROUND_X_POS = 0
BACKGROUND_SPEED = 2
BGM_LOOP = -1
BGM_VOLUME = 0.3

PIPE_SPAWNING_INTERVAL = 3500
PIPE_SPAWNING_X_POS = 1720
OPTIMAL_GAP_OFFSET = 100

SCORE = 0
SCORE_POS = (1550, 50)
HIGHEST_SCORE_POS = (50, 50)


class Game:
    def __init__(self):
        """Initialize pygame and set up the game window, fonts, sprites, etc."""
        
        self.setup()

        # Create background
        self.background = Background()
        self.background_width = self.background.image.get_width()
        self.background_x_pos = BACKGROUND_X_POS 
        self.bgm = pygame.mixer.Sound("assets/audio/bgm.mp3")
        self.go_sound = pygame.mixer.Sound("assets/audio/game_over.mp3")
        self.hit_sound = pygame.mixer.Sound("assets/audio/hit.mp3")
        self.fall_sound = pygame.mixer.Sound("assets/audio/fall.mp3")
        self.score_sound = pygame.mixer.Sound("assets/audio/score.mp3")

        # Create font
        self.title_font = pygame.font.Font("assets/font/Pixeltype.ttf", TITLE_FONT_SIZE)
        self.message_font = pygame.font.Font("assets/font/Pixeltype.ttf", MESSAGE_FONT_SIZE)

        # Create player
        self.bird = pygame.sprite.GroupSingle()
        player = Bird()
        self.bird.add(player)

        # Create pipes 
        self.pipes = pygame.sprite.Group()

        # Create score
        self.load_score()

        # Game state
        self.game_active = False

        # Timer
        # Pipe timer 
        self.pipe_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.pipe_timer, PIPE_SPAWNING_INTERVAL)

        # Play BGM
        self.bgm.play(loops=BGM_LOOP)
        self.bgm.set_volume(BGM_VOLUME)



    def main(self):
        self.setup()
        self.run_game()

    def setup(self):
        """Initialize basic pygame setup"""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(DISPLAY_CAPTION)
        self.clock = pygame.time.Clock()
    
    def run_game(self): 
        """
        Integrate methods that run the game
        """
        while True:
            self.handle_events()
            self.update()
            self.render()
            pygame.display.update()
            self.clock.tick(FPS)

    def handle_events(self):
        """Handle different types of events (keyboard/mouse)"""
        for event in pygame.event.get():
            # Quit game
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.quit_game()
            if event.type == self.pipe_timer:
                self.spawn_pipes()
            else:
                # start the game by pressing space
                if not self.game_active and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.restart_game()

    def update(self):
        """
        Logic for moving background, updating bird position, handling collisions, etc.
        """
        if self.game_active:
            # moving background - update background_x_pos by the function return value
            self.background_x_pos = self.move_background()

            # draw bird and call bird update method 
            self.bird.draw(self.screen)
            self.bird.update()

            # draw pipes and call pipe update method
            self.pipes.draw(self.screen)
            self.pipes.update()

            # collisions
            self.game_active = self.game_over()

            # update score
            self.data['score'] = self.update_score()

    def render(self):
        """
        : game_active == True
        Render game menu

        : game_active == False
        Render game over screen.
        """
        
        if self.game_active:
            
            # display score
            score_surf = self.message_font.render(f"Score: {int(self.data['score'])}", False, (255,255,255))
            score_rect = score_surf.get_rect(midright =SCORE_POS)
            self.screen.blit(score_surf, score_rect)

            # display highest score
            highest_score_surf = self.message_font.render(f"Highest Score: {int(self.data['highest_score'])}", False, (255,255,255))
            highest_score_rect = highest_score_surf.get_rect(midleft =HIGHEST_SCORE_POS)
            self.screen.blit(highest_score_surf, highest_score_rect)
            
            self.visualize_rect()

        else:
            # render background first
            self.screen.blit(self.background.image, self.background.rect)
            self.bird.draw(self.screen)

            if self.data['score'] == SCORE:

                self.render_menu()
                
            else:
                self.render_game_over()
                
    # Helper functions
    def render_menu(self):
        """Render menu"""
        # Title
        game_title = self.title_font.render("Flappy Bird", False, (0,0,0))
        game_title_rect = game_title.get_rect(center=(800, 300))

        # Message 
        game_message = self.message_font.render("Press Space To Start", False, (0,0,0))
        game_message_rect = game_message.get_rect(center=(800, 600))

        self.screen.blit(game_title, game_title_rect)
        self.screen.blit(game_message, game_message_rect)
    
    def render_game_over(self):
        """Render game over screen"""

        game_over_title = self.title_font.render("Game Over!", False, (0,0,0))
        game_over_rect = game_over_title.get_rect(center=(800, 300))
        # Score
        score_message = self.message_font.render(f"Your score: {int(self.data['score'])}", False, (0,0,0))
        score_message_rect = score_message.get_rect(center=(800, 600))
        
        # Highest Score
        highest_score_message = self.message_font.render(f"The Highest Score: {int(self.data['highest_score'])}", False, (0,0,0))
        highest_score_rect = highest_score_message.get_rect(center=(800, 700))
        self.screen.blit(game_over_title, game_over_rect)
        self.screen.blit(score_message, score_message_rect)
        self.screen.blit(highest_score_message, highest_score_rect)

    def move_background(self):
        """
        Blit background to screen & make it move end to end continuously.

        :param background_x_pos: x-coordinate of the background
        :type background_x_pos: int

        :return: updated background_x_pos value to be stored in a variable.
        :rtype: int
        """
        self.screen.blit(self.background.image, (self.background_x_pos, 0))
        self.screen.blit(self.background.image, (self.background_width + self.background_x_pos, 0))
        # reset x when background move outside the screen
        if (self.background_x_pos == -self.background_width):
            self.background_x_pos = 0
        # set the speed of moving background
        self.background_x_pos -= BACKGROUND_SPEED
        return self.background_x_pos

    def game_over(self):
    
        """
        trigger game over if 
        : player collides with pipes
        : player jumps out of the screen
        : player falls out of the screen

        :return: False if condition has met, otherwise True.
        :rtype: boolean
        """
        if self.bird.sprite.trigger_game_over() or pygame.sprite.spritecollide(self.bird.sprite, self.pipes, False): 
            # play game_over sound tracks
            self.integrate_game_over_sound()
            # reset
            self.pipes.empty()
            self.bird.sprite.reset()
            if self.data['score'] > self.data['highest_score']: 
                self.data['highest_score'] = self.data['score']
            return False
        else:
            return True

    def update_score(self):
        """
        Update Score mechanism
        : increase score when bird middle x passes pipe middle x (for individual pipe) and when the pipe has not been passed yet.
        : note: the score increase only by 0.5 because each pair of pipes has two pipes in it - total = 1
        : set self.passed to be True for each indivual pipe - prevent the score from updating after passing.

        :return: updated score when bird passes the pipes.
        :rtype: float
        """
        for pipe in self.pipes:
            if self.bird.sprite.rect.center[0] >= pipe.rect.center[0] and not pipe.passed:
                self.play_score_sound()
                self.data['score'] += 0.5
                pipe.passed = True
        return self.data['score']   

    def load_score(self):
        """
        Load JSON data from a text file.
        """
        try:
            with open('score.txt', 'r') as score_file:
                self.data = json.load(score_file)
                self.data['score'] = SCORE
        except:
            print('No file is created yet.')
            
    def save_score(self):
        """
        Create a text file to store JSON data if there's no file exists before.
        Otherwise, store the highest score in each game.
        """
        
        if self.data['score'] > self.data['highest_score']: 
            self.data['highest_score'] = self.data['score']
            with open('score.txt', 'w') as score_file:
                json.dump(self.data, score_file)

    def get_optimal_pipes(self):
        """
        Implement optimal gap size - ensure bottom pipe not always appear to be very low.
        
        :return: y_position for top pipes and bottom pipes
        :rtype: int
        """
        y_pos_top = randint(-100 - OPTIMAL_GAP_OFFSET, 200 - OPTIMAL_GAP_OFFSET)
        y_pos_bottom = randint(600 + OPTIMAL_GAP_OFFSET, 800 + OPTIMAL_GAP_OFFSET)
        
        while y_pos_bottom - y_pos_top < 500:
            y_pos_bottom = randint(800 + OPTIMAL_GAP_OFFSET, 1000 + OPTIMAL_GAP_OFFSET)
        return y_pos_top, y_pos_bottom
    
    def spawn_pipes(self):
        """
        Get optimal pipe position and gap size between pipes
        Create top pipe and bottom pipe instances
        Spawning pipes in pair
        """
        y_pos_top, y_pos_bottom = self.get_optimal_pipes()
        
        top_pipe = Pipe(is_top=True, x_pos= PIPE_SPAWNING_X_POS, y_pos= y_pos_top)
        bottom_pipe = Pipe(is_top=False, x_pos= PIPE_SPAWNING_X_POS, y_pos= y_pos_bottom )
        
        self.pipes.add(top_pipe, bottom_pipe)

    def quit_game(self):
        """Save score and quit the game window"""
        self.save_score()
        pygame.quit()
        sys.exit()
    
    def restart_game(self):
        """reset game state to TRUE and score value to zero"""
        self.game_active = True
        self.data['score'] = SCORE 
        self.pipes.empty() # to clear pipes before start

    # Utility
    def visualize_rect(self):
        # visualize rectangles of bird and pipes
        pygame.draw.rect(self.screen, (250, 0, 0), self.bird.sprite.rect, 2)
        for pipe in self.pipes:
            pygame.draw.rect(self.screen, (0,0,255), pipe.rect, 2)
    
    # Audio
    def integrate_game_over_sound(self):
        """
        integrate sound - hit, fall, and game over
        """
        self.play_hit_sound()
        if pygame.mixer.get_busy():
                sleep(0.2)
        self.play_fall_sound()
        if pygame.mixer.get_busy():
                sleep(0.2)
        self.play_game_over_sound()
        if pygame.mixer.get_busy():
                sleep(0.2)

    def play_hit_sound(self):
        self.hit_sound.play()
        self.hit_sound.set_volume(0.5)

    def play_fall_sound(self):
        self.fall_sound.play()
        self.fall_sound.set_volume(0.5)

    def play_game_over_sound(self):
        self.go_sound.play()
        self.go_sound.set_volume(0.5)
    
    def play_score_sound(self):
        self.score_sound.play()
        self.score_sound.set_volume(0.3)

if __name__ == "__main__":
    # Initialize and run the game
    game = Game()
    game.main()