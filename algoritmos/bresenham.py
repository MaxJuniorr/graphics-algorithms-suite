# algoritmos/bresenham.py

def calcular_linha_bresenham(ponto_inicial, ponto_final):
    """
    Calcula todos os pontos (pixels) de uma linha entre dois pontos
    usando o algoritmo de Bresenham. Funciona para todos os octantes.

    Args:
        ponto_inicial (tuple): Uma tupla (x1, y1) com as coordenadas do ponto inicial.
        ponto_final (tuple): Uma tupla (x2, y2) com as coordenadas do ponto final.

    Returns:
        list: Uma lista de tuplas [(x, y), ...], representando os pixels da linha.
    """
    x1, y1 = ponto_inicial
    x2, y2 = ponto_final
    
    pixels = []
    
    # Deltas
    dx = x2 - x1
    dy = y2 - y1

    # Define os sinais do incremento
    sinal_x = 1 if dx > 0 else -1
    sinal_y = 1 if dy > 0 else -1
    
    # Trabalhamos com os valores absolutos para o cálculo
    dx = abs(dx)
    dy = abs(dy)

    # Verifica se a linha é mais "deitada" (predominância de X) ou "em pé" (predominância de Y)
    if dx > dy:
        # A variação em X é maior
        p = 2 * dy - dx
        x, y = x1, y1
        for _ in range(dx + 1):
            pixels.append((x, y))
            if p >= 0:
                y += sinal_y
                p -= 2 * dx
            x += sinal_x
            p += 2 * dy
    else:
        # A variação em Y é maior ou igual
        p = 2 * dx - dy
        x, y = x1, y1
        for _ in range(dy + 1):
            pixels.append((x, y))
            if p >= 0:
                x += sinal_x
                p -= 2 * dy
            y += sinal_y
            p += 2 * dx
            
    return pixels