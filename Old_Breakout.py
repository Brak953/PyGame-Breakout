from random import randrange as rnd
import pygame


def BreakoutMinigame(width, height):
    # Various game variables
    global fps
    running = True
    WIDTH, HEIGHT = width, height
    fps = 30
    
    # Paddle settings
    paddle_w = 330
    paddle_h = 35
    paddle_speed = 15
    paddle = pygame.Rect(WIDTH // 2 - paddle_w // 2, HEIGHT - paddle_h - 10, paddle_w, paddle_h)
    
    # Ball settings
    ball_radius = 20
    ball_speed = 6
    ball_rect = int(ball_radius * 2 ** 0.5)
    ball = pygame.Rect(rnd(ball_rect, WIDTH - ball_rect), HEIGHT // 2, ball_rect, ball_rect)
    dx, dy = 1, -1
    
    # Scores for the two players
    global P1_score, P2_score, scores
    P1_score = 0
    P2_score = 0
    scores = []

    # Block configuration
    global block_list, color_list
    block_list = [pygame.Rect(10 + 120 * i, 10 + 70 * j, 100, 50) for i in range(10) for j in range(4)]
    color_list = [(rnd(30, 256), rnd(30, 256), rnd(30, 256)) for i in range(10) for j in range(4)]

    # Function for resetting variables and values to how they were when the function was initially called
    def ResetScreen(ball, paddle):
        global block_list, color_list, n, fps, hit_index
        block_list = [pygame.Rect(10 + 120 * i, 10 + 70 * j, 100, 50) for i in range(10) for j in range(4)]
        color_list = [(rnd(30, 256), rnd(30, 256), rnd(30, 256)) for i in range(10) for j in range(4)]
        ball.x, ball.y = rnd(ball_rect, WIDTH - ball_rect), HEIGHT // 2
        paddle.x, paddle.y = WIDTH // 2 - paddle_w // 2, HEIGHT - paddle_h - 10
        fps = 30
        n = 0
        hit_index = 0

    # Variables for screen and clock
    pygame.init()
    sc = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    # Background image
    img = pygame.image.load('Background.jpg').convert()
    img = pygame.transform.scale(img, (width, height))

    # Runs the game twice, once for each player
    for k in range (2):
        global n
        n = 0

        # Makes sure the ball stays still at the start of each round, before changing the x and y values
        def moveBall(n):
            if n <=50:
                return
            else:
                ball.x += ball_speed * dx
                ball.y += ball_speed * dy

        # Collision logic
        def detect_collision(dx, dy, ball, rect):
            if dx > 0:
                delta_x = ball.right - rect.left
            else:
                delta_x = rect.right - ball.left
            if dy > 0:
                delta_y = ball.bottom - rect.top
            else:
                delta_y = rect.bottom - ball.top

            if abs(delta_x - delta_y) < 10:
                dx, dy = -dx, -dy
            elif delta_x > delta_y:
                dy = -dy
            elif delta_y > delta_x:
                dx = -dx
            return dx, dy

        # Main game loop
        while running:
            # Quits game if it has been told to do so
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            # Display background image
            sc.blit(img, (0, 0))

            # Draw remaining game objects
            [pygame.draw.rect(sc, color_list[color], block) for color, block in enumerate(block_list)]
            pygame.draw.rect(sc, pygame.Color('darkorange'), paddle)
            pygame.draw.circle(sc, pygame.Color('white'), ball.center, ball_radius)

            # Increase the value of n, up to 50, before calling the function moveBall using this value
            if n <= 50:
                n+=1
            moveBall(n)

            # Check collisions with walls
            if ball.centerx < ball_radius or ball.centerx > WIDTH - ball_radius:
                dx = -dx
            if ball.centery < ball_radius:
                dy = -dy

            # Check collision with paddle
            if ball.colliderect(paddle) and dy > 0:
                dx, dy = detect_collision(dx, dy, ball, paddle)

            # Check collision with blocks
            hit_index = ball.collidelist(block_list)
            if hit_index != -1:
                hit_rect = block_list.pop(hit_index)
                if k == 0:
                    P1_score += 1
                elif k == 1:
                    P2_score += 1
                dx, dy = detect_collision(dx, dy, ball, hit_rect)
                # Increase ball speed
                fps += 10

            # Check win or game over conditions
            if ball.bottom > HEIGHT:
                ResetScreen(ball, paddle)
                k+=1
                dx, dy = 1, -1
                break
            # Checks if all blocks on screen 
            elif not len(block_list):
                ResetScreen(ball, paddle)
                k+=1
                dx, dy = 1, -1
                break

            # Handle user input
            key = pygame.key.get_pressed()
            if (key[pygame.K_LEFT] or key[pygame.K_a]) and paddle.left > 0:
                paddle.left -= paddle_speed
            if (key[pygame.K_RIGHT] or key[pygame.K_d]) and paddle.right < WIDTH:
                paddle.right += paddle_speed

            # Update screen
            pygame.display.flip()
            clock.tick(fps)
        
        # Checks if the loop is on its first cycle
        if k == 1:
            # Adds the amount of blocks destroyed to 
            scores.append(P1_score)

            sc.fill('black')

            # Display game over message
            font = pygame.font.Font(None, 36)
            message = f"GAME OVER! YOUR SCORE: {P1_score}!"
            text = font.render(message, True, (255, 255, 255))
            text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
            sc.blit(text, text_rect)

            # Display "PRESS SPACE TO CONTINUE" message
            font = pygame.font.Font(None, 24)
            message = "PRESS SPACE TO CONTINUE"
            text = font.render(message, True, (255, 255, 255))
            text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
            sc.blit(text, text_rect)

            # Pause the game loop
            pygame.display.flip()
            paused = True

            # Makes sure the game does not play unless spacebar is pressed
            while paused:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        paused = False
                clock.tick(fps)
        
        # Second cycle of the loop
        elif k == 2:
            scores.append(P2_score)
            score_difference = scores[0] - scores[1]
            
            # Checks the difference in the two player scores to determine the winner
            if score_difference > 0:
                player_win = 1
            elif score_difference < 0:
                player_win = 2
            elif score_difference == 0:
                player_win = rnd(1,3)
            
            # Display game over message
            sc.fill('black')
            font = pygame.font.Font(None, 36)
            message = ''
            if player_win == 1:
                message = f"P1 WON! P2 SCORE: {P2_score}!"
            elif player_win == 2:
                message = f"P2 WON! P2 SCORE: {P2_score}!"
            text = font.render(message, True, (255, 255, 255))
            text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
            sc.blit(text, text_rect)

            # Display "PRESS SPACE TO CONTINUE" message
            font = pygame.font.Font(None, 24)
            message = "PRESS SPACE TO CONTINUE"
            text = font.render(message, True, (255, 255, 255))
            text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
            sc.blit(text, text_rect)

            # Pause the game loop
            pygame.display.flip()
            paused = True

            # Makes sure the game does progress further unless spacebar is pressed
            while paused:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        paused = False
                clock.tick(fps)
            return player_win

if __name__ == '__main__':
    BreakoutMinigame(1200, 800)