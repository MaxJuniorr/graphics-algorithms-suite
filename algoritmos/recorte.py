"""Implementação de algoritmos de recorte de linha."""

# Códigos de região para o algoritmo de Cohen-Sutherland
INSIDE = 0  # 0000
LEFT = 1    # 0001
RIGHT = 2   # 0010
BOTTOM = 4  # 0100
TOP = 8     # 1000

def _compute_outcode(x, y, xmin, ymin, xmax, ymax):
    """Calcula o código de região para um ponto."""
    code = INSIDE
    if x < xmin:
        code |= LEFT
    elif x > xmax:
        code |= RIGHT
    if y < ymin:
        code |= BOTTOM
    elif y > ymax:
        code |= TOP
    return code

def cohen_sutherland_clip(p1, p2, xmin, ymin, xmax, ymax):
    """
    Recorta uma linha (p1, p2) para uma janela de recorte retangular.

    Args:
        p1 (tuple): Ponto inicial da linha (x1, y1).
        p2 (tuple): Ponto final da linha (x2, y2).
        xmin (int): Coordenada X mínima da janela.
        ymin (int): Coordenada Y mínima da janela.
        xmax (int): Coordenada X máxima da janela.
        ymax (int): Coordenada Y máxima da janela.

    Returns:
        tuple: Uma tupla (p1, p2) com as novas coordenadas da linha recortada,
               ou None se a linha estiver completamente fora da janela.
    """
    x1, y1 = p1
    x2, y2 = p2
    outcode1 = _compute_outcode(x1, y1, xmin, ymin, xmax, ymax)
    outcode2 = _compute_outcode(x2, y2, xmin, ymin, xmax, ymax)
    accept = False

    while True:
        # Caso 1: Ambos os pontos dentro da janela (aceitação trivial)
        if not (outcode1 | outcode2):
            accept = True
            break
        # Caso 2: Ambos os pontos fora da mesma região (rejeição trivial)
        elif (outcode1 & outcode2):
            break
        # Caso 3: Pelo menos um ponto fora, precisa recortar
        else:
            x, y = 0, 0
            # Pega o ponto que está fora
            outcode_out = outcode1 if outcode1 else outcode2

            # Encontra o ponto de interseção
            # A linha é y = y1 + slope * (x - x1), x = x1 + (y - y1) / slope
            if outcode_out & TOP:
                x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
                y = ymax
            elif outcode_out & BOTTOM:
                x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
                y = ymin
            elif outcode_out & RIGHT:
                x = xmax
                y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
            elif outcode_out & LEFT:
                x = xmin
                y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)

            # Atualiza o ponto que estava fora com a nova interseção
            if outcode_out == outcode1:
                x1, y1 = round(x), round(y)
                outcode1 = _compute_outcode(x1, y1, xmin, ymin, xmax, ymax)
            else:
                x2, y2 = round(x), round(y)
                outcode2 = _compute_outcode(x2, y2, xmin, ymin, xmax, ymax)

    if accept:
        return ((x1, y1), (x2, y2))
    return None
