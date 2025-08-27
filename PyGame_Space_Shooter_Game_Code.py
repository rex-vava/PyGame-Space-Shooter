import pygame
import random
import math

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 100)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 50)
PURPLE = (180, 70, 255)

# Player class
class Player:
    def __init__(self):
        self.width = 40
        self.height = 50
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - self.height - 20
        self.speed = 5
        self.color = BLUE
        self.shoot_cooldown = 0
        self.health = 100
        
    def draw(self):
        # Draw player ship
        pygame.draw.polygon(screen, self.color, [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height)
        ])
        # Draw engine glow
        pygame.draw.polygon(screen, YELLOW, [
            (self.x + self.width // 2 - 5, self.y + self.height),
            (self.x + self.width // 2, self.y + self.height + 15),
            (self.x + self.width // 2 + 5, self.y + self.height)
        ])
        
    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > HEIGHT // 2:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < HEIGHT - self.height:
            self.y += self.speed
            
    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            
    def shoot(self, bullets):
        if self.shoot_cooldown == 0:
            bullets.append(Bullet(self.x + self.width // 2, self.y))
            self.shoot_cooldown = 15
            return True
        return False

# Bullet class
class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 4
        self.speed = 7
        self.color = GREEN
        
    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, WHITE, (self.x, self.y), self.radius - 2)
        
    def move(self):
        self.y -= self.speed
        
    def off_screen(self):
        return self.y < 0

# Enemy class
class Enemy:
    def __init__(self):
        self.size = random.randint(20, 40)
        self.x = random.randint(self.size, WIDTH - self.size)
        self.y = random.randint(-100, -self.size)
        self.speed = random.uniform(1.0, 3.0)
        self.color = random.choice([RED, PURPLE, YELLOW])
        self.points = 50 - self.size  # Smaller enemies are worth more points
        
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.size, self.size), 2)
        
    def move(self):
        self.y += self.speed
        
    def off_screen(self):
        return self.y > HEIGHT
        
    def collide_with_bullet(self, bullet):
        distance = math.sqrt((self.x + self.size/2 - bullet.x)**2 + (self.y + self.size/2 - bullet.y)**2)
        return distance < (self.size/2 + bullet.radius)
        
    def collide_with_player(self, player):
        return (self.x + self.size > player.x and 
                self.x < player.x + player.width and
                self.y + self.size > player.y and
                self.y < player.y + player.height)

# Star background class
class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.uniform(0.1, 2)
        self.speed = random.uniform(0.2, 1.0)
        
    def draw(self):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), self.size)
        
    def move(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

# Explosion effect class
class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 5
        self.max_radius = 30
        self.growing = True
        
    def draw(self):
        if self.growing:
            self.radius += 1
            if self.radius >= self.max_radius:
                self.growing = False
        else:
            self.radius -= 1
            
        pygame.draw.circle(screen, YELLOW, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, RED, (self.x, self.y), self.radius - 5)
        
    def finished(self):
        return self.radius <= 0

# Game setup
player = Player()
bullets = []
enemies = []
stars = [Star() for _ in range(100)]
explosions = []
score = 0
level = 1
enemy_spawn_timer = 0
game_over = False
font = pygame.font.SysFont(None, 36)

# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot(bullets)
            if event.key == pygame.K_r and game_over:
                # Reset game
                player = Player()
                bullets = []
                enemies = []
                explosions = []
                score = 0
                level = 1
                game_over = False
    
    if not game_over:
        # Player movement
        keys = pygame.key.get_pressed()
        player.move(keys)
        player.update()
        
        # Spawn enemies
        enemy_spawn_timer += 1
        if enemy_spawn_timer >= 60 - min(50, level * 5):  # Spawn rate increases with level
            enemies.append(Enemy())
            enemy_spawn_timer = 0
            
        # Update bullets
        for bullet in bullets[:]:
            bullet.move()
            if bullet.off_screen():
                bullets.remove(bullet)
                
        # Update enemies
        for enemy in enemies[:]:
            enemy.move()
            if enemy.off_screen():
                enemies.remove(enemy)
                
            # Check collision with bullets
            for bullet in bullets[:]:
                if enemy.collide_with_bullet(bullet):
                    explosions.append(Explosion(enemy.x + enemy.size//2, enemy.y + enemy.size//2))
                    score += enemy.points
                    enemies.remove(enemy)
                    bullets.remove(bullet)
                    break
                    
            # Check collision with player
            if enemy.collide_with_player(player):
                player.health -= 10
                explosions.append(Explosion(enemy.x + enemy.size//2, enemy.y + enemy.size//2))
                enemies.remove(enemy)
                if player.health <= 0:
                    game_over = True
        
        # Update stars
        for star in stars:
            star.move()
            
        # Update explosions
        for explosion in explosions[:]:
            if explosion.finished():
                explosions.remove(explosion)
                
        # Level up
        if score >= level * 1000:
            level += 1
    
    # Draw everything
    screen.fill(BLACK)
    
    # Draw stars
    for star in stars:
        star.draw()
    
    # Draw player
    player.draw()
    
    # Draw bullets
    for bullet in bullets:
        bullet.draw()
        
    # Draw enemies
    for enemy in enemies:
        enemy.draw()
        
    # Draw explosions
    for explosion in explosions:
        explosion.draw()
    
    # Draw HUD
    pygame.draw.rect(screen, (30, 30, 50), (0, 0, WIDTH, 40))
    score_text = font.render(f"Score: {score}", True, GREEN)
    level_text = font.render(f"Level: {level}", True, YELLOW)
    health_text = font.render(f"Health: {player.health}", True, RED)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, 10))
    screen.blit(health_text, (WIDTH - health_text.get_width() - 10, 10))
    
    # Draw game over screen
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        game_over_text = font.render("GAME OVER", True, RED)
        restart_text = font.render("Press R to Restart", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 20))
    
    # Draw controls help
    if not game_over:
        controls_text = font.render("Controls: Arrow Keys to Move, SPACE to Shoot", True, WHITE)
        screen.blit(controls_text, (WIDTH // 2 - controls_text.get_width() // 2, HEIGHT - 40))
    
    # Update display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(60)

pygame.quit()
