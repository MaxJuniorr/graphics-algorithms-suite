import math
from typing import List, Tuple

"""
Roteiro de apresentação – Transformações 2D (Translação, Escala, Rotação)

1) Modelo
   - Representamos pontos como tuplas (x, y) e aplicamos transformações básicas.

2) Ideias
   - Transladar: somar (tx, ty) a cada ponto.
   - Escalar: mover ponto em relação a um centro fixo (cx, cy) por fatores (sx, sy).
   - Rotacionar: mover em torno de um pivô (px, py) pelo ângulo dado.

3) Observações
   - Arredondamento ao final para rasterização.
"""

def round_half_up_simple(n):
    """Arredonda n para o inteiro mais próximo com a regra half-up."""
    return math.floor(n + 0.5)

Point = Tuple[int, int]

def transladar(pontos: List[Point], tx: int, ty: int) -> List[Point]:
    """
    Aplica uma translação a uma lista de pontos.

    Args:
        pontos: A lista de vértices (x, y) do polígono.
        tx: O deslocamento na direção x.
        ty: O deslocamento na direção y.

    Returns:
        Uma nova lista de pontos transladados.
    """
    # Compreensão de lista: para cada p=(x,y), soma (tx,ty)
    return [(p[0] + tx, p[1] + ty) for p in pontos]

def escalar(pontos: List[Point], sx: float, sy: float, ponto_fixo: Point) -> List[Point]:
    """
    Aplica uma escala a uma lista de pontos em relação a um ponto fixo.

    Args:
        pontos: A lista de vértices (x, y) do polígono.
        sx: O fator de escala na direção x.
        sy: O fator de escala na direção y.
        ponto_fixo: O ponto (cx, cy) que permanece inalterado após a escala.

    Returns:
        Uma nova lista de pontos escalados.
    """
    cx, cy = ponto_fixo              # centro fixo da transformação
    pontos_escalados = []            # resultado acumulado
    # Loop sobre cada ponto p=(x,y) e aplica fórmula de escala relativa ao centro (cx,cy)
    for p in pontos:
        x, y = p
        novo_x = cx + (x - cx) * sx
        novo_y = cy + (y - cy) * sy
        pontos_escalados.append((round(novo_x), round(novo_y)))  # arredonda para grid
    return pontos_escalados

def rotacionar(pontos: List[Point], angulo: float, pivo: Point) -> List[Point]:
    """
    Aplica uma rotação a uma lista de pontos em torno de um ponto de pivô.

    Args:
        pontos: A lista de vértices (x, y) do polígono.
        angulo: O ângulo de rotação em graus.
        pivo: O ponto (px, py) sobre o qual a rotação é aplicada.

    Returns:
        Uma nova lista de pontos rotacionados.
    """
    px, py = pivo                    # pivô de rotação
    radianos = math.radians(angulo)  # ângulo em radianos
    cos_a = math.cos(radianos)
    sin_a = math.sin(radianos)
    
    pontos_rotacionados = []         # lista resultado
    # Loop: translada para origem, aplica rotação, translada de volta e arredonda
    for p in pontos:
        x, y = p
        # Transladar para a origem
        x_temp = x - px
        y_temp = y - py
        
        # Rotacionar em torno da origem
        novo_x_temp = x_temp * cos_a - y_temp * sin_a
        novo_y_temp = x_temp * sin_a + y_temp * cos_a
        
        # Transladar de volta para o pivô
        novo_x = novo_x_temp + px
        novo_y = novo_y_temp + py
        
        pontos_rotacionados.append((round_half_up_simple(novo_x), round_half_up_simple(novo_y)))
    return pontos_rotacionados
