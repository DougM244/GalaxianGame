import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import os
import json
from menu import show_menu, show_game_over, show_shop
from boss import Boss, BOSS_CONFIGS

WIDTH, HEIGHT = 800, 600
SHIP_WIDTH, SHIP_HEIGHT = 60, 20
ALIEN_WIDTH, ALIEN_HEIGHT = 40, 20
BULLET_WIDTH, BULLET_HEIGHT = 5, 10
POWERUP_SIZE = 32

NUM_STARS = 100

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(1, 3)
        self.size = random.uniform(1, 2)
        self.color = (random.random(), random.random(), random.random())

    def update(self):
        self.y -= self.speed
        if self.y < 0:
            self.y = HEIGHT
            self.x = random.randint(0, WIDTH)

    def draw(self):
        glPointSize(self.size)
        glColor3f(*self.color)
        glBegin(GL_POINTS)
        glVertex2f(self.x, self.y)
        glEnd()

def draw_tiled_bg(tex_id, tw, th):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glColor3f(1, 1, 1)
    for x in range(0, WIDTH, tw):
        for y in range(0, HEIGHT, th):
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(x, y)
            glTexCoord2f(1, 0); glVertex2f(x + tw, y)
            glTexCoord2f(1, 1); glVertex2f(x + tw, y + th)
            glTexCoord2f(0, 1); glVertex2f(x, y + th)
            glEnd()
    glDisable(GL_TEXTURE_2D)

def draw_num(x, y, num, textures):
    for digit in str(num):
        idx = int(digit)
        tex = textures[idx]
        if tex:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, tex[0])
            glColor4f(1, 1, 1, 1)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(x, y)
            glTexCoord2f(1, 0); glVertex2f(x + tex[1], y)
            glTexCoord2f(1, 1); glVertex2f(x + tex[1], y + tex[2])
            glTexCoord2f(0, 1); glVertex2f(x, y + tex[2])
            glEnd()
            glDisable(GL_TEXTURE_2D)
            glDisable(GL_BLEND)
            x += tex[1] + 2

class Ship:
    def __init__(self, texture=None, tex_w=60, tex_h=60, bullet_texture=None, bullet_tex_w=16, bullet_tex_h=16):
        self.x = WIDTH // 2
        self.y = 40
        self.lives = 3
        self.score = 0
        self.coins = 0
        self.bullets = []
        self.cooldown = 0
        self.texture = texture
        self.tex_w = tex_w
        self.tex_h = tex_h
        self.bullet_texture = bullet_texture
        self.bullet_tex_w = bullet_tex_w
        self.bullet_tex_h = bullet_tex_h
        self.som_tiro = None
        self.speed = 5
        self.fire_rate = 10
        self.powerups = {
            "speed": {"active": False, "timer": 0, "duration": 300},
            "shield": {"active": False, "timer": 0, "duration": 300},
            "double_shot": {"active": False, "timer": 0, "duration": 300}
        }
        self.initial_speed = self.speed
        self.initial_fire_rate = self.fire_rate
        self.shield_texture = None

    def move(self, dx):
        self.x += dx * self.speed
        self.x = max(SHIP_WIDTH//2, min(WIDTH-SHIP_WIDTH//2, self.x))

    def shoot(self):
        if self.cooldown == 0:
            if self.powerups["double_shot"]["active"]:
                self.bullets.append([self.x - 10, self.y + SHIP_HEIGHT//2])
                self.bullets.append([self.x + 10, self.y + SHIP_HEIGHT//2])
            else:
                self.bullets.append([self.x, self.y + SHIP_HEIGHT//2])
            self.cooldown = self.fire_rate
            if self.som_tiro:
                self.som_tiro.play()

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1
        for b in self.bullets:
            b[1] += 5
        self.bullets = [b for b in self.bullets if b[1] < HEIGHT]

        for pu_type in self.powerups:
            if self.powerups[pu_type]["active"]:
                self.powerups[pu_type]["timer"] -= 1
                if self.powerups[pu_type]["timer"] <= 0:
                    self.deactivate_powerup(pu_type)
        
    def activate_powerup(self, pu_type):
        if pu_type == "speed":
            self.powerups["speed"]["active"] = True
            self.powerups["speed"]["timer"] = self.powerups["speed"]["duration"]
            self.speed = self.initial_speed * 1.5
        elif pu_type == "shield":
            self.powerups["shield"]["active"] = True
            self.powerups["shield"]["timer"] = self.powerups["shield"]["duration"]
        elif pu_type == "double_shot":
            self.powerups["double_shot"]["active"] = True
            self.powerups["double_shot"]["timer"] = self.powerups["double_shot"]["duration"]
            self.fire_rate = self.initial_fire_rate // 2

    def deactivate_powerup(self, pu_type):
        self.powerups[pu_type]["active"] = False
        if pu_type == "speed":
            self.speed = self.initial_speed
        elif pu_type == "double_shot":
            self.fire_rate = self.initial_fire_rate

    def draw(self, is_lit):
        if self.texture:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture)
            color_factor = 1.0 if is_lit else 0.5
            glColor3f(color_factor, color_factor, color_factor)
            x = self.x - self.tex_w // 2
            y = self.y - self.tex_h // 2
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(x, y)
            glTexCoord2f(1, 0); glVertex2f(x + self.tex_w, y)
            glTexCoord2f(1, 1); glVertex2f(x + self.tex_w, y + self.tex_h)
            glTexCoord2f(0, 1); glVertex2f(x, y + self.tex_h)
            glEnd()
            glDisable(GL_TEXTURE_2D)
        else:
            glColor3f(0, 1, 1)
            glRectf(self.x-SHIP_WIDTH//2, self.y-SHIP_HEIGHT//2, self.x+SHIP_WIDTH//2, self.y+SHIP_HEIGHT//2)
        
        if self.powerups["shield"]["active"] and self.shield_texture:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.shield_texture[0])
            glColor4f(1, 1, 1, 1)
            shield_size = 80
            sx = self.x - shield_size / 2
            sy = self.y - shield_size / 2
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(sx, sy)
            glTexCoord2f(1, 0); glVertex2f(sx + shield_size, sy)
            glTexCoord2f(1, 1); glVertex2f(sx + shield_size, sy + shield_size)
            glTexCoord2f(0, 1); glVertex2f(sx, sy + shield_size)
            glEnd()
            glDisable(GL_TEXTURE_2D)
            glDisable(GL_BLEND)

        for b in self.bullets:
            if self.bullet_texture:
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, self.bullet_texture)
                glColor4f(1, 1, 1, 1)
                bx = b[0] - self.bullet_tex_w // 2
                by = b[1]
                glBegin(GL_QUADS)
                glTexCoord2f(0, 0); glVertex2f(bx, by)
                glTexCoord2f(1, 0); glVertex2f(bx + self.bullet_tex_w, by)
                glTexCoord2f(1, 1); glVertex2f(bx + self.bullet_tex_w, by + self.bullet_tex_h)
                glTexCoord2f(0, 1); glVertex2f(bx, by + self.bullet_tex_h)
                glEnd()
                glDisable(GL_TEXTURE_2D)
                glDisable(GL_BLEND)
            else:
                glColor3f(1, 1, 0)
                glRectf(b[0]-BULLET_WIDTH//2, b[1], b[0]+BULLET_WIDTH//2, b[1]+BULLET_HEIGHT)

class Alien:
    def __init__(self, x, y, texture=None, tex_w=40, tex_h=20, bullet_texture=None, bullet_tex_w=16, bullet_tex_h=16):
        self.x = x
        self.y = y
        self.alive = True
        self.attacking = False
        self.bullet = None
        self.texture = texture
        self.tex_w = tex_w
        self.tex_h = tex_h
        self.bullet_texture = bullet_texture
        self.bullet_tex_w = bullet_tex_w
        self.bullet_tex_h = bullet_tex_h
        self.som_tiro = None

    def attack(self):
        self.attacking = True
        self.bullet = [self.x, self.y-ALIEN_HEIGHT//2]
        if self.som_tiro:
            self.som_tiro.play()

    def update(self):
        if self.attacking and self.bullet:
            self.bullet[1] -= 4
            if self.bullet[1] < 0:
                self.attacking = False
                self.bullet = None

    def draw(self, is_lit):
        if self.alive:
            if self.texture:
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, self.texture)
                color_factor = 1.0 if is_lit else 0.5
                glColor3f(color_factor, color_factor, color_factor)
                x = self.x - self.tex_w // 2
                y = self.y - self.tex_h // 2
                glBegin(GL_QUADS)
                glTexCoord2f(0, 0); glVertex2f(x, y)
                glTexCoord2f(1, 0); glVertex2f(x + self.tex_w, y)
                glTexCoord2f(1, 1); glVertex2f(x + self.tex_w, y + self.tex_h)
                glTexCoord2f(0, 1); glVertex2f(x, y + self.tex_h)
                glEnd()
                glDisable(GL_TEXTURE_2D)
            else:
                glColor3f(1, 0, 0)
                glRectf(self.x-ALIEN_WIDTH//2, self.y-ALIEN_HEIGHT//2, self.x+ALIEN_WIDTH//2, self.y+ALIEN_HEIGHT//2)
        if self.attacking and self.bullet:
            if self.bullet_texture:
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, self.bullet_texture)
                glColor4f(1, 1, 1, 1)
                bx = self.bullet[0] - self.bullet_tex_w // 2
                by = self.bullet[1]
                glBegin(GL_QUADS)
                glTexCoord2f(0, 0); glVertex2f(bx, by)
                glTexCoord2f(1, 0); glVertex2f(bx + self.bullet_tex_w, by)
                glTexCoord2f(1, 1); glVertex2f(bx + self.bullet_tex_w, by + self.bullet_tex_h)
                glTexCoord2f(0, 1); glVertex2f(bx, by + self.bullet_tex_h)
                glEnd()
                glDisable(GL_TEXTURE_2D)
                glDisable(GL_BLEND)
            else:
                glColor3f(1, 1, 1)
                glRectf(self.bullet[0]-BULLET_WIDTH//2, self.bullet[1], self.bullet[0]+BULLET_WIDTH//2, self.bullet[1]+BULLET_HEIGHT)

class PowerUp:
    def __init__(self, x, y, pu_type, texture):
        self.x = x
        self.y = y
        self.pu_type = pu_type
        self.texture = texture
        self.size = POWERUP_SIZE

    def update(self):
        self.y -= 1

    def draw(self):
        if self.texture:
            glEnable(GL_TEXTURE_2D)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glBindTexture(GL_TEXTURE_2D, self.texture[0])
            glColor4f(1, 1, 1, 1)
            x = self.x - self.size // 2
            y = self.y - self.size // 2
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(x, y)
            glTexCoord2f(1, 0); glVertex2f(x + self.size, y)
            glTexCoord2f(1, 1); glVertex2f(x + self.size, y + self.size)
            glTexCoord2f(0, 1); glVertex2f(x, y + self.size)
            glEnd()
            glDisable(GL_TEXTURE_2D)
            glDisable(GL_BLEND)

def draw_text(x, y, text, size=24):
    font = pygame.font.SysFont('Arial', size)
    text_surface = font.render(text, True, (255,255,255), (0,0,0))
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    glRasterPos2i(x, HEIGHT - y - text_surface.get_height())
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

def load_texture(filename, size=None):
    if not os.path.exists(filename):
        print(f"Erro: Arquivo de textura não encontrado: {filename}")
        return None
    img = pygame.image.load(filename).convert_alpha()
    if size:
        img = pygame.transform.smoothscale(img, size)
    img_data = pygame.image.tostring(img, "RGBA", True)
    width, height = img.get_size()
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    return tex_id, width, height

def save_highscores(scores):
    with open('highscores.json', 'w') as f:
        json.dump(scores, f)

def load_highscores():
    if os.path.exists('highscores.json'):
        with open('highscores.json', 'r') as f:
            return json.load(f)
    return []

def save_player_data(data):
    with open('player_data.json', 'w') as f:
        json.dump(data, f, indent=4)

def load_player_data():
    if os.path.exists('player_data.json'):
        with open('player_data.json', 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("player_data.json está vazio ou corrompido. Criando novo arquivo...")
    
    default_data = {"coins": 0, "current_ship": "nave.png", "unlocked_ships": ["nave.png"]}
    save_player_data(default_data)
    return default_data

def enter_initials_screen(bg_texture, clock, score):
    initials = ['A', 'A', 'A']
    selected_char = 0
    run_initials = True

    while run_initials:
        for event in pygame.event.get():
            if event.type == QUIT:
                return "quit", score
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    highscores = load_highscores()
                    highscores.append({'initials': ''.join(initials), 'score': score})
                    highscores.sort(key=lambda x: x['score'], reverse=True)
                    highscores = highscores[:10]
                    save_highscores(highscores)
                    return "game_over", score
                if event.key == K_LEFT:
                    selected_char = (selected_char - 1) % 3
                if event.key == K_RIGHT:
                    selected_char = (selected_char + 1) % 3
                if event.key == K_UP:
                    char_code = ord(initials[selected_char])
                    char_code = char_code + 1 if char_code < ord('Z') else ord('A')
                    initials[selected_char] = chr(char_code)
                if event.key == K_DOWN:
                    char_code = ord(initials[selected_char])
                    char_code = char_code - 1 if char_code > ord('A') else ord('Z')
                    initials[selected_char] = chr(char_code)
        
        glClear(GL_COLOR_BUFFER_BIT)
        if bg_texture:
            draw_tiled_bg(bg_texture[0], bg_texture[1], bg_texture[2])

        draw_text(WIDTH // 2 - 160, HEIGHT // 2 - 100, "NEW HIGHSCORE!", size=48)
        draw_text(WIDTH // 2 - 100, HEIGHT // 2 - 40, "Enter your initials:", size=24)
        draw_text(WIDTH // 2 - 50, HEIGHT // 2 + 10, "".join(initials), size=48)
        
        x_pos_cursor = (WIDTH // 2 - 50) + (selected_char * 35)
        draw_text(x_pos_cursor, HEIGHT // 2 + 50, "_", size=48)

        pygame.display.flip()
        clock.tick(30)
        
    
def get_text_width(text, size=24):
    font = pygame.font.SysFont('Arial', size)
    text_surface = font.render(text, True, (255,255,255))
    return text_surface.get_width()

def draw_button(x, y, text, size=24, color=(255, 255, 255)):
    font = pygame.font.SysFont('Arial', size)
    text_surface = font.render(text, True, color)
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    width, height = text_surface.get_size()
    
    glRasterPos2i(x, HEIGHT - y - height)
    glDrawPixels(width, height, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
    
    return pygame.Rect(x, y, width, height)

def run_game(bg_texture, vidas_texture, ship_texture_data, alien_textures, bullet_ship_tex, bullet_alien_tex, numeros_texture, ship_attributes, powerup_textures, shield_texture):
    pygame.mixer.music.load('musica.mp3')
    pygame.mixer.music.play(-1)

    som_tiro = pygame.mixer.Sound('tiro.mp3')
    som_tiro_alien = pygame.mixer.Sound('tiro_alien.mp3')
    som_explosao = pygame.mixer.Sound('explosao.mp3')
    som_perde_vida = pygame.mixer.Sound('perde_vida.mp3')

    ship = Ship(texture=ship_texture_data[0], tex_w=ship_texture_data[1], tex_h=ship_texture_data[2],
                bullet_texture=bullet_ship_tex[0] if bullet_ship_tex else None,
                bullet_tex_w=bullet_ship_tex[1] if bullet_ship_tex else 16,
                bullet_tex_h=bullet_ship_tex[2] if bullet_ship_tex else 16)
    
    ship.lives = ship_attributes["lives"]
    ship.speed = ship_attributes["speed"]
    ship.initial_speed = ship.speed
    ship.fire_rate = ship_attributes["fire_rate"]
    ship.initial_fire_rate = ship.fire_rate
    ship.som_tiro = som_tiro
    ship.shield_texture = shield_texture

    aliens = []
    powerups = []
    linhas = 5
    base = 5
    espacamento_x = 60
    espacamento_y = 40
    boss = None
    paused = False
    
    powerup_spawn_counter = 0
    powerup_spawn_threshold = random.randint(10, 30)

    for l in range(linhas):
        n_aliens = base + l
        largura_total = (n_aliens-1) * espacamento_x
        y = HEIGHT - 60 - l*espacamento_y
        for i in range(n_aliens):
            x = WIDTH//2 - largura_total//2 + i*espacamento_x
            tex = random.choice(alien_textures) if alien_textures else None
            alien = Alien(x, y,
                texture=tex[0] if tex else None,
                tex_w=tex[1] if tex else 40,
                tex_h=tex[2] if tex else 20,
                bullet_texture=bullet_alien_tex[0] if bullet_alien_tex else None,
                bullet_tex_w=bullet_alien_tex[1] if bullet_alien_tex else 16,
                bullet_tex_h=bullet_alien_tex[2] if bullet_alien_tex else 16)
            alien.som_tiro = som_tiro_alien
            aliens.append(alien)
    
    running = True
    attack_timer = 0
    alien_dir = 1
    alien_speed = 2
    attack_interval = 40
    nivel = 1
    
    clock = pygame.time.Clock()
    stars = [Star() for _ in range(NUM_STARS)]
    is_lit = True

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    paused = not paused
                    if paused:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                elif event.key in (K_RETURN, K_m):
                    pygame.mixer.music.stop()
                    return "menu", ship.score
                elif event.key == K_l:
                    is_lit = not is_lit
        
        if paused:
            glClear(GL_COLOR_BUFFER_BIT)
            if bg_texture:
                draw_tiled_bg(bg_texture[0], bg_texture[1], bg_texture[2])
            ship.draw(is_lit)
            for alien in aliens:
                alien.draw(is_lit)
            if vidas_texture:
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, vidas_texture[0])
                for i in range(ship.lives):
                    x = 20 + i*28
                    y = HEIGHT-28
                    glColor4f(1, 1, 1, 1)
                    glBegin(GL_QUADS)
                    glTexCoord2f(0, 0); glVertex2f(x, y)
                    glTexCoord2f(1, 0); glVertex2f(x + vidas_texture[1], y)
                    glTexCoord2f(1, 1); glVertex2f(x + vidas_texture[1], y + vidas_texture[2])
                    glTexCoord2f(0, 1); glVertex2f(x, y + vidas_texture[2])
                    glEnd()
                glDisable(GL_TEXTURE_2D)
                glDisable(GL_BLEND)

            draw_num(WIDTH//2 - 20, HEIGHT - 40, nivel, numeros_texture)

            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glColor4f(0, 0, 0, 0.5)
            glBegin(GL_QUADS)
            glVertex2f(0, 0); glVertex2f(WIDTH, 0)
            glVertex2f(WIDTH, HEIGHT); glVertex2f(0, HEIGHT)
            glEnd()
            glDisable(GL_BLEND)

            titulo = "PAUSADO"
            draw_text(WIDTH//2 - get_text_width(titulo, 36)//2, HEIGHT//2 - 10, titulo, size=36)

            subtitulo = "Pressione ESC para continuar"
            draw_text(WIDTH//2 - get_text_width(subtitulo, 24)//2, HEIGHT//2 + 30, subtitulo, size=24)

            voltar = "Voltar ao menu (Pressione ENTER ou M)"
            draw_text(WIDTH//2 - get_text_width(voltar, 28)//2, HEIGHT//2 + 80, voltar, size=28)

            pygame.display.flip()
            clock.tick(30)
            continue

        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            ship.move(-5)
        if keys[K_RIGHT]:
            ship.move(5)
        if keys[K_SPACE] or keys[K_LCTRL]:
            ship.shoot()

        ship.update()
        
        for pu in powerups[:]:
            pu.update()
            if pu.y < 0:
                powerups.remove(pu)
            
            if abs(pu.x - ship.x) < SHIP_WIDTH/2 and abs(pu.y - ship.y) < SHIP_HEIGHT/2:
                powerups.remove(pu)
                if pu.pu_type == "life":
                    if ship.lives < 5:
                        ship.lives += 1
                elif pu.pu_type in ["speed", "shield", "double_shot"]:
                    ship.activate_powerup(pu.pu_type)
        
        attack_timer += 1
        if aliens and not boss:
            if attack_timer > attack_interval:
                attack_timer = 0
                attackers = [a for a in aliens if a.alive and not a.attacking]
                if attackers:
                    random.choice(attackers).attack()
            borda_direita = max([alien.x for alien in aliens if alien.alive], default=0) + ALIEN_WIDTH//2
            borda_esquerda = min([alien.x for alien in aliens if alien.alive], default=WIDTH) - ALIEN_WIDTH//2
            if borda_direita >= WIDTH:
                alien_dir = -1
            if borda_esquerda <= 0:
                alien_dir = 1
            for alien in aliens:
                if alien.alive:
                    alien.x += alien_dir * alien_speed
                alien.update()
            for b in ship.bullets[:]:
                for alien in aliens:
                    if alien.alive and abs(b[0]-alien.x)<ALIEN_WIDTH//2 and abs(b[1]-alien.y)<ALIEN_HEIGHT//2:
                        alien.alive = False
                        ship.score += 1
                        ship.coins += 1
                        ship.bullets.remove(b)
                        som_explosao.play()
                        
                        powerup_spawn_counter += 1
                        if powerup_spawn_counter >= powerup_spawn_threshold:
                            pu_type = random.choice(list(powerup_textures.keys()))
                            powerups.append(PowerUp(alien.x, alien.y, pu_type, powerup_textures[pu_type]))
                            powerup_spawn_counter = 0
                            powerup_spawn_threshold = random.randint(10, 30)
                        
                        break
            for alien in aliens:
                if alien.attacking and alien.bullet:
                    if abs(alien.bullet[0]-ship.x)<SHIP_WIDTH//2 and abs(alien.bullet[1]-ship.y)<SHIP_HEIGHT//2:
                        if not ship.powerups["shield"]["active"]:
                            ship.lives -= 1
                            som_perde_vida.play()
                        alien.attacking = False
                        alien.bullet = None
        
        for star in stars:
            star.update()

        glClear(GL_COLOR_BUFFER_BIT)
        if bg_texture:
            draw_tiled_bg(bg_texture[0], bg_texture[1], bg_texture[2])
        for star in stars:
            star.draw()
            
        ship.draw(is_lit)
        for alien in aliens:
            alien.draw(is_lit)
        for pu in powerups:
            pu.draw()
        
        if boss:
            boss.update(ship)
            boss.draw(is_lit)

            if boss:
                for b in ship.bullets[:]:
                    if (b[0] > boss.x - boss.tex_w / 2 and b[0] < boss.x + boss.tex_w / 2 and
                        b[1] > boss.y - boss.tex_h / 2 and b[1] < boss.y + boss.tex_h / 2):
                        
                        ship.bullets.remove(b)
                        if boss.take_damage(5):
                            boss = None
                            som_explosao.play()
                            ship.score += 100
                            ship.coins += 10
                            break
            
            if boss:
                for b in boss.bullets[:]:
                    if (abs(b[0] - ship.x) < SHIP_WIDTH / 2 and
                        abs(b[1] - ship.y) < SHIP_HEIGHT / 2):
                        if not ship.powerups["shield"]["active"]:
                            ship.lives -= 1
                            som_perde_vida.play()
                        boss.bullets.remove(b)

        if vidas_texture:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, vidas_texture[0])
            for i in range(ship.lives):
                x = 20 + i*28
                y = HEIGHT-28
                glColor4f(1, 1, 1, 1)
                glBegin(GL_QUADS)
                glTexCoord2f(0, 0); glVertex2f(x, y)
                glTexCoord2f(1, 0); glVertex2f(x + vidas_texture[1], y)
                glTexCoord2f(1, 1); glVertex2f(x + vidas_texture[1], y + vidas_texture[2])
                glTexCoord2f(0, 1); glVertex2f(x, y + vidas_texture[2])
                glEnd()
            glDisable(GL_TEXTURE_2D)
            glDisable(GL_BLEND)
        else:
            for i in range(ship.lives):
                glColor3f(1, 0, 0)
                glRectf(20 + i*25, HEIGHT-30, 35 + i*25, HEIGHT-10)
        
        score_str = str(ship.score)
        score_w = sum(numeros_texture[int(d)][1] + 2 for d in score_str)
        draw_num(WIDTH - score_w - 20, HEIGHT - 40, ship.score, numeros_texture)
        
        draw_num(WIDTH//2 - 20, HEIGHT - 40, nivel, numeros_texture)
        draw_text(60, 50, f"Coins: {ship.coins}", size=24)

        pygame.display.flip()
        clock.tick(30)
        
        if not any(a.alive for a in aliens) and not boss:
            nivel += 1
            alien_speed += 1
            attack_interval = max(10, attack_interval - 5)
            aliens = []
            
            powerup_spawn_counter = 0
            powerup_spawn_threshold = random.randint(10, 30)

            if nivel == 3:
                boss_config = BOSS_CONFIGS["boss_1"]
                boss_tex = load_texture(boss_config["texture_file"], boss_config["texture_size"])
                boss = Boss(boss_config, boss_tex, bullet_alien_tex, som_tiro_alien)
            elif nivel == 6:
                boss_config = BOSS_CONFIGS["boss_2"]
                boss_tex = load_texture(boss_config["texture_file"], boss_config["texture_size"])
                boss = Boss(boss_config, boss_tex, bullet_alien_tex, som_tiro_alien)
            else:
                for l in range(linhas):
                    n_aliens = base + l
                    largura_total = (n_aliens-1) * espacamento_x
                    y = HEIGHT - 60 - l*espacamento_y
                    for i in range(n_aliens):
                        x = WIDTH//2 - largura_total//2 + i*espacamento_x
                        tex = random.choice(alien_textures) if alien_textures else None
                        alien = Alien(x, y,
                            texture=tex[0] if tex else None,
                            tex_w=tex[1] if tex else 40,
                            tex_h=tex[2] if tex else 20,
                            bullet_texture=bullet_alien_tex[0] if bullet_alien_tex else None,
                            bullet_tex_w=bullet_alien_tex[1] if bullet_alien_tex else 16,
                            bullet_tex_h=bullet_alien_tex[2] if bullet_alien_tex else 16)
                        alien.som_tiro = som_tiro_alien
                        aliens.append(alien)
        if ship.lives <= 0:
            running = False

    highscores = load_highscores()
    is_new_highscore = False
    if not highscores or ship.score > highscores[-1]['score'] or len(highscores) < 10:
        is_new_highscore = True
    
    player_data = load_player_data()
    player_data["coins"] += ship.coins
    save_player_data(player_data)

    if is_new_highscore:
        return "enter_initials", ship.score
    else:
        return "game_over", ship.score

def main():
    pygame.init()
    pygame.mixer.init()

    pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
    gluOrtho2D(0, WIDTH, 0, HEIGHT)
    glClearColor(0, 0, 0, 1)

    bg_texture = load_texture('space_bg.png', (128, 128))
    vidas_texture = load_texture('vidas.png', (24, 24))
    
    ship_textures = {
        "nave.png": load_texture('nave.png', (32, 32)),
        "playerShip1_red.png": load_texture('playerShip1_red.png', (32, 32)),
        "playerShip2_orange.png": load_texture('playerShip2_orange.png', (32, 32)),
        "playerShip3_green.png": load_texture('playerShip3_green.png', (32, 32))
    }
    
    alien_textures = []
    for fname in ['ufoBlue.png', 'ufoGreen.png', 'ufoRed.png', 'ufoYellow.png']:
        tex = load_texture(fname, (32, 32))
        if tex:
            alien_textures.append(tex)

    bullet_ship_tex = load_texture('disparoNave.png', (8, 16))
    bullet_alien_tex = load_texture('disparoAlien.png', (8, 16))
    numeros_texture = []
    for i in range(10):
        tex = load_texture(f'img_numbers/{i}.png', (24, 32))
        numeros_texture.append(tex)
    coin_texture = load_texture('coin.png', (16, 16))
    
    powerup_textures = {
        "life": load_texture('nave.png', (POWERUP_SIZE, POWERUP_SIZE)),
        "speed": load_texture('bold_silver.png', (POWERUP_SIZE, POWERUP_SIZE)),
        "shield": load_texture('shield_silver.png', (POWERUP_SIZE, POWERUP_SIZE)),
        "double_shot": load_texture('star_silver.png', (POWERUP_SIZE, POWERUP_SIZE))
    }
    
    shield_texture = load_texture('shield1.png', (128, 128))

    player_data = load_player_data()
    
    clock = pygame.time.Clock()
    game_state = "menu"
    final_score = 0
    
    ship_attributes_dict = {
        "nave.png": {"speed": 1.5, "lives": 3, "fire_rate": 10},
        "playerShip1_red.png": {"speed": 3, "lives": 2, "fire_rate": 10},
        "playerShip2_orange.png": {"speed": 0.75, "lives": 5, "fire_rate": 10},
        "playerShip3_green.png": {"speed": 2, "lives": 3, "fire_rate": 7}
    }

    while game_state != "quit":
        if game_state == "menu":
            game_state = show_menu(bg_texture, clock)
        elif game_state == "shop":
            game_state, player_data = show_shop(bg_texture, clock, player_data, coin_texture, ship_textures)
        elif game_state == "start_game":
            ship_file = player_data["current_ship"]
            ship_texture_data = ship_textures[ship_file]
            selected_ship_attrs = ship_attributes_dict[ship_file]
            
            game_state, final_score = run_game(bg_texture, vidas_texture, ship_texture_data, alien_textures, bullet_ship_tex, bullet_alien_tex, numeros_texture, selected_ship_attrs, powerup_textures, shield_texture)
        elif game_state == "enter_initials":
            game_state, final_score = enter_initials_screen(bg_texture, clock, final_score)
        elif game_state == "game_over":
            game_state, final_score = show_game_over(bg_texture, clock, load_highscores(), final_score)
    
    pygame.quit()
    quit()

if __name__ == '__main__':
    main()