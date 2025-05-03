import pygame
import random
import math
from collections import deque

# Initialize
pygame.init()
W, H, C = 20, 15, 40  # Larger cells for better graphics
FPS = 8
scr = pygame.display.set_mode((W*C, H*C+100))
pygame.display.set_caption("Garden Snake Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 20)

# Colors
GRASS_GREEN = (100, 200, 50)
DIRT_BROWN = (139, 69, 19)
SKY_BLUE = (135, 206, 235)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SNAKE_GREEN = (50, 200, 50)
APPLE_RED = (255, 50, 50)
APPLE_LEAF = (50, 150, 50)
WALL_GRAY = (100, 100, 100)

# Load graphics
def create_apple_surface(size):
    apple = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(apple, APPLE_RED, (size//2, size//2), size//2 - 2)
    # Draw leaf
    leaf_points = [(size//3, size//4), (size//2+5, size//6), (size//2+10, size//4)]
    pygame.draw.polygon(apple, APPLE_LEAF, leaf_points)
    # Draw stem
    pygame.draw.line(apple, (100, 80, 50), (size//2, size//4), (size//2, size//8), 2)
    return apple

def create_grass_tile(size):
    tile = pygame.Surface((size, size))
    tile.fill(GRASS_GREEN)
    # Draw some grass blades
    for _ in range(10):
        x = random.randint(0, size)
        height = random.randint(3, 8)
        pygame.draw.line(tile, (random.randint(150, 200), random.randint(200, 255), random.randint(50, 100)), 
                        (x, size), (x, size-height), 1)
    return tile

# Create graphics surfaces
apple_img = create_apple_surface(C)
grass_tile = create_grass_tile(C)

class SnakeGame:
    def __init__(self):
        self.snake = [(W//2, H//2)]
        self.walls = [(random.randint(0,W-1), random.randint(0,H-1)) for _ in range(5)]
        self.animation_frame = 0
        self.reset()
        
    def reset(self):
        self.snake = [(W//2, H//2)]
        self.dir = (1, 0)
        self.score = 0
        self.food = self.new_food()
        self.game_over = False
        self.auto = False
        self.animation_frame = 0
    
    def new_food(self):
        while True:
            f = (random.randint(0,W-1), random.randint(0,H-1))
            if f not in self.snake and f not in self.walls:
                return f
    
    def move(self):
        if self.game_over: return
        
        head = ((self.snake[0][0]+self.dir[0])%W, (self.snake[0][1]+self.dir[1])%H)
        if head in self.walls or head in self.snake[:-1]:
            self.game_over = True
            return
            
        self.snake.insert(0, head)
        if head == self.food:
            self.score += 1
            self.food = self.new_food()
            self.animation_frame = 10
        else:
            self.snake.pop()
    
    def bfs_path(self):
        start, target = self.snake[0], self.food
        visited = set()
        q = deque([(start, [])])
        
        while q:
            p, path = q.popleft()
            if p == target: 
                return path
            if p in visited: 
                continue
            visited.add(p)
            
            for d in [(1,0), (-1,0), (0,1), (0,-1)]:
                n = ((p[0]+d[0])%W, (p[1]+d[1])%H)
                if n not in self.snake[:-1] and n not in self.walls:
                    q.append((n, path+[d]))
        return []
    
    def auto_move(self):
        if not hasattr(self, 'path') or not self.path:
            self.path = self.bfs_path()
        if self.path:
            self.dir = self.path.pop(0)
        self.move()
    
    def draw_animated_snake(self):
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 0.2 + 0.8
        
        for i, (x,y) in enumerate(self.snake):
            size_factor = 1.0
            if i == 0:  # Head
                size_factor = 1.1 if self.animation_frame > 0 else 1.0
                color = (min(255, SNAKE_GREEN[0] + 50), SNAKE_GREEN[1], SNAKE_GREEN[2])
            else:
                wave = math.sin(pygame.time.get_ticks() * 0.01 - i * 0.5) * 0.1
                size_factor = 0.9 + wave
                color = (SNAKE_GREEN[0], SNAKE_GREEN[1] - 30, SNAKE_GREEN[2])
            
            size = int(C * size_factor)
            offset = (C - size) // 2
            rect = pygame.Rect(x*C + offset, y*C + offset, size, size)
            pygame.draw.rect(scr, color, rect, border_radius=size//4)
            
            if i == 0:  # Draw eyes on head
                eye_size = C // 8
                dir_x, dir_y = self.dir
                if dir_x == 1:  # Right
                    eye_positions = [
                        (x*C + C - eye_size*2, y*C + eye_size*2),
                        (x*C + C - eye_size*2, y*C + C - eye_size*2)
                    ]
                elif dir_x == -1:  # Left
                    eye_positions = [
                        (x*C + eye_size*2, y*C + eye_size*2),
                        (x*C + eye_size*2, y*C + C - eye_size*2)
                    ]
                elif dir_y == -1:  # Up
                    eye_positions = [
                        (x*C + eye_size*2, y*C + eye_size*2),
                        (x*C + C - eye_size*2, y*C + eye_size*2)
                    ]
                else:  # Down
                    eye_positions = [
                        (x*C + eye_size*2, y*C + C - eye_size*2),
                        (x*C + C - eye_size*2, y*C + C - eye_size*2)
                    ]
                
                for ex, ey in eye_positions:
                    pygame.draw.circle(scr, WHITE, (ex, ey), eye_size)
                    pygame.draw.circle(scr, BLACK, (ex, ey), eye_size//2)
        
        if self.animation_frame > 0:
            self.animation_frame -= 1
    
    def draw(self):
        # Draw garden background
        for x in range(W):
            for y in range(H):
                scr.blit(grass_tile, (x*C, y*C))
        
        # Draw sky background at top
        pygame.draw.rect(scr, SKY_BLUE, (0, 0, W*C, C))
        
        # Draw walls (rocks)
        for wall in self.walls:
            pygame.draw.rect(scr, WALL_GRAY, (wall[0]*C, wall[1]*C, C, C), border_radius=5)
            # Add some rock texture
            for _ in range(5):
                px = wall[0]*C + random.randint(5, C-5)
                py = wall[1]*C + random.randint(5, C-5)
                pygame.draw.circle(scr, (WALL_GRAY[0]-20, WALL_GRAY[1]-20, WALL_GRAY[2]-20), (px, py), random.randint(1, 3))
        
        # Draw apple
        pulse_size = math.sin(pygame.time.get_ticks() * 0.005) * 5 + C
        scaled_apple = pygame.transform.scale(apple_img, (int(pulse_size), int(pulse_size)))
        scr.blit(scaled_apple, (self.food[0]*C + (C - pulse_size)/2, self.food[1]*C + (C - pulse_size)/2))
        
        # Draw snake
        self.draw_animated_snake()
        
        # Draw UI panel
        pygame.draw.rect(scr, DIRT_BROWN, (0, H*C, W*C, 100))
        
        # Draw UI text
        mode_color = (255, 255, 100) if self.auto else WHITE
        scr.blit(font.render(f"Apples Collected: {self.score}", 1, WHITE), (10, H*C+10))
        scr.blit(font.render(f"Mode: {'AUTO' if self.auto else 'MANUAL'}", 1, mode_color), (10, H*C+40))
        scr.blit(font.render("SPACE: Toggle Auto | ENTER: Restart | ESC: Stop Auto", 1, WHITE), (10, H*C+70))
        
        if self.game_over:
            s = pygame.Surface((W*C,H*C), pygame.SRCALPHA)
            s.fill((0,0,0,180))
            scr.blit(s, (0,0))
            scr.blit(font.render("GAME OVER! Press ENTER", 1, WHITE), (W*C//2-100, H*C//2))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_RETURN:
                        self.reset()
                    elif e.key == pygame.K_ESCAPE and self.auto:
                        self.auto = False
                    elif not self.auto and not self.game_over:
                        if e.key == pygame.K_UP: self.dir = (0,-1)
                        elif e.key == pygame.K_DOWN: self.dir = (0,1)
                        elif e.key == pygame.K_LEFT: self.dir = (-1,0)
                        elif e.key == pygame.K_RIGHT: self.dir = (1,0)
                    if e.key == pygame.K_SPACE:
                        self.auto = not self.auto
            
            if not self.game_over:
                if self.auto:
                    self.auto_move()
                else:
                    self.move()
            
            self.draw()
            clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    SnakeGame().run()
