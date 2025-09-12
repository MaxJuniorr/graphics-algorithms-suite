from typing import List, Tuple
from algoritmos.bresenham import calcular_linha_bresenham

"""
Roteiro de apresentação – Polilinha

1) Problema
   - Ligar uma sequência de vértices (x,y) com segmentos de reta discretos.

2) Ideia
   - Para cada par consecutivo de pontos, usamos Bresenham para rasterizar a linha.
   - Concatenamos todos os pixels dos segmentos.

3) Observações
   - Não removemos duplicatas entre segmentos; se quiser, pode deduplicar depois.
   - Se houver menos de 2 pontos, não há segmento a rasterizar.
"""

def rasterizar_polilinha(pontos: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """
    Rasteriza uma polilinha conectando uma lista de pontos em sequência.

    Args:
        pontos: Uma lista de tuplas (x, y) representando os vértices da polilinha.

    Returns:
        Uma lista de pixels (x, y) que formam a polilinha.
    """
    pixels_total = []  # acumula todos os pixels dos segmentos consecutivos
    if len(pontos) < 2:
        return []      # menos de 2 pontos => nada a ligar

    # Loop de segmentos: conecta ponto i ao ponto i+1
    for i in range(len(pontos) - 1):
        ponto_inicial = pontos[i]      # vértice atual
        ponto_final = pontos[i + 1]    # próximo vértice
        # Rasteriza o segmento com Bresenham e adiciona ao total
        pixels_linha = calcular_linha_bresenham(ponto_inicial, ponto_final)
        pixels_total.extend(pixels_linha)
    
    return pixels_total
