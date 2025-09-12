import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import os
import json

WIDTH, HEIGHT = 800, 600

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
    font = pygame.font.SysFont('Arial', size)
    text_surface = font.render(text, True, (255, 255, 255), (0, 0, 0))
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    glRasterPos2i(x, HEIGHT - y - text_surface.get_height())
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

def show_menu(bg_texture, clock):
    run_menu = True
    selected_option = 0
    options = ["Start Game", "Shop", "Quit"]
    
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
                    elif options[selected_option] == "Shop":
                        return "shop"
                    elif options[selected_option] == "Quit":
                        return "quit"
                        
        glClear(GL_COLOR_BUFFER_BIT)
        
        if bg_texture:
            draw_tiled_bg(bg_texture[0], bg_texture[1], bg_texture[2])
        
        draw_text(WIDTH // 2 - 120, HEIGHT // 2 - 100, "GALAXIAN", size=48)
        
        for i, option in enumerate(options):
            color = (255, 255, 255) if i == selected_option else (150, 150, 150)
            
            font = pygame.font.SysFont('Arial', 32)
            text_surface = font.render(option, True, color, (0, 0, 0))
            text_data = pygame.image.tostring(text_surface, "RGBA", True)
            
            x = WIDTH // 2 - text_surface.get_width() // 2
            y = HEIGHT // 2 + 50 + i * 40
            
            glRasterPos2i(x, HEIGHT - y - text_surface.get_height())
            glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        
        pygame.display.flip()
        clock.tick(30)
        
def show_game_over(bg_texture, clock, highscores, score):
    run_game_over = True
    selected_option = 0
    options = ["Back to Menu", "Quit"]
    
    while run_game_over:
        for event in pygame.event.get():
            if event.type == QUIT:
                return "quit", score
            if event.type == KEYDOWN:
                if event.key == K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == K_RETURN:
                    if options[selected_option] == "Back to Menu":
                        return "menu", score
                    elif options[selected_option] == "Quit":
                        return "quit", score
                        
        glClear(GL_COLOR_BUFFER_BIT)
        
        if bg_texture:
            draw_tiled_bg(bg_texture[0], bg_texture[1], bg_texture[2])
        
        draw_text(WIDTH // 2 - 160, HEIGHT // 2 - 180, "GAME OVER", size=48)
        
        draw_text(WIDTH // 2 - 100, HEIGHT // 2 - 120, "HIGH SCORES", size=32)
        y_offset = HEIGHT // 2 - 80
        for i, entry in enumerate(highscores):
            score_text = f"{i+1}. {entry['initials']} - {entry['score']}"
            draw_text(WIDTH // 2 - 100, y_offset + i * 30, score_text, size=24)
            
        for i, option in enumerate(options):
            color = (255, 255, 255) if i == selected_option else (150, 150, 150)
            
            font = pygame.font.SysFont('Arial', 32)
            text_surface = font.render(option, True, color, (0, 0, 0))
            text_data = pygame.image.tostring(text_surface, "RGBA", True)
            
            x = WIDTH // 2 - text_surface.get_width() // 2
            y = HEIGHT // 2 + 100 + i * 40
            
            glRasterPos2i(x, HEIGHT - y - text_surface.get_height())
            glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        
        pygame.display.flip()
        clock.tick(30)

def show_shop(bg_texture, clock, player_data, coin_texture, ship_textures):
    run_shop = True
    selected_option = 0
    
    ships_data = [
        {"name": "Light-Fighter", "file": "nave.png", "price": 0, "speed": 1.5, "lives": 3, "fire_rate": 10},
        {"name": "Firebolt", "file": "playerShip1_red.png", "price": 10000, "speed": 3, "lives": 2, "fire_rate": 10},
        {"name": "Cruiser", "file": "playerShip2_orange.png", "price": 15000, "speed": 0.75, "lives": 5, "fire_rate": 10},
        {"name": "Rapid-Shot", "file": "playerShip3_green.png", "price": 30000, "speed": 2, "lives": 3, "fire_rate": 7}
    ]
    
    options = ships_data + [{"name": "Back to Menu", "file": None, "price": None}]

    while run_shop:
        for event in pygame.event.get():
            if event.type == QUIT:
                return "quit", player_data
            if event.type == KEYDOWN:
                if event.key == K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == K_ESCAPE:
                    return "menu", player_data
                elif event.key == K_RETURN:
                    selected_item = options[selected_option]
                    
                    if selected_item["name"] == "Back to Menu":
                        return "menu", player_data
                    
                    selected_ship = selected_item
                    
                    if selected_ship["file"] in player_data["unlocked_ships"]:
                        player_data["current_ship"] = selected_ship["file"]
                        # Salvamos os dados após equipar a nave
                        # É importante salvar aqui para que a escolha seja permanente
                        # No entanto, a lógica de retorno para o menu já faz isso na main().
                        # Então, vamos salvar somente se uma compra for feita.
                        return "menu", player_data
                    elif player_data["coins"] >= selected_ship["price"]:
                        player_data["coins"] -= selected_ship["price"]
                        player_data["unlocked_ships"].append(selected_ship["file"])
                        player_data["current_ship"] = selected_ship["file"]
                        # Adicionamos a chamada para salvar os dados imediatamente após a compra
                        from galaxian import save_player_data
                        save_player_data(player_data)
                        return "menu", player_data
        
        glClear(GL_COLOR_BUFFER_BIT)
        if bg_texture:
            draw_tiled_bg(bg_texture[0], bg_texture[1], bg_texture[2])
        
        draw_text(WIDTH // 2 - 60, 50, "SHOP", size=48)
        draw_text(60, 50, f"Coins: {player_data['coins']}", size=24)
        
        y_start = 150
        line_spacing = 100
        
        for i, item in enumerate(options):
            y_pos = y_start + i * line_spacing
            
            color = (255, 255, 255) if i == selected_option else (150, 150, 150)
            
            if item["name"] == "Back to Menu":
                font = pygame.font.SysFont('Arial', 32)
                text_surface = font.render("Back to Menu", True, color, (0, 0, 0))
                text_data = pygame.image.tostring(text_surface, "RGBA", True)
                x = WIDTH // 2 - text_surface.get_width() // 2
                glRasterPos2i(x, HEIGHT - y_pos - text_surface.get_height())
                glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)
                continue
                
            ship = item
            is_unlocked = ship["file"] in player_data["unlocked_ships"]
            
            glEnable(GL_TEXTURE_2D)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            
            ship_tex_id = ship_textures[ship["file"]][0]
            glBindTexture(GL_TEXTURE_2D, ship_tex_id)
            
            if i == selected_option:
                glColor4f(1, 1, 1, 1)
            else:
                glColor4f(0.6, 0.6, 0.6, 1)
            
            ship_x = WIDTH // 2 - 250
            ship_y = HEIGHT - (y_pos + 30 + 32)
            
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(ship_x, ship_y)
            glTexCoord2f(1, 0); glVertex2f(ship_x + 32, ship_y)
            glTexCoord2f(1, 1); glVertex2f(ship_x + 32, ship_y + 32)
            glTexCoord2f(0, 1); glVertex2f(ship_x, ship_y + 32)
            glEnd()
            
            glDisable(GL_TEXTURE_2D)
            glDisable(GL_BLEND)

            font = pygame.font.SysFont('Arial', 32)
            text_surface = font.render(ship["name"], True, color, (0, 0, 0))
            text_data = pygame.image.tostring(text_surface, "RGBA", True)
            glRasterPos2i(WIDTH // 2 - 150, HEIGHT - y_pos - text_surface.get_height())
            glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)
            
            draw_text(WIDTH // 2 - 150, y_pos + 30, f"Speed: {ship['speed']}", size=18)
            draw_text(WIDTH // 2 - 150, y_pos + 50, f"Lives: {ship['lives']}", size=18)
            draw_text(WIDTH // 2 - 150, y_pos + 70, f"Fire Rate: {100/ship['fire_rate']:.0f}%", size=18)
            
            if is_unlocked:
                draw_text(WIDTH // 2 + 50, y_pos, "OWNED", size=24)
            else:
                glPushMatrix()
                glTranslate(WIDTH // 2 + 50, HEIGHT - (y_pos + 10), 0)
                glScale(20, 20, 1)
                glEnable(GL_TEXTURE_2D)
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                glBindTexture(GL_TEXTURE_2D, coin_texture[0])
                glBegin(GL_QUADS)
                glTexCoord2f(0, 0); glVertex2f(-0.5, -0.5)
                glTexCoord2f(1, 0); glVertex2f(0.5, -0.5)
                glTexCoord2f(1, 1); glVertex2f(0.5, 0.5)
                glTexCoord2f(0, 1); glVertex2f(-0.5, 0.5)
                glEnd()
                glDisable(GL_TEXTURE_2D)
                glDisable(GL_BLEND)
                glPopMatrix()
                draw_text(WIDTH // 2 + 70, y_pos, str(ship["price"]), size=24)
        
        pygame.display.flip()
        clock.tick(30)