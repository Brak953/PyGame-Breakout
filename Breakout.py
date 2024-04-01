import pygame
from random import randrange as rnd

# Define game parameters
HEIGHT = 800
WIDTH = 1200
FPS = 30

class BlockGrid:
    """
    Class for making grid consisting of interactive blocks

    No parameters
    """
    def __init__(self):
        # Setting block size
        self.width = 100
        self.height = 50

    def createGrid(self):
        """
        Method for making lists containing the positions and colors of each individual block in the grid
        """
        self.block_list = [pygame.Rect(10 + 120 * i, 10 + 70 * j, self.width, self.height) for i in range(10) for j in range(4)]
        self.color_list = [(rnd(30, 256), rnd(30, 256), rnd(30, 256)) for _ in range(len(self.block_list))]

    def draw(self, display):
        """
        Method for iterating through the block list and displaying each individual block on-screen

        Parameters:
        display: pygame.Surface
        """
        [pygame.draw.rect(display, self.color_list[color], block) for color, block in enumerate(self.block_list)]

class Paddle:
    """
    Class for the user-controlled paddle

    Parameters:
    width; int
    height; int
    paddle_speed; int 
    """
    def __init__(self, width, height, paddle_speed):
        self.width = width
        self.height = height
        self.speed = paddle_speed
        self.rect = pygame.Rect(WIDTH // 2 - self.width // 2, HEIGHT - self.height - 10, self.width, self.height)
    
    def move(self, direction):
        """
        Method for moving the paddle left and right and ensuring it is inside the playable area

        Parameters:
        direction: str
        """
        if direction == "left" and self.rect.left > 0:
            self.rect.x -= self.speed
        elif direction == "right" and self.rect.right < WIDTH:
            self.rect.x += self.speed

class Ball:
    """
    Class for the ball

    Parameters:
    radius: int
    speed: int
    """
    def __init__(self, radius, speed):
        self.radius = radius
        self.speed = speed
        self.surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)  # Create transparent surface
        self.original_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)  # Original surface for transparency
        pygame.draw.circle(self.surface, (255, 255, 255), (radius, radius), radius)  # Draw a white circle on the surface
        self.rect = self.surface.get_rect(center=(rnd(radius, WIDTH - radius), HEIGHT // 2))
        self.dx = 1
        self.dy = -1
        self.original_surface.blit(self.surface, (0, 0))  # Copy surface to original_surface for transparency

    def move(self):
        """
        Method for moving the ball across the x and y
        """
        self.rect.x += self.speed * self.dx
        self.rect.y += self.speed * self.dy
    
    def update_transparency(self, score):
        """
        Method for changing the transparency of the ball based on score

        Parameters:
        score: int
        """
        alpha = max(0, min(255, 255 - score * 20))  # Adjust the decrement value for desired transparency change
        self.surface.set_alpha(alpha)  # Set transparency



class BreakoutGame:
    """
    Class for handling game inputs, actions and events

    Parameters:
    width: int
    height: int
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.fps = FPS
        self.paddle_width = 300
        self.paddle_height = 30
        self.paddle_speed = 10
        self.ball_speed = 5
        self.running = True
        self.P1_score = 0
        self.paddle_moving_direction = None
        self.initialize()

    def modifier_screen(self):
        """
        Display the modifier screen with options for playstyle
        """
        self.screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 36)
        text1 = font.render("Choose a modifier:", True, pygame.Color('white'))
        text_rect1 = text1.get_rect(center=(self.width // 2, self.height // 2 - 50))
        text2 = font.render("1. Ball gradually becomes invisible", True, pygame.Color('white'))
        text_rect2 = text2.get_rect(center=(self.width // 2, self.height // 2))
        text3 = font.render("2. Ball speed increases with each hit", True, pygame.Color('white'))
        text_rect3 = text3.get_rect(center=(self.width // 2, self.height // 2 + 50))
        self.screen.blit(text1, text_rect1)
        self.screen.blit(text2, text_rect2)
        self.screen.blit(text3, text_rect3)
        pygame.display.flip()

        # Handling of modification
        modifier_chosen = False
        while not modifier_chosen:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.modifier = "invisible"
                        modifier_chosen = True
                    elif event.key == pygame.K_2:
                        self.modifier = "speed"
                        modifier_chosen = True
                elif event.type == pygame.QUIT:
                    self.modifier = "Shutdown"
                    modifier_chosen = True

    def initialize(self):
        """
        Initialize the pygame display and other necessary components
        """
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Breakout Minigame")
        self.clock = pygame.time.Clock()
        self.load_assets()
        self.modifier_screen()
        self.create_objects()

    def load_assets(self):
        """
        Load background image for the game, with error handling
        """
        try:
            self.background_image = pygame.image.load('Background.jpg').convert()
            self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))
        except pygame.error as e:
            print("Error loading background image:", e)

    def create_objects(self):
        """
        Create instances of paddle, ball, and block grid
        """
        self.paddle = Paddle(self.paddle_width, self.paddle_height, self.paddle_speed)
        self.ball = Ball(10, self.ball_speed)
        self.block_grid = BlockGrid()
        self.block_grid.createGrid()

    def handle_events(self):
        """
        Handle pygame events such as quitting the game
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def handle_input(self):
        """
        Handle user input for moving the paddle
        """
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.paddle.move("left")
            self.paddle_moving_direction = "left"
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.paddle.move("right")
            self.paddle_moving_direction = "right"
        else:
            self.paddle_moving_direction = None

    def handle_collisions(self):
        """
        Handle collisions of the ball with walls, paddle, and blocks
        """
        # Update ball position
        self.ball.move()

        # Check collisions with walls
        if self.ball.rect.centerx < self.ball.radius or self.ball.rect.centerx > self.width - self.ball.radius:
            self.ball.dx = -self.ball.dx
        if self.ball.rect.centery < self.ball.radius:
            self.ball.dy = -self.ball.dy

        # Check collision with paddle
        if self.ball.rect.colliderect(self.paddle.rect) and self.ball.dy > 0:
            # Adjust ball's horizontal velocity based on paddle's movement direction
            if self.paddle_moving_direction == "left":
                self.ball.dx = -abs(self.ball.dx)
            elif self.paddle_moving_direction == "right":
                self.ball.dx = abs(self.ball.dx)
            else:
                # If the ball is moving straight up, adjust its trajectory
                if self.ball.dy < 0:
                    self.ball.dx = -abs(self.ball.dx) if self.ball.dx > 0 else abs(self.ball.dx)

            self.ball.dy = -self.ball.dy

        # Check collision with blocks
        hit_index = self.ball.rect.collidelist(self.block_grid.block_list)
        if hit_index != -1:
            hit_rect = self.block_grid.block_list.pop(hit_index)
            self.block_grid.color_list.pop(hit_index)            
            self.P1_score += 1

            # Determine the side of the block hit by the ball
            if self.ball.dx > 0:  # Ball moving right
                if self.ball.rect.right > hit_rect.left and self.ball.rect.left < hit_rect.left:
                    self.ball.dx = -self.ball.dx
            else:  # Ball moving left
                if self.ball.rect.left < hit_rect.right and self.ball.rect.right > hit_rect.right:
                    self.ball.dx = -self.ball.dx

            if self.ball.dy > 0:  # Ball moving down
                if self.ball.rect.bottom > hit_rect.top and self.ball.rect.top < hit_rect.top:
                    self.ball.dy = -self.ball.dy
            else:  # Ball moving up
                if self.ball.rect.top < hit_rect.bottom and self.ball.rect.bottom > hit_rect.bottom:
                    self.ball.dy = -self.ball.dy

            if self.modifier == "speed":
                # Increase ball speed based on the number of blocks hit
                self.ball.speed += 0.1 * self.P1_score

                # Increase paddle speed based on the number of blocks hit
                self.paddle.speed += 0.1 * self.P1_score
            elif self.modifier == "invisible":
                self.ball.update_transparency(self.P1_score)  # Update ball transparency based on score


    def update_screen(self):
        """
        Update the screen with game objects
        """
        self.screen.blit(self.background_image, (0, 0))
        self.block_grid.draw(self.screen)
        pygame.draw.rect(self.screen, pygame.Color('darkorange'), self.paddle.rect)
        self.screen.blit(self.ball.surface, self.ball.rect)
        pygame.display.flip()

    def reset_screen(self):
        """
        Reset the game screen and modifier choice
        """
        self.modifier = None
        self.create_objects()
        self.P1_score = 0

    def end_screen(self):
        """
        Display the end screen with the final score
        """
        self.screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 36)
        text = font.render(f"Game Over! Blocks Destroyed: {self.P1_score}", True, pygame.Color('white'))
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.delay(3000)  # Display the end screen for 3 seconds before quitting
        self.running = False

    def run(self):
        """
        Main game loop
        """
        # Checks if the game is supposed to be running, and not being told to shut down
        while self.running and self.modifier != "Shutdown":
            # If the game is supposed to run, continue as normal
            self.handle_events()
            self.handle_input()
            self.handle_collisions()
            self.update_screen()

            # Check if the ball hits the bottom of the screen
            if self.ball.rect.bottom >= self.height:
                self.end_screen()  # Call the end screen function

            # On-screen updates are handled using the fps tied to the class
            self.clock.tick(self.fps)

        pygame.quit()

# Function that makes the file only run if run directly, or called seperately
if __name__ == '__main__':
    game = BreakoutGame(WIDTH, HEIGHT)
    game.run()