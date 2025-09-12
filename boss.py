# boss.py

import pygame
from OpenGL.GL import *
import random
import math

WIDTH, HEIGHT = 800, 600

class Boss:
    def __init__(self, texture, bullet_texture, som_tiro):
        self.x = WIDTH // 2
        self.y = HEIGHT - 100
        self.texture = texture
        self.tex_w = texture[1]
        self.tex_h = texture[2]
        self.health = 100  # O boss tem 100 pontos de vida
        self.bullets = []
        self.bullet_texture = bullet_texture
        self.bullet_tex_w = bullet_texture[1]
        self.bullet_tex_h = bullet_texture[2]
        self.som_tiro = som_tiro
        self.move_dir = 1
        self.speed = 5
        self.cooldown = 0
        self.max_cooldown = 30 #60 Cooldown para o ataque do boss

    def update(self):
        # Lógica de movimento do boss (vai e volta horizontalmente)
        self.x += self.move_dir * self.speed
        if self.x > WIDTH - self.tex_w // 2 or self.x < self.tex_w // 2:
            self.move_dir *= -1
            self.y -= 10 # Move para baixo a cada vez que atinge a borda

        # Lógica de ataque do boss
        self.cooldown += 1
        if self.cooldown >= self.max_cooldown:
            self.shoot()
            self.cooldown = 0

        # Atualiza a posição dos tiros do boss
        #for b in self.bullets:
        #    b[1] -= 4
        #self.bullets = [b for b in self.bullets if b[1] > 0]
        for b in self.bullets:
            b[0] += b[2] # Adiciona a velocidade X
            b[1] += b[3] # Adiciona a velocidade Y
        self.bullets = [b for b in self.bullets if b[1] > 0 and b[1] < HEIGHT and b[0] > 0 and b[0] < WIDTH]

    # def shoot(self):
    #     Disparo triplo
    #     self.bullets.append([self.x, self.y - self.tex_h // 2])
    #     self.bullets.append([self.x - 20, self.y - self.tex_h // 2])
    #     self.bullets.append([self.x + 20, self.y - self.tex_h // 2])
    #     if self.som_tiro:
    #         self.som_tiro.play()

    def shoot(self):
        num_bullets = 5  # Quantos projéteis serão disparados
        spread_angle = 60 # Ângulo total de dispersão em graus
        bullet_speed = 4 # Velocidade dos projéteis
        
        # O ângulo de partida será centralizado em 270 graus (para baixo)
        start_angle = 270 - (spread_angle / 2) # Ex: 270 - 30 = 240 graus
        
        for i in range(num_bullets):
            angle = start_angle + i * (spread_angle / (num_bullets - 1))
            
            # Converte o ângulo para radianos e calcula a velocidade X e Y
            dx = math.cos(math.radians(angle)) * bullet_speed
            dy = math.sin(math.radians(angle)) * bullet_speed
            
            # Adiciona o projétil com sua posição e velocidade
            self.bullets.append([self.x, self.y - self.tex_h // 2, dx, dy])
            
        if self.som_tiro:
            self.som_tiro.play()

    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0

    def draw(self):
        # Desenhar o boss (a textura)
        if self.health > 0:
            # HABILITE o blending (transparência)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            
            # HABILITE o uso de texturas
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture[0])
            glColor4f(1, 1, 1, 1)  # Use glColor4f para cores com alfa
            
            x = self.x - self.tex_w // 2
            y = self.y - self.tex_h // 2
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(x, y)
            glTexCoord2f(1, 0); glVertex2f(x + self.tex_w, y)
            glTexCoord2f(1, 1); glVertex2f(x + self.tex_w, y + self.tex_h)
            glTexCoord2f(0, 1); glVertex2f(x, y + self.tex_h)
            glEnd()
            
            # DESABILITE o uso de texturas e o blending depois de desenhar a textura do boss
            glDisable(GL_TEXTURE_2D)
            glDisable(GL_BLEND)
            
            # Desenhar barra de vida do boss
            # Esta parte não precisa de blending de textura, então o glDisable acima está correto
            glColor3f(1, 0, 0) # Cor vermelha
            glRectf(self.x - 50, self.y + self.tex_h // 2 + 10, self.x - 50 + self.health, self.y + self.tex_h // 2 + 18)
        
        # Desenhar os tiros do boss
        for b in self.bullets:
            if self.bullet_texture:
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, self.bullet_texture[0])
                glColor4f(1, 1, 1, 1)
                bx = b[0] - self.bullet_texture[1] // 2
                by = b[1]
                glBegin(GL_QUADS)
                glTexCoord2f(0, 0); glVertex2f(bx, by)
                glTexCoord2f(1, 0); glVertex2f(bx + self.bullet_texture[1], by)
                glTexCoord2f(1, 1); glVertex2f(bx + self.bullet_texture[1], by + self.bullet_texture[2])
                glTexCoord2f(0, 1); glVertex2f(bx, by + self.bullet_texture[2])
                glEnd()
                glDisable(GL_TEXTURE_2D)
                glDisable(GL_BLEND)