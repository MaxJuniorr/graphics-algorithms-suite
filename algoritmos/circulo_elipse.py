# algoritmos/circulo_elipse.py

def calcular_circulo(centro, raio):
    """
    Calcula os pixels de um círculo usando o Algoritmo do Ponto Médio.

    Args:
        centro (tuple): Uma tupla (xc, yc) com as coordenadas do centro.
        raio (int): O raio do círculo.

    Returns:
        list: Uma lista de tuplas [(x, y), ...], representando os pixels do círculo.
    """
    xc, yc = centro
    x = 0
    y = raio
    p = 1 - raio  # Parâmetro de decisão inicial

    pixels = []

    def adicionar_pixels_simetricos(x, y):
        """Adiciona os 8 pixels simétricos para o octante calculado."""
        pixels.append((xc + x, yc + y))
        pixels.append((xc - x, yc + y))
        pixels.append((xc + x, yc - y))
        pixels.append((xc - x, yc - y))
        pixels.append((xc + y, yc + x))
        pixels.append((xc - y, yc + x))
        pixels.append((xc + y, yc - x))
        pixels.append((xc - y, yc - x))

    # O loop calcula os pixels para um octante, e a função acima espelha para os outros 7
    while x <= y:
        adicionar_pixels_simetricos(x, y)
        x += 1
        if p < 0:
            p += 2 * x + 1
        else:
            y -= 1
            p += 2 * (x - y) + 1
            
    return pixels

def calcular_elipse(centro, rx, ry):
    """
    Calcula os pixels de uma elipse usando o Algoritmo do Ponto Médio.

    Args:
        centro (tuple): Uma tupla (xc, yc) com as coordenadas do centro.
        rx (int): O raio no eixo X.
        ry (int): O raio no eixo Y.

    Returns:
        list: Uma lista de tuplas [(x, y), ...], representando os pixels da elipse.
    """
    xc, yc = centro
    pixels = []

    def adicionar_pixels_simetricos(x, y):
        """Adiciona os 4 pixels simétricos para o quadrante calculado."""
        pixels.append((xc + x, yc + y))
        pixels.append((xc - x, yc + y))
        pixels.append((xc + x, yc - y))
        pixels.append((xc - x, yc - y))

    # --- Região 1 ---
    x = 0
    y = ry
    p1 = (ry**2) - (rx**2 * ry) + (0.25 * rx**2)
    dx = 2 * ry**2 * x
    dy = 2 * rx**2 * y

    while dx < dy:
        adicionar_pixels_simetricos(x, y)
        x += 1
        dx = 2 * ry**2 * x
        if p1 < 0:
            p1 += dx + (ry**2)
        else:
            y -= 1
            dy = 2 * rx**2 * y
            p1 += dx - dy + (ry**2)

    # --- Região 2 ---
    p2 = (ry**2 * (x + 0.5)**2) + (rx**2 * (y - 1)**2) - (rx**2 * ry**2)
    
    while y >= 0:
        adicionar_pixels_simetricos(x, y)
        y -= 1
        dy = 2 * rx**2 * y
        if p2 > 0:
            p2 += (rx**2) - dy
        else:
            x += 1
            dx = 2 * ry**2 * x
            p2 += dx - dy + (rx**2)
            
    return pixels