import pygame
pygame.init()


WIDTH, HEIGHT, = 700, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
BALL_RADIUS = 7

SCORE_FONT = pygame.font.SysFont("comicsans", 30)

WINNING_SCORE = 10

BOUNCE_SOUND = pygame.mixer.Sound("boing-2-44164.mp3")
BOUNCE_SOUND.set_volume(1)
BACKGROUND_MUSIC = pygame.mixer.Sound("powerful-beat-121791.mp3")
BACKGROUND_MUSIC.set_volume(0.5)
VICTORY_MUSIC = pygame.mixer.Sound("victoryff.swf.mp3")

#Mixer channels
BOUNCE_CHANNEL = pygame.mixer.Channel(0)
MUSIC_CHANNEL = pygame.mixer.Channel(1)
VICTORY_CHANNEL = pygame.mixer.Channel(2)

class Paddle:
    COLOR = WHITE
    VEL = 6

    def __init__(self, x, y, width, height):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.width = width
        self.height = height

    def draw(self, win):
        pygame.draw.rect(win, self.COLOR, (self.x, self.y, self.width, self.height))

    def move(self, up=True):
        if up:
            self.y -= self.VEL
        else:
            self.y += self.VEL

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y

class Ball:
    MAX_VEL = 5
    COLOR = WHITE

    def __init__(self, x, y, radius):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.radius = radius
        self.x_vel = self.MAX_VEL
        self.y_vel = 0

    def draw(self, win):
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.radius)

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel

    def reset(self, direction):
        self.x = self.original_x
        self.y = self.original_y
        self.y_vel = 0
        
        if direction is True:
            self.x_vel = self.MAX_VEL
            self.x_vel *= -1
        else:
            self.x_vel *= -1 
            self.x_vel = self.MAX_VEL
       

def draw(win, paddles, ball, left_score, right_score):
    win.fill(BLACK)

    left_score_text = SCORE_FONT.render(f"{left_score}", 1, WHITE)
    right_score_text = SCORE_FONT.render(f"{right_score}", 1, WHITE)
    win.blit(left_score_text, (WIDTH // 4 - left_score_text.get_width()//2, 20))
    win.blit(right_score_text, (WIDTH * (3/4) - right_score_text.get_width()//2, 20))

    for paddle in paddles:
        paddle.draw(win) 

    for i in range(10, HEIGHT, HEIGHT//30):
        if i % 2 == 1:
            continue
        pygame.draw.rect(win, WHITE, (WIDTH//2 - 1, i, 6, HEIGHT//60))

    ball.draw(win)
    pygame.display.update()


def handle_collision(ball, left_paddle, right_paddle):
    
    #collision with ceilings
    if ball.y + ball.radius >= HEIGHT:
        #if we hit the bottom of the ceiling
        BOUNCE_CHANNEL.play(BOUNCE_SOUND)
        ball.y_vel *= -1 
    elif ball.y - ball.radius <= 0:
        #if we hit the top of the ceiling
        ball.y_vel *= -1
        BOUNCE_CHANNEL.play(BOUNCE_SOUND)

    if ball.x_vel < 0:
        #left paddle
        if ball.y >= left_paddle.y and ball.y <= left_paddle.y + left_paddle.height:
            if ball.x - ball.radius <= left_paddle.x + left_paddle.width:
                #speeding up ball every time it hits the paddle
                ball.x_vel *= -1
                ball.x_vel += 0.5

                middle_y = left_paddle.y + left_paddle.height / 2
                difference_in_y = middle_y - ball.y
                reduction_factor = (left_paddle.height / 2) / ball.MAX_VEL
                y_vel = difference_in_y / reduction_factor
                ball.y_vel = -1 * y_vel
                BOUNCE_CHANNEL.play(BOUNCE_SOUND)

    else:
        #right paddle
        if ball.y >= right_paddle.y and ball.y <= right_paddle.y + right_paddle.height:
            if ball.x + ball.radius >= right_paddle.x:
                ball.x_vel *= -1
                ball.x_vel -= 0.5

                middle_y = right_paddle.y + right_paddle.height / 2
                difference_in_y = middle_y - ball.y
                reduction_factor = (left_paddle.height / 2) / ball.MAX_VEL
                y_vel = difference_in_y / reduction_factor
                ball.y_vel = -1 * y_vel
                BOUNCE_CHANNEL.play(BOUNCE_SOUND)


def handle_paddle_movement(keys, left_paddle, right_paddle):
    if keys[pygame.K_w] and left_paddle.y - left_paddle.VEL >= 0:
        left_paddle.move(up=True)
    if keys[pygame.K_s] and left_paddle.y + left_paddle.VEL + left_paddle.height <= HEIGHT:
        left_paddle.move(up=False)

    if keys[pygame.K_UP] and right_paddle.y - right_paddle.VEL >= 0:
        right_paddle.move(up=True)
    if keys[pygame.K_DOWN] and right_paddle.y + right_paddle.VEL + right_paddle.height <= HEIGHT:
        right_paddle.move(up=False)

def main():
    run = True
    clock = pygame.time.Clock()

    left_paddle = Paddle(10, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = Paddle(WIDTH - 10 - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)

    ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS)

    left_score = 0
    right_score = 0
    MUSIC_CHANNEL.play(BACKGROUND_MUSIC, loops=-1)
    
    while run: 
        clock.tick(FPS)
        draw(WIN,[left_paddle, right_paddle], ball, left_score, right_score)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        keys = pygame.key.get_pressed()
        handle_paddle_movement(keys, left_paddle, right_paddle)

        ball.move()
        handle_collision(ball, left_paddle, right_paddle)

        if ball.x < 0:
            right_score += 1
            left = True
            ball.reset(left)
            left_paddle.reset()
            right_paddle.reset()
            pygame.time.delay(1000)
        elif ball.x > WIDTH:
            left_score += 1
            left = False
            ball.reset(left)
            left_paddle.reset()
            right_paddle.reset()
            pygame.time.delay(1000)

        won = False
        if left_score >= WINNING_SCORE:
            won = True
            MUSIC_CHANNEL.stop()
            VICTORY_CHANNEL.play(VICTORY_MUSIC)
            win_text = "  Player  1 Wins!"
        elif right_score >= WINNING_SCORE:
            won = True
            MUSIC_CHANNEL.stop()
            VICTORY_CHANNEL.play(VICTORY_MUSIC)
            win_text = "  Player  2 Wins!"
        
        if won:
            text = SCORE_FONT.render(win_text, 1, WHITE)
            WIN.blit(text, (WIDTH // 2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
            pygame.display.update()
            pygame.time.delay(5000)
            ball.reset(True)
            left_paddle.reset()
            right_paddle.reset()
            left_score = 0
            right_score = 0
            MUSIC_CHANNEL.play(BACKGROUND_MUSIC, loops = -1)
            

    pygame.quit()

if __name__ == '__main__':
    main()