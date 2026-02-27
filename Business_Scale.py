#Importing necessary Libraries
import pygame
import random
import math

#CONSTANTS
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

#Physics CONSTANTS
ACCELERATION = 1.0
FRICTION = -0.12
GRAVITY = 0.8
JUMP_FORCE = -17
DOUBLE_JUMP_THRESHOLD = 100  #After (100) points, you unlock a double jump.

#Colors
BG_COLOR = (20, 24, 35) #Very Dark Grey w/ a Blue Tint.
GRID_COLOR = (40, 50, 65) #Gray
PLAYER_COLOR = (0, 255, 150) #Neon Green
PLAYER_ACCENT = (255, 255, 255) #White
WHITE = (255, 255, 255) #White
PLATFORM_COLOR = (70, 130, 180) #Steel Blue
ENEMY_COLOR = (255, 60, 60) #Volatility Red
GOLD_COLOR = (255, 215, 0) #Multiplier Gold
TEXT_COLOR = (220, 220, 220) #Slightly Darker White


#SFX/Music
pygame.mixer.init()

jump_sound = pygame.mixer.Sound("Music/Jump_M.wav")
lose_life_sound = pygame.mixer.Sound("Music/LoseLife_M.wav")
lose_sound = pygame.mixer.Sound("Music/Lose_M.wav")
platform_sound = pygame.mixer.Sound("Music/Platform_M.wav")
powerup_sound = pygame.mixer.Sound("Music/Powerup_M.wav")

pygame.mixer.music.load("Music/BG_M.wav")
pygame.mixer.music.play(-1)

class Particle(pygame.sprite.Sprite):
    #Explosion Particles
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((6, 6))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vel_x = random.uniform(-4, 4)
        self.vel_y = random.uniform(-4, 4)
        self.life = 30 #Frames to live

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.life -= 1
        if self.life <= 0:
            self.kill()
        self.image.set_alpha(int((self.life / 30) * 255))

class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.image = pygame.Surface((40, 40))
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        
        #Physics Vectors
        self.pos = pygame.math.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        
        #In-Game Actions
        self.jump_count = 0  #Tracks Jumps (0, 1, or 2)
        self.multiplier_timer = 0
        self.lives = 3
        self.score = 0

    def reset(self):
        #Reset Player State for Game Restarting
        self.pos = pygame.math.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.jump_count = 0  #Reset Jumps
        self.multiplier_timer = 0
        self.lives = 3
        self.score = 0

    def update(self):
        #Physics Calculation
        self.acc = pygame.math.Vector2(0, GRAVITY)
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            self.acc.x = -ACCELERATION
        if keys[pygame.K_RIGHT]:
            self.acc.x = ACCELERATION

        # Add Friction
        self.acc.x += self.vel.x * FRICTION
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        # Stop at X (edges)
        if self.pos.x > SCREEN_WIDTH:
            self.pos.x = SCREEN_WIDTH
        if self.pos.x < 0:
            self.pos.x = 0

        # Update Rect
        self.rect.midbottom = self.pos

        # Multiplier Timer (5 seconds, so 300 frames)
        if self.multiplier_timer > 0:
            self.multiplier_timer -= 1
            if self.multiplier_timer % 10 < 5:
                self.image.fill(GOLD_COLOR)
            else:
                self.image.fill(PLAYER_COLOR)
        else:
            self.image.fill(PLAYER_COLOR)

    def jump(self):
        # Check collision with Ground just to see if we are grounded
        self.rect.y += 2
        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.y -= 2
        
        #If on ground, reset count. 
        if hits:
            self.jump_count = 0

#MC-12
        #Normal Jump
        if self.jump_count == 0:
            jump_sound.play()
            self.vel.y = JUMP_FORCE
            self.jump_count = 1
            
        #Double Jump (When Unlocked)
        elif self.jump_count == 1 and self.score >= DOUBLE_JUMP_THRESHOLD:
            jump_sound.play()
            self.vel.y = JUMP_FORCE
            self.jump_count = 2 #2 means that we jumped twice.
            
            # Create particle effect for double jump (White explosion)
            for _ in range(15):
                self.game.particles.add(Particle(self.rect.centerx, self.rect.bottom, WHITE))

    def bounce(self):
        #Effects from Stomping Enemies
        jump_sound.play()

        #MC-10 \/
        #powerup_sound.play()

        self.vel.y = -20 #Small Hop
        self.multiplier_timer = 300 #5 Seconds (300/FPS)
        
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width):
        super().__init__()
        self.image = pygame.Surface((width, 18))
        self.image.fill(PLATFORM_COLOR)

        #Making a Line on top of each Platform for Polish
        pygame.draw.rect(self.image, (150, 200, 255), (0,0,width, 4))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.passed = False

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Draw an Enemy (Just a Square but rotated 45*)
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, ENEMY_COLOR, [(20,0), (40,20), (20,40), (0,20)])
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, SCREEN_WIDTH - 40)
        self.rect.y = -50
        self.speed_y = random.randint(3, 7)

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Business Scale (From KPI Dashboard: Market Action Platformer)")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Consolas", 20, bold=True)
        self.running = True
        self.game_state = "PLAYING"  #PLAYING or GAMEOVER
        
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        
        self.player = Player(self)
        self.all_sprites.add(self.player)
        
        self.shake_timer = 0
        self.spawn_timer = 0
        self.start_game()

    def start_game(self):
        #Clear existing Sprites first (Restart Game)
        self.platforms.empty()
        self.enemies.empty()
        self.particles.empty()
        self.all_sprites.empty()
        
        #Re-Add Player
        self.all_sprites.add(self.player)
        
        #Initial Platforms
        p = Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH)
        self.platforms.add(p)
        self.all_sprites.add(p)
        for i in range(1, 8):
            p = Platform(random.randrange(0, SCREEN_WIDTH - 100), SCREEN_HEIGHT - (i * 100), 120)
            self.platforms.add(p)
            self.all_sprites.add(p)

    def reset_game(self):
        #Fully reset game state for restart
        self.player.reset()
        self.start_game()
        self.spawn_timer = 0
        self.shake_timer = 0
        self.game_state = "PLAYING"

    def draw_grid(self):
        #Draw Grid Lines to look like a Chart
        for x in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))

    def screen_shake(self):
        if self.shake_timer > 0:
            self.shake_timer -= 1
            offset_x = random.randint(-4, 4)
            offset_y = random.randint(-4, 4)
            return offset_x, offset_y
        return 0, 0

    def run(self):
        while self.running:
            self.events()
            if self.game_state == "PLAYING":
                self.update()
            self.draw()
            self.clock.tick(FPS)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if self.game_state == "PLAYING" and event.key == pygame.K_SPACE:
                    self.player.jump()
                if self.game_state == "GAMEOVER" and event.key == pygame.K_r:
                    self.reset_game()

    def update(self):
        self.all_sprites.update()
        self.particles.update()

        #Camera Scroll (Infinite Climb)
        if self.player.rect.top <= SCREEN_HEIGHT / 4:
            self.player.pos.y += abs(self.player.vel.y)
            for p in self.platforms:
                p.rect.y += abs(self.player.vel.y)
                if p.rect.top >= SCREEN_HEIGHT:
                    p.kill()
            for e in self.enemies:
                e.rect.y += abs(self.player.vel.y)
            
            #Spawn New Platforms
            while len(self.platforms) < 8:
                width = random.randint(80, 150)
                p = Platform(random.randint(0, SCREEN_WIDTH - width), -30, width)
                self.platforms.add(p)
                self.all_sprites.add(p)

        #Platform Collisions (Landing)
        if self.player.vel.y > 0:
            hits = pygame.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                for platform in hits:
                    if (self.player.rect.bottom >= platform.rect.top and 
                        self.player.rect.bottom <= platform.rect.top + 15 and
                        self.player.vel.y > 0):
                        
                        self.player.pos.y = platform.rect.top
                        self.player.vel.y = 0
                        self.player.jump_count = 0  #Reset Jump Count when Grounded.
                        
                        if not platform.passed:
                            mult = 2 if self.player.multiplier_timer > 0 else 1
                            self.player.score += (10 * mult)

                            if mult == 0:
                                pass
                            else:
                                platform_sound.play()

                            platform.passed = True
                        break

        #Defeat Enemy
        enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for enemy in enemy_hits:
            #Check if hitting from top (Stomp, or when player velocity is falling)
            if self.player.vel.y > 0 and self.player.rect.bottom < enemy.rect.centery + 10:
                enemy.kill()
                self.player.bounce()
                for _ in range(15):
                    self.particles.add(Particle(enemy.rect.centerx, enemy.rect.centery, ENEMY_COLOR))
            else:
                self.player.lives -= 1
                self.shake_timer = 10
                self.player.pos = pygame.math.Vector2(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
                self.player.vel = pygame.math.Vector2(0, 0)
                self.enemies.empty() 

        #Spawning Enemies
        self.spawn_timer += 1
        if self.spawn_timer >= 110:
            e = Enemy()
            self.enemies.add(e)
            self.all_sprites.add(e)
            self.spawn_timer = 0

        #Fall Off Screen
        if self.player.rect.top > SCREEN_HEIGHT:
            lose_life_sound.play()
            self.player.lives -= 1
            self.shake_timer = 10
            self.player.pos = pygame.math.Vector2(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
            self.player.vel = pygame.math.Vector2(0, 0)
            p = Platform(self.player.rect.x - 50, self.player.rect.y + 60, 200)
            self.platforms.add(p)
            self.all_sprites.add(p)

        #Check Game Over
        if self.player.lives <= 0:
            lose_sound.play()
            self.game_state = "GAMEOVER"

    def draw(self):
        ox, oy = self.screen_shake()
        self.screen.fill(BG_COLOR)
        self.draw_grid()

        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, (sprite.rect.x + ox, sprite.rect.y + oy))
        for p in self.particles:
            self.screen.blit(p.image, (p.rect.x + ox, p.rect.y + oy))

        #UI at Top of Screen
        pygame.draw.rect(self.screen, (30, 30, 40), (0, 0, SCREEN_WIDTH, 60))
        pygame.draw.line(self.screen, WHITE, (0, 60), (SCREEN_WIDTH, 60), 2)

        score_surf = self.font.render(f"REVENUE (SCORE): ${self.player.score}k", True, PLAYER_ACCENT)
        self.screen.blit(score_surf, (20, 20))

        lives_color = PLAYER_ACCENT if self.player.lives > 1 else ENEMY_COLOR
        lives_surf = self.font.render(f"CAPITAL (LIVES): {self.player.lives}", True, lives_color)
        self.screen.blit(lives_surf, (300, 20))

        # Show if Double Jump is Unlocked
        if self.player.score >= DOUBLE_JUMP_THRESHOLD:
            dj_status = "UNLOCKED"
            dj_color = GOLD_COLOR
        else:
            dj_status = f"LOCKED (<{DOUBLE_JUMP_THRESHOLD})"
            dj_color = (100, 100, 100)
            
        dj_surf = self.font.render(f"DOUBLE JUMP: {dj_status}", True, dj_color)
        self.screen.blit(dj_surf, (515, 40)) #Positioned below Multiplier

        if self.player.multiplier_timer > 0:
            mult_surf = self.font.render("MARKET BOOM: 2X ACTIVE!", True, GOLD_COLOR)
            self.screen.blit(mult_surf, (550, 10))

        if self.game_state == "GAMEOVER":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            go_surf = self.font.render("INSOLVENT! GAME OVER", True, ENEMY_COLOR)
            restart_surf = self.font.render("PRESS 'R' TO RESTART", True, WHITE)
            self.screen.blit(go_surf, (SCREEN_WIDTH//2 - go_surf.get_width()//2, SCREEN_HEIGHT//2 - 30))
            self.screen.blit(restart_surf, (SCREEN_WIDTH//2 - restart_surf.get_width()//2, SCREEN_HEIGHT//2 + 10))

        pygame.display.flip()

#Run the Game
if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()



#--------------------
#README Paragraph:
#Business Scale is a Finance-themed Infinite Climber we built.
#You climb a Market Grid to grow your Score (Revenue) while not losing your Lives (Capital). 
#Avoid or Stomp on Red Enemies to survive, and jumping on Enemies triggers a Market Boom for Double Points!
#Reaching 100 (100K Revenue) points unlocks a Double Jump.
#The goal is to scale the business as high as possible until you lose all your Lives (Capital).
#--------------------



#--------------------
#Resources:
#Audio from "Scratch.mit.edu"
#--------------------



#--------------------
#Student Reflections:
# This project was stressful, but with a partner, it wasn't so bad.
# I thought that my partner was very helpful. 
# He AI'd some hard coding structure, but he wasn't too bad himself with the code. 
# He coded the music code using the resources (audio files) I gave him, from Scratch.mit.edu
# I coded the player to fix collisions, add polish, enemy speed, double jump physics, fixed the UI at the top of the screen, and helped with the colors.
#--------------------