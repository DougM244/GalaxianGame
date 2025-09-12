# menu.py

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

WIDTH, HEIGHT = 800, 600

# Esta função é a versão simplificada da sua draw_tiled_bg, para evitar
# que o menu precise importar funções de outro arquivo.
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

def draw_text(x, y, text, size=24):
    """
    Desenha texto na tela usando Pygame e OpenGL.
    """
    font = pygame.font.SysFont('Arial', size)
    text_surface = font.render(text, True, (255, 255, 255), (0, 0, 0))
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    glRasterPos2i(x, HEIGHT - y - text_surface.get_height())
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

def show_menu(bg_texture, clock):
    """
    Exibe o menu inicial do jogo e gerencia a navegação.
    Recebe a textura de fundo e o relógio.
    """
    run_menu = True
    selected_option = 0
    options = ["Start Game", "Quit"]
    
    while run_menu:
        for event in pygame.event.get():
            if event.type == QUIT:
                return "quit"
            if event.type == KEYDOWN:
                if event.key == K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == K_RETURN:
                    if options[selected_option] == "Start Game":
                        return "start_game"
                    elif options[selected_option] == "Quit":
                        return "quit"
                        
        glClear(GL_COLOR_BUFFER_BIT)
        
        # Desenha o fundo usando a textura passada como argumento
        if bg_texture:
            draw_tiled_bg(bg_texture[0], bg_texture[1], bg_texture[2])
        
        draw_text(WIDTH // 2 - 120, HEIGHT // 2 - 100, "GALAXIAN", size=48)
        
        for i, option in enumerate(options):
            color = (255, 255, 255) if i == selected_option else (150, 150, 150)
            
            # Para evitar `NameError` e manter a modularidade,
            # desenhamos o texto das opções aqui mesmo.
            font = pygame.font.SysFont('Arial', 32)
            text_surface = font.render(option, True, color, (0, 0, 0))
            text_data = pygame.image.tostring(text_surface, "RGBA", True)
            
            x = WIDTH // 2 - text_surface.get_width() // 2
            y = HEIGHT // 2 + 50 + i * 40
            
            glRasterPos2i(x, HEIGHT - y - text_surface.get_height())
            glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        
        pygame.display.flip()
        clock.tick(30)