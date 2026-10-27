import pygame
import random
import sys

# Configuración de ventana
ANCHO = 1024
ALTO = 680
FPS_DEFECTO = 12

# Paleta Pixel Art 
CIELO = (32, 28, 44)
SUELO = (70, 110, 55)
SUELO_LINEA = (45, 80, 35)

C_PIEL = (245, 185, 30)
C_SOMBRA = (200, 135, 15)
C_MANCHA = (135, 55, 15)
C_HOCICO = (220, 165, 100)
C_LINEA = (30, 20, 10)

# Colores de Glows para el algoritmo
C_EVAL = (255, 65, 65)
C_LIMITE = (65, 140, 255)
C_ORDENADO = (70, 220, 110)

def generar_manada(n_elementos):
    """Genera la manada desordenada con 5 alturas únicas (Few Unique)."""
    alturas = [1, 2, 3, 4, 5]
    array = [random.choice(alturas) for _ in range(n_elementos)]
    random.shuffle(array)
    return array

def quick_sort_3way(arr, low, high, stats):
    """Algoritmo Quick Sort de 3 vías con métricas de rendimiento."""
    if low >= high:
        return
    lt = low
    i = low + 1
    gt = high
    v = arr[low]

    while i <= gt:
        stats['comparaciones'] += 1
        if arr[i] < v:
            stats['intercambios'] += 1
            arr[lt], arr[i] = arr[i], arr[lt]
            lt += 1
            i += 1
        else:
            stats['comparaciones'] += 1
            if arr[i] > v:
                stats['intercambios'] += 1
                arr[gt], arr[i] = arr[i], arr[gt]
                gt -= 1
            else:
                i += 1
        yield arr, lt, i, gt

    yield from quick_sort_3way(arr, low, lt - 1, stats)
    yield from quick_sort_3way(arr, gt + 1, high, stats)

def renderizar_jirafa_pixel(nivel, estado, p_size=3):
    """Construye un sprite Pixel Art detallado mediante rejilla de píxeles."""
    ancho_grid = 18
    alto_cuello = 4 + (nivel * 6)
    alto_grid = 14 + alto_cuello

    surf = pygame.Surface((ancho_grid * p_size, alto_grid * p_size), pygame.SRCALPHA)

    piel, mancha = C_PIEL, C_MANCHA
    if estado == 'evaluando':
        piel, mancha = C_EVAL, (140, 0, 0)
    elif estado == 'limite':
        piel, mancha = C_LIMITE, (10, 40, 150)
    elif estado == 'ordenado':
        piel, mancha = C_ORDENADO, (20, 120, 40)

    def px(gx, gy, col):
        pygame.draw.rect(surf, col, (gx * p_size, gy * p_size, p_size, p_size))

    y_base = alto_grid - 1

    # Patas y Pezuñas
    for x in [3, 5, 10, 12]:
        px(x, y_base, C_LINEA)
        px(x, y_base - 1, C_SOMBRA)
        px(x, y_base - 2, piel)
        px(x, y_base - 3, piel)

    # Cuerpo
    y_cuerpo = y_base - 4
    for bx in range(2, 14):
        for by in range(y_cuerpo - 4, y_cuerpo + 1):
            px(bx, by, piel)
    for bx in range(2, 14):
        px(bx, y_cuerpo, C_SOMBRA)
    px(4, y_cuerpo - 2, mancha)
    px(5, y_cuerpo - 2, mancha)
    px(8, y_cuerpo - 3, mancha)
    px(9, y_cuerpo - 3, mancha)

    # Cola
    px(1, y_cuerpo - 3, C_LINEA)
    px(0, y_cuerpo - 2, mancha)

    # Cuello Pixel Art
    x_cuello = 10
    y_inicio_cuello = y_cuerpo - 4
    y_top_cuello = y_inicio_cuello - alto_cuello

    for cy in range(y_top_cuello, y_inicio_cuello):
        px(x_cuello, cy, piel)
        px(x_cuello + 1, cy, piel)
        px(x_cuello + 2, cy, C_SOMBRA)

    for cy in range(y_top_cuello + 2, y_inicio_cuello - 1, 4):
        px(x_cuello + 1, cy, mancha)
        px(x_cuello + 1, cy + 1, mancha)

    # Cabeza y Hocico
    y_cabeza = y_top_cuello - 3
    for hx in range(9, 16):
        for hy in range(y_cabeza, y_cabeza + 3):
            px(hx, hy, piel)

    px(14, y_cabeza + 1, C_HOCICO)
    px(15, y_cabeza + 1, C_HOCICO)
    px(14, y_cabeza + 2, C_HOCICO)

    # Ojo y Cuernos
    px(12, y_cabeza + 1, (255, 255, 255))
    px(13, y_cabeza + 1, C_LINEA)
    px(10, y_cabeza - 1, C_SOMBRA)
    px(10, y_cabeza - 2, mancha)
    px(12, y_cabeza - 1, C_SOMBRA)
    px(12, y_cabeza - 2, mancha)

    return surf

def main():
    pygame.init()
    
    # Forzamos centrado de ventana y evento básico para asegurar la apertura
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Quick Sort 3-Way: Pixel Art Giraffe Edition")
    reloj = pygame.time.Clock()

    # Uso de la fuente interna por defecto
    fuente_m = pygame.font.Font(None, 24)
    fuente_g = pygame.font.Font(None, 34)

    # Pre-generación del caché de sprites (garantiza fluidez total)
    cache_sprites = {}
    for niv in range(1, 6):
        for est in ['normal', 'evaluando', 'limite', 'ordenado']:
            cache_sprites[(niv, est)] = renderizar_jirafa_pixel(niv, est)

    n_jirafas = 22
    fps = FPS_DEFECTO
    pausado = False
    ordenado = False

    stats = {'comparaciones': 0, 'intercambios': 0}
    arr = generar_manada(n_jirafas)
    algoritmo = quick_sort_3way(arr, 0, len(arr) - 1, stats)
    lt, i, gt = -1, -1, -1

    while True:
        avanzar_frame = False

        # Procesamiento explícito de eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE and not ordenado:
                    pausado = not pausado
                elif evento.key == pygame.K_r:
                    arr = generar_manada(n_jirafas)
                    stats = {'comparaciones': 0, 'intercambios': 0}
                    algoritmo = quick_sort_3way(arr, 0, len(arr) - 1, stats)
                    ordenado = False
                    pausado = False
                    lt, i, gt = -1, -1, -1
                elif evento.key == pygame.K_UP:
                    fps = min(60, fps + 4)
                elif evento.key == pygame.K_DOWN:
                    fps = max(1, fps - 4)
                elif evento.key == pygame.K_n and pausado and not ordenado:
                    avanzar_frame = True

        if (not pausado or avanzar_frame) and not ordenado:
            try:
                arr, lt, i, gt = next(algoritmo)
            except StopIteration:
                ordenado = True
                lt, i, gt = -1, -1, -1

        # Renderizado de fondo estilo retro
        pantalla.fill(CIELO)
        y_suelo = ALTO - 70
        pygame.draw.rect(pantalla, SUELO, (0, y_suelo, ANCHO, 70))
        pygame.draw.rect(pantalla, SUELO_LINEA, (0, y_suelo, ANCHO, 6))

        # Dibujar jirafas alineadas al suelo
        ancho_slot = ANCHO / len(arr)
        for indice, nivel in enumerate(arr):
            estado = 'normal'
            if ordenado:
                estado = 'ordenado'
            elif indice == i:
                estado = 'evaluando'
            elif indice == lt or indice == gt:
                estado = 'limite'

            sprite = cache_sprites[(nivel, estado)]
            pos_x = int(indice * ancho_slot + (ancho_slot - sprite.get_width()) / 2)
            pos_y = y_suelo - sprite.get_height()
            pantalla.blit(sprite, (pos_x, pos_y))

        # Panel HUD superior
        pygame.draw.rect(pantalla, (20, 18, 28), (0, 0, ANCHO, 85))
        pygame.draw.line(pantalla, (80, 75, 100), (0, 85), (ANCHO, 85), 2)

        txt_comp = fuente_m.render(f"Lecturas / Comparaciones: {stats['comparaciones']}", True, (240, 240, 240))
        txt_swaps = fuente_m.render(f"Intercambios / Swaps: {stats['intercambios']}", True, (245, 185, 30))
        txt_fps = fuente_m.render(f"Velocidad: {fps} FPS", True, (100, 200, 255))

        pantalla.blit(txt_comp, (25, 15))
        pantalla.blit(txt_swaps, (25, 38))
        pantalla.blit(txt_fps, (25, 60))

        # Indicador de estado
        if ordenado:
            txt_estado = fuente_g.render("¡MANADA ORDENADA!", True, C_ORDENADO)
        elif pausado:
            txt_estado = fuente_g.render("PAUSADO", True, (255, 90, 90))
        else:
            txt_estado = fuente_g.render("ORDENANDO...", True, (255, 255, 255))

        pantalla.blit(txt_estado, (420, 15))

        txt_ctrl1 = fuente_m.render("[ESPACIO] Pausa/Reanudar   [R] Reiniciar   [N] Paso a paso", True, (180, 180, 190))
        txt_ctrl2 = fuente_m.render("[FLECHAS] Cambiar velocidad FPS", True, (180, 180, 190))
        pantalla.blit(txt_ctrl1, (420, 45))
        pantalla.blit(txt_ctrl2, (420, 65))

        pygame.display.flip()
        reloj.tick(fps)

if __name__ == "__main__":
    main()

