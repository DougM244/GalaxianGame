# boss.py

import pygame
from OpenGL.GL import *
import random
import math

WIDTH, HEIGHT = 800, 600

# Dicionário de configurações dos bosses
BOSS_CONFIGS = {
    "boss_1": {
        "health": 150,
        "speed": 4,
        "max_cooldown": 30,
        "texture_file": 'img_boss_ship/boss_lv10.png',
        "texture_size": (100, 100),
        "attack_type": "tracking_shot"
    },
    "boss_2": {
        "health": 170,
        "speed": 4,
        "max_cooldown": 20,
        "texture_file": 'img_boss_ship/boss_lv5.png',
        "texture_size": (100, 100),
        "attack_type": "spread_shot"
    }
}

class Boss:
    def __init__(self, config, texture, bullet_texture, som_tiro):
        self.x = WIDTH // 2
        self.y = HEIGHT - 100
        self.texture = texture
        self.tex_w = texture[1]
        self.tex_h = texture[2]
        
        # Atribua as características do boss a partir do dicionário de configuração
        self.health = config["health"]
        self.speed = config["speed"]
        self.max_cooldown = config["max_cooldown"]
        self.attack_type = config["attack_type"]
        
        self.bullets = []
        self.bullet_texture = bullet_texture
        self.bullet_tex_w = bullet_texture[1]
        self.bullet_tex_h = bullet_texture[2]
        self.som_tiro = som_tiro
        self.move_dir = 1
        self.cooldown = 0
    
    def update(self, ship):
        self.x += self.move_dir * self.speed
        if self.x > WIDTH - self.tex_w // 2 or self.x < self.tex_w // 2:
            self.move_dir *= -1
            self.y -= 10
        
        self.cooldown += 1
        if self.cooldown >= self.max_cooldown:
            self.shoot(ship)
            self.cooldown = 0
        
        for b in self.bullets:
            current_bullet_speed = 4
            # Ponto a partir do qual as balas param de seguir
            tracking_limit = HEIGHT / 2
            if b[4] == "tracking" and b[1] > tracking_limit:
                # Posição atual do tiro
                bullet_x, bullet_y = b[0], b[1]
                
                # Vetor para o jogador
                target_x, target_y = ship.x, ship.y
                
                # Calcula o ângulo atual do tiro
                current_angle = math.atan2(b[3], b[2])
                
                # Calcula o ângulo desejado para o jogador
                desired_angle = math.atan2(target_y - bullet_y, target_x - bullet_x)
                
                angle_diff = desired_angle - current_angle
                
                if angle_diff > math.pi:
                    angle_diff -= 2 * math.pi
                elif angle_diff < -math.pi:
                    angle_diff += 2 * math.pi
                
                turn_rate = math.radians(3)
                
                if angle_diff > turn_rate:
                    angle_diff = turn_rate
                elif angle_diff < -turn_rate:
                    angle_diff = -turn_rate
                
                new_angle = current_angle + angle_diff
                
                b[2] = math.cos(new_angle) * current_bullet_speed
                b[3] = math.sin(new_angle) * current_bullet_speed
            
            # Move o tiro
            b[0] += b[2] 
            b[1] += b[3]

        self.bullets = [b for b in self.bullets if b[1] > 0 and b[1] < HEIGHT and b[0] > 0 and b[0] < WIDTH]

    def shoot(self, ship):
        if self.attack_type == "spread_shot":
            num_bullets = 5
            spread_angle = 60
            bullet_speed = 4
            
            start_angle = 270 - (spread_angle / 2)
            
            for i in range(num_bullets):
                angle = start_angle + i * (spread_angle / (num_bullets - 1))
                dx = math.cos(math.radians(angle)) * bullet_speed
                dy = math.sin(math.radians(angle)) * bullet_speed
                
                # Adiciona o tipo de ataque 'spread' para consistência
                self.bullets.append([self.x, self.y - self.tex_h // 2, dx, dy, "spread"])
            
        elif self.attack_type == "tracking_shot":
            bullet_speed = 3
            
            offset_angle_degrees = 90 # <--- ÂNGULO DE DESVIO (em graus)

            # Calcula o ângulo base direto para o jogador
            base_angle = math.atan2(ship.y - self.y, ship.x - self.x)
            
            # --- Primeiro Tiro (desviado para a esquerda) ---
            angle1 = base_angle - math.radians(offset_angle_degrees)
            dx1 = math.cos(angle1) * bullet_speed
            dy1 = math.sin(angle1) * bullet_speed
            self.bullets.append([self.x, self.y - self.tex_h // 2, dx1, dy1, "tracking"])

            # --- Segundo Tiro (desviado para a direita) ---
            angle2 = base_angle + math.radians(offset_angle_degrees)
            dx2 = math.cos(angle2) * bullet_speed
            dy2 = math.sin(angle2) * bullet_speed
            self.bullets.append([self.x, self.y - self.tex_h // 2, dx2, dy2, "tracking"])
        
        if self.som_tiro:
            self.som_tiro.play()

    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0

    def draw(self):
        if self.health > 0:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture[0])
            glColor4f(1, 1, 1, 1)
            x = self.x - self.tex_w // 2
            y = self.y - self.tex_h // 2
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(x, y)
            glTexCoord2f(1, 0); glVertex2f(x + self.tex_w, y)
            glTexCoord2f(1, 1); glVertex2f(x + self.tex_w, y + self.tex_h)
            glTexCoord2f(0, 1); glVertex2f(x, y + self.tex_h)
            glEnd()
            glDisable(GL_TEXTURE_2D)
            glDisable(GL_BLEND)
            
            glColor3f(1, 0, 0)
            glRectf(self.x - 50, self.y + self.tex_h // 2 + 10, self.x - 50 + self.health, self.y + self.tex_h // 2 + 18)
        
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