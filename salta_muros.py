import pygame
import sys
import random

# 1. Inicializar Pygame
pygame.init()

# 2. Configuración de la Pantalla
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 450 
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Plataformas: Puntuación y Game Over")

# Colores y Configuración Global
SKY_BLUE = (135, 206, 235)
GROUND_GREEN = (0, 150, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
PLAYER_COLOR = (0, 0, 255)
OBSTACLE_COLOR = (255, 165, 0)
IMAGE_SIZE = (40, 40)
SCROLL_SPEED = 6 

# --- Estado y Estadísticas del Juego ---
GAME_STATE = "MENU" # Puede ser "MENU", "PLAYING", o "GAME_OVER"
score = 0
deaths = 0 # Nuevo contador de veces que el jugador ha perdido
obstacle_passed = False # Flag para contar la puntuación

# 3. Cargar Gráficos y Fuentes (Robusto ante FileNotFoundError)
try:
    player_img = pygame.image.load('jugador.png').convert_alpha()
    player_img = pygame.transform.scale(player_img, IMAGE_SIZE)
    
    obstacle_img = pygame.image.load('obstaculo.png').convert_alpha()
    obstacle_img = pygame.transform.scale(obstacle_img, IMAGE_SIZE)
    
except pygame.error as e:
    print(f"ATENCIÓN: {e}. No se encontraron las imágenes. Usando cuadrados de color.")
    player_img = pygame.Surface(IMAGE_SIZE)
    player_img.fill(PLAYER_COLOR) 
    obstacle_img = pygame.Surface(IMAGE_SIZE)
    obstacle_img.fill(OBSTACLE_COLOR) 

# Fuentes
font_small = pygame.font.Font(None, 30)
font_medium = pygame.font.Font(None, 40)
font_large = pygame.font.Font(None, 74)


# 4. Configuración del Jugador
player_rect = player_img.get_rect()
player_rect.x = 100
player_rect.y = SCREEN_HEIGHT - player_rect.height - 40 

# Variables de Salto y Gravedad
y_velocity = 0
gravity = 1
is_jumping = False
jump_force = -18

# 5. Definición de Plataformas y Obstáculos
platforms = [
    pygame.Rect(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40)
]

obstacle_rect = obstacle_img.get_rect()
obstacle_rect.x = SCREEN_WIDTH + 500
obstacle_rect.y = SCREEN_HEIGHT - obstacle_rect.height - 40


# --- Funciones Esenciales de Control ---

def draw_text(text, font, color, surface, x, y, centered=True):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    if centered:
        textrect.center = (x, y)
    else:
        textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def reset_game():
    global y_velocity, is_jumping, score, obstacle_passed
    # Reinicia la posición y la física
    player_rect.x = 100
    player_rect.y = SCREEN_HEIGHT - player_rect.height - 40 
    y_velocity = 0
    is_jumping = False
    
    # Reinicia el obstáculo fuera de pantalla
    obstacle_rect.x = SCREEN_WIDTH + random.randint(300, 600)
    
    # Solo reinicia la puntuación si el estado anterior fue 'GAME_OVER'
    # Si volvemos desde el menú, la puntuación se reinicia a 0.
    if GAME_STATE == "MENU":
        score = 0
    
    obstacle_passed = False

def main_menu():
    global GAME_STATE
    
    while GAME_STATE == "MENU":
        screen.fill(SKY_BLUE)
        
        draw_text('PLATAFORMAS CLÁSICO', font_large, BLACK, screen, SCREEN_WIDTH // 2, 100)
        draw_text('Derrotas: ' + str(deaths), font_medium, RED, screen, SCREEN_WIDTH // 2, 170)
        
        draw_text('Pulsa ESPACIO para JUGAR', font_medium, BLACK, screen, SCREEN_WIDTH // 2, 280)
        draw_text('Controles: ESPACIO o FLECHA ARRIBA para Saltar', font_small, BLACK, screen, SCREEN_WIDTH // 2, 320)
        
        pygame.draw.rect(screen, GROUND_GREEN, platforms[0])
        screen.blit(player_img, player_rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    GAME_STATE = "PLAYING"
                    reset_game()
                    return

def game_over_screen():
    global GAME_STATE
    global deaths
    
    # Aumentar contador de derrotas
    deaths += 1
    
    # Mostrar la pantalla de Muerte por un momento
    screen.fill(BLACK)
    draw_text('¡HAS MUERTO!', font_large, RED, screen, SCREEN_WIDTH // 2, 150)
    draw_text(f'Puntuación Final: {score}', font_medium, WHITE, screen, SCREEN_WIDTH // 2, 250)
    draw_text('Pulsa ESPACIO para continuar...', font_small, WHITE, screen, SCREEN_WIDTH // 2, 350)
    pygame.display.flip()
    
    wait_for_input = True
    while wait_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    GAME_STATE = "MENU"
                    wait_for_input = False


# --- Funciones de Juego ---

def apply_gravity_and_check_floor():
    global y_velocity, is_jumping
    
    y_velocity += gravity
    player_rect.y += y_velocity
    
    for platform in platforms:
        if player_rect.colliderect(platform):
            if y_velocity > 0:
                player_rect.bottom = platform.top 
                y_velocity = 0
                is_jumping = False
                
def update_world():
    global score, obstacle_passed
    
    # Mover el obstáculo hacia la izquierda
    obstacle_rect.x -= SCROLL_SPEED
    
    # Lógica de Puntuación
    if obstacle_rect.right < player_rect.left and not obstacle_passed:
        score += 1
        obstacle_passed = True
        
    # Si el obstáculo sale de la pantalla, reiniciarlo y preparar para la siguiente puntuación
    if obstacle_rect.right < 0:
        obstacle_rect.x = SCREEN_WIDTH + random.randint(400, 800)
        obstacle_passed = False # Resetea la bandera para poder contar el siguiente obstáculo


def check_obstacle_collision():
    if player_rect.colliderect(obstacle_rect):
        return True
    return False

def draw_hud():
    # Dibuja la puntuación y las derrotas en la parte superior
    score_text = f"Puntuación: {score}"
    deaths_text = f"Derrotas: {deaths}"
    
    draw_text(score_text, font_medium, BLACK, screen, 10, 10, centered=False)
    draw_text(deaths_text, font_medium, RED, screen, SCREEN_WIDTH - 10, 10, centered=False) # Se ajusta la posición x manualmente para que quede a la derecha

# 7. Bucle Principal del Juego
clock = pygame.time.Clock()

while True:
    if GAME_STATE == "MENU":
        main_menu()
    
    elif GAME_STATE == "GAME_OVER":
        game_over_screen()
    
    elif GAME_STATE == "PLAYING":
        
        # --- 7. Manejo de Eventos ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_SPACE or event.key == pygame.K_UP) and not is_jumping:
                    is_jumping = True
                    y_velocity = jump_force 
            
        # --- 8. Lógica del Juego ---
        
        apply_gravity_and_check_floor()
        
        update_world()
            
        # Colisión
        if check_obstacle_collision():
            GAME_STATE = "GAME_OVER" # Cambia el estado a la pantalla de muerte
            
        # --- 9. Dibujo ---

        screen.fill(SKY_BLUE)
        
        pygame.draw.rect(screen, GROUND_GREEN, platforms[0])
        
        screen.blit(obstacle_img, obstacle_rect)
        
        screen.blit(player_img, player_rect)
        
        # Dibujar HUD (Puntuación y Derrotas)
        draw_hud()

        # --- 10. Actualizar ---
        pygame.display.flip()
        clock.tick(60)