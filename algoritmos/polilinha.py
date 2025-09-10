from typing import List, Tuple
from algoritmos.bresenham import calcular_linha_bresenham

def rasterizar_polilinha(pontos: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """
    Rasteriza uma polilinha conectando uma lista de pontos em sequência.

    Args:
        pontos: Uma lista de tuplas (x, y) representando os vértices da polilinha.

    Returns:
        Uma lista de pixels (x, y) que formam a polilinha.
    """
    pixels_total = []
    if len(pontos) < 2:
        return []

    for i in range(len(pontos) - 1):
        ponto_inicial = pontos[i]
        ponto_final = pontos[i+1]
        pixels_linha = calcular_linha_bresenham(ponto_inicial, ponto_final)
        pixels_total.extend(pixels_linha)
    
    return pixels_total
