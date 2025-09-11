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

def sutherland_hodgman_clip(subject_polygon, clip_window):
    """
    Recorta um polígono usando o algoritmo de Sutherland-Hodgman.

    Args:
        subject_polygon (list): Lista de vértices do polígono a ser recortado.
        clip_window (tuple): Tupla (xmin, ymin, xmax, ymax) da janela de recorte.

    Returns:
        list: Lista de vértices do polígono recortado.
    """
    xmin, ymin, xmax, ymax = clip_window
    
    def clip_left(vertices):
        clipped = []
        for i in range(len(vertices)):
            p1 = vertices[i]
            p2 = vertices[(i + 1) % len(vertices)]
            p1_inside = p1[0] >= xmin
            p2_inside = p2[0] >= xmin

            if p1_inside and p2_inside: # Ambos dentro
                clipped.append(p2)
            elif p1_inside and not p2_inside: # P1 dentro, P2 fora
                # Interseção
                x = xmin
                y = p1[1] + (p2[1] - p1[1]) * (xmin - p1[0]) / (p2[0] - p1[0])
                clipped.append((round(x), round(y)))
            elif not p1_inside and p2_inside: # P1 fora, P2 dentro
                # Interseção
                x = xmin
                y = p1[1] + (p2[1] - p1[1]) * (xmin - p1[0]) / (p2[0] - p1[0])
                clipped.append((round(x), round(y)))
                clipped.append(p2)
        return clipped

    def clip_right(vertices):
        clipped = []
        for i in range(len(vertices)):
            p1 = vertices[i]
            p2 = vertices[(i + 1) % len(vertices)]
            p1_inside = p1[0] <= xmax
            p2_inside = p2[0] <= xmax

            if p1_inside and p2_inside:
                clipped.append(p2)
            elif p1_inside and not p2_inside:
                x = xmax
                y = p1[1] + (p2[1] - p1[1]) * (xmax - p1[0]) / (p2[0] - p1[0])
                clipped.append((round(x), round(y)))
            elif not p1_inside and p2_inside:
                x = xmax
                y = p1[1] + (p2[1] - p1[1]) * (xmax - p1[0]) / (p2[0] - p1[0])
                clipped.append((round(x), round(y)))
                clipped.append(p2)
        return clipped

    def clip_bottom(vertices):
        clipped = []
        for i in range(len(vertices)):
            p1 = vertices[i]
            p2 = vertices[(i + 1) % len(vertices)]
            p1_inside = p1[1] >= ymin
            p2_inside = p2[1] >= ymin

            if p1_inside and p2_inside:
                clipped.append(p2)
            elif p1_inside and not p2_inside:
                y = ymin
                x = p1[0] + (p2[0] - p1[0]) * (ymin - p1[1]) / (p2[1] - p1[1])
                clipped.append((round(x), round(y)))
            elif not p1_inside and p2_inside:
                y = ymin
                x = p1[0] + (p2[0] - p1[0]) * (ymin - p1[1]) / (p2[1] - p1[1])
                clipped.append((round(x), round(y)))
                clipped.append(p2)
        return clipped

    def clip_top(vertices):
        clipped = []
        for i in range(len(vertices)):
            p1 = vertices[i]
            p2 = vertices[(i + 1) % len(vertices)]
            p1_inside = p1[1] <= ymax
            p2_inside = p2[1] <= ymax

            if p1_inside and p2_inside:
                clipped.append(p2)
            elif p1_inside and not p2_inside:
                y = ymax
                x = p1[0] + (p2[0] - p1[0]) * (ymax - p1[1]) / (p2[1] - p1[1])
                clipped.append((round(x), round(y)))
            elif not p1_inside and p2_inside:
                y = ymax
                x = p1[0] + (p2[0] - p1[0]) * (ymax - p1[1]) / (p2[1] - p1[1])
                clipped.append((round(x), round(y)))
                clipped.append(p2)
        return clipped

    clipped_polygon = clip_left(subject_polygon)
    clipped_polygon = clip_right(clipped_polygon)
    clipped_polygon = clip_bottom(clipped_polygon)
    clipped_polygon = clip_top(clipped_polygon)

    return clipped_polygon
