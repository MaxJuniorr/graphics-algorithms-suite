# algoritmos/curvas_bezier.py
from .bresenham import calcular_linha_bresenham

def calcular_pontos_bezier_cubica(p0, p1, p2, p3, num_segmentos=20):
    """
    Calcula uma lista de pontos ao longo de uma Curva de Bézier Cúbica.

    Args:
        p0, p1, p2, p3 (tuple): Pontos inicial, de controle 1, de controle 2 e final.
        num_segmentos (int): A "resolução" da curva. Mais segmentos = mais suave.

    Returns:
        list: Uma lista de pontos [(x, y), ...] que formam a curva.
    """
    pontos_da_curva = []
    
    # O loop vai de 0 a num_segmentos, calculando o valor de 't' de 0.0 a 1.0
    for i in range(num_segmentos + 1):
        t = i / num_segmentos
        
        # Fórmula da Curva de Bézier Cúbica
        um_menos_t = 1 - t
        
        # Coeficientes da fórmula
        b0 = um_menos_t ** 3
        b1 = 3 * t * (um_menos_t ** 2)
        b2 = 3 * (t ** 2) * um_menos_t
        b3 = t ** 3

        # Calcula o ponto (x, y) para o valor de 't' atual
        x = round(b0 * p0[0] + b1 * p1[0] + b2 * p2[0] + b3 * p3[0])
        y = round(b0 * p0[1] + b1 * p1[1] + b2 * p2[1] + b3 * p3[1])
        
        # Evita adicionar pontos duplicados
        if not pontos_da_curva or pontos_da_curva[-1] != (x, y):
            pontos_da_curva.append((x, y))
            
    return pontos_da_curva


def rasterizar_curva_bezier(p0, p1, p2, p3, num_segmentos=20):
    """
    Calcula os pontos da curva e usa Bresenham para gerar os pixels.

    Returns:
        list: A lista final de pixels a serem desenhados.
    """
    pixels_finais = []
    
    # 1. Calcula os vértices da polilinha que aproxima a curva
    pontos_da_curva = calcular_pontos_bezier_cubica(p0, p1, p2, p3, num_segmentos)
    
    # 2. Usa Bresenham para desenhar linhas entre cada par de pontos consecutivos
    for i in range(len(pontos_da_curva) - 1):
        ponto_atual = pontos_da_curva[i]
        proximo_ponto = pontos_da_curva[i+1]
        
        segmento = calcular_linha_bresenham(ponto_atual, proximo_ponto)
        pixels_finais.extend(segmento)
        
    # Remove duplicados que podem ocorrer nas junções dos segmentos
    return list(set(pixels_finais))