import math
from typing import List, Tuple

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
    cx, cy = ponto_fixo
    pontos_escalados = []
    for p in pontos:
        x, y = p
        novo_x = cx + (x - cx) * sx
        novo_y = cy + (y - cy) * sy
        pontos_escalados.append((round(novo_x), round(novo_y)))
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
    px, py = pivo
    radianos = math.radians(angulo)
    cos_a = math.cos(radianos)
    sin_a = math.sin(radianos)
    
    pontos_rotacionados = []
    for p in pontos:
        x, y = p
        # Transladar para a origem
        x_temp = x - px
        y_temp = y - py
        
        # Rotacionar
        novo_x_temp = x_temp * cos_a - y_temp * sin_a
        novo_y_temp = x_temp * sin_a + y_temp * cos_a
        
        # Transladar de volta
        novo_x = novo_x_temp + px
        novo_y = novo_y_temp + py
        
        pontos_rotacionados.append((round(novo_x), round(novo_y)))
    return pontos_rotacionados
