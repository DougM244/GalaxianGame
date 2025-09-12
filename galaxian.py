import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import os
from menu import show_menu

WIDTH, HEIGHT = 800, 600
SHIP_WIDTH, SHIP_HEIGHT = 60, 20
ALIEN_WIDTH, ALIEN_HEIGHT = 40, 20
BULLET_WIDTH, BULLET_HEIGHT = 5, 10

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
            x += tex[1] + 2  # espaço entre os dígitos

class Ship:
    def __init__(self, texture=None, tex_w=60, tex_h=60, bullet_texture=None, bullet_tex_w=16, bullet_tex_h=16):
        self.x = WIDTH // 2
        self.y = 40
        self.lives = 3
        self.score = 0
        self.bullets = []
        self.cooldown = 0
        self.texture = texture
        self.tex_w = tex_w
        self.tex_h = tex_h
        self.bullet_texture = bullet_texture
        self.bullet_tex_w = bullet_tex_w
        self.bullet_tex_h = bullet_tex_h
        self.som_tiro = None  # atributo para o som do tiro

    def move(self, dx):
        self.x += dx
        self.x = max(SHIP_WIDTH//2, min(WIDTH-SHIP_WIDTH//2, self.x))

    def shoot(self):
        if self.cooldown == 0:
            self.bullets.append([self.x, self.y + SHIP_HEIGHT//2])
            self.cooldown = 10
            if self.som_tiro:
                self.som_tiro.play()

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1
        for b in self.bullets:
            b[1] += 5  # velocidade do tiro reduzida
        self.bullets = [b for b in self.bullets if b[1] < HEIGHT]

    def draw(self):
        # Desenhar nave como textura OpenGL
        if self.texture:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture)
            glColor3f(1, 1, 1)
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
        # Desenhar tiros
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
        self.som_tiro = None  # atributo para o som do tiro do alien

    def attack(self):
        self.attacking = True
        self.bullet = [self.x, self.y-ALIEN_HEIGHT//2]
        if self.som_tiro:
            self.som_tiro.play()

    def update(self):
        if self.attacking and self.bullet:
            self.bullet[1] -= 4  # velocidade do tiro do alien reduzida
            if self.bullet[1] < 0:
                self.attacking = False
                self.bullet = None

    def draw(self):
        if self.alive:
            if self.texture:
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, self.texture)
                glColor3f(1, 1, 1)
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

def run_game(bg_texture, vidas_texture, nave_texture, alien_textures, bullet_ship_tex, bullet_alien_tex, numeros_texture):
    """
    Função principal que contém o loop do jogo.
    """
    pygame.mixer.music.load('musica.mp3')
    pygame.mixer.music.play(-1)

    som_tiro = pygame.mixer.Sound('tiro.mp3')
    som_tiro_alien = pygame.mixer.Sound('tiro_alien.mp3')
    som_explosao = pygame.mixer.Sound('explosao.mp3')
    som_perde_vida = pygame.mixer.Sound('perde_vida.mp3')

    if nave_texture:
        ship = Ship(texture=nave_texture[0], tex_w=nave_texture[1], tex_h=nave_texture[2],
                    bullet_texture=bullet_ship_tex[0] if bullet_ship_tex else None,
                    bullet_tex_w=bullet_ship_tex[1] if bullet_ship_tex else 16,
                    bullet_tex_h=bullet_ship_tex[2] if bullet_ship_tex else 16)
    else:
        ship = Ship(bullet_texture=bullet_ship_tex[0] if bullet_ship_tex else None,
                    bullet_tex_w=bullet_ship_tex[1] if bullet_ship_tex else 16,
                    bullet_tex_h=bullet_ship_tex[2] if bullet_ship_tex else 16)
    ship.som_tiro = som_tiro

    aliens = []
    linhas = 5
    base = 5
    espacamento_x = 60
    espacamento_y = 40
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

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            ship.move(-5)
        if keys[K_RIGHT]:
            ship.move(5)
        if keys[K_SPACE] or keys[K_LCTRL]:
            ship.shoot()

        ship.update()
        attack_timer += 1
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
                    ship.score += 100
                    ship.bullets.remove(b)
                    som_explosao.play()
                    break
        for alien in aliens:
            if alien.attacking and alien.bullet:
                if abs(alien.bullet[0]-ship.x)<SHIP_WIDTH//2 and abs(alien.bullet[1]-ship.y)<SHIP_HEIGHT//2:
                    ship.lives -= 1
                    som_perde_vida.play()
                    alien.attacking = False
                    alien.bullet = None
        glClear(GL_COLOR_BUFFER_BIT)
        if bg_texture:
            draw_tiled_bg(bg_texture[0], bg_texture[1], bg_texture[2])
        ship.draw()
        for alien in aliens:
            alien.draw()
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
        for i in range(ship.score // 200):
            glColor3f(1, 1, 0)
            glRectf(WIDTH-30 - i*15, HEIGHT-30, WIDTH-20 - i*15, HEIGHT-10)
        draw_num(WIDTH//2 - 20, HEIGHT - 40, nivel, numeros_texture)
        pygame.display.flip()
        clock.tick(30)
        if not any(a.alive for a in aliens):
            nivel += 1
            alien_speed += 1
            attack_interval = max(10, attack_interval - 5)
            aliens = []
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

    return "game_over" # Você pode retornar o estado de "game_over" para a função main()

def main():
    pygame.init()
    pygame.mixer.init()

    pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
    gluOrtho2D(0, WIDTH, 0, HEIGHT)
    glClearColor(0, 0, 0, 1)

    # AQUI AS TEXTURAS SÃO CARREGADAS ANTES DO LOOP PRINCIPAL
    # A função `load_texture` agora pode ser chamada aqui
    bg_texture = load_texture('space_bg.png', (128, 128))
    vidas_texture = load_texture('vidas.png', (24, 24))
    nave_texture = load_texture('nave.png', (32, 32))
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

    clock = pygame.time.Clock()
    game_state = "menu"

    while game_state != "quit":
        if game_state == "menu":
            game_state = show_menu(bg_texture, clock)
        elif game_state == "start_game":
            game_state = run_game(bg_texture, vidas_texture, nave_texture, alien_textures, bullet_ship_tex, bullet_alien_tex, numeros_texture)
        elif game_state == "game_over":
            print("Game Over! Voltando para o menu...")
            pygame.time.wait(2000)
            game_state = "menu"
    
    pygame.quit()
    quit()

if __name__ == '__main__':
    main()