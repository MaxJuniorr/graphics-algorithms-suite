"""Implementação de algoritmos de recorte de linha e polígono."""

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

    # Normaliza entrada: remove fechamento duplicado se existir
    if subject_polygon and len(subject_polygon) >= 2 and subject_polygon[0] == subject_polygon[-1]:
        subject_polygon = subject_polygon[:-1]
    # Recortes sucessivos
    clipped_polygon = clip_left(subject_polygon)
    clipped_polygon = clip_right(clipped_polygon)
    clipped_polygon = clip_bottom(clipped_polygon)
    clipped_polygon = clip_top(clipped_polygon)

    # Remove vértices redundantes consecutivos (ex.: iguais)
    if clipped_polygon:
        compact = [clipped_polygon[0]]
        for p in clipped_polygon[1:]:
            if p != compact[-1]:
                compact.append(p)
        clipped_polygon = compact

    # Garante polígono fechado quando há pelo menos 2 vértices
    if clipped_polygon and len(clipped_polygon) >= 2 and clipped_polygon[0] != clipped_polygon[-1]:
        clipped_polygon.append(clipped_polygon[0])

    return clipped_polygon


def suth_hodgman_clip_convexo(subject_polygon, clip_polygon):
    """Recorta um polígono arbitrário contra uma janela de recorte poligonal convexa.

    subject_polygon: lista de (x,y) do polígono a recortar (aberto ou fechado).
    clip_polygon: lista de (x,y) do polígono convexo da janela (aberto ou fechado).
    Retorna lista de (x,y) do polígono resultante (fechado se houver pelo menos 2 vértices).
    """
    from utils.geometria import garantir_ccw

    def intersect(p1, p2, q1, q2):
        # Interseção de segmentos p1->p2 e q1->q2 (linhas infinitas)
        x1, y1 = p1; x2, y2 = p2
        x3, y3 = q1; x4, y4 = q2
        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if den == 0:
            return p2  # paralelos/colineares, retorna extremo para manter continuidade
        px = ((x1*y2 - y1*x2)*(x3 - x4) - (x1 - x2)*(x3*y4 - y3*x4)) / den
        py = ((x1*y2 - y1*x2)*(y3 - y4) - (y1 - y2)*(x3*y4 - y3*x4)) / den
        return (round(px), round(py))

    def inside(p, a, b):
        # Considerando borda a->b com polígono clip CCW, lado interno é à esquerda (cross >= 0)
        ax, ay = a; bx, by = b; px, py = p
        return (bx - ax) * (py - ay) - (by - ay) * (px - ax) >= 0

    # Normaliza: remove fechamento duplicado
    S = subject_polygon[:]
    if len(S) >= 2 and S[0] == S[-1]:
        S = S[:-1]
    C = clip_polygon[:]
    if len(C) >= 2 and C[0] == C[-1]:
        C = C[:-1]
    if len(C) < 3 or len(S) < 3:
        return []
    C = garantir_ccw(C)

    output = S
    for i in range(len(C)):
        a = C[i]
        b = C[(i + 1) % len(C)]
        input_list = output
        if not input_list:
            break
        output = []
        for j in range(len(input_list)):
            s = input_list[j]
            e = input_list[(j + 1) % len(input_list)]
            s_in = inside(s, a, b)
            e_in = inside(e, a, b)
            if s_in and e_in:
                output.append(e)
            elif s_in and not e_in:
                output.append(intersect(s, e, a, b))
            elif (not s_in) and e_in:
                output.append(intersect(s, e, a, b))
                output.append(e)
            # ambos fora: adiciona nada

    # Remove duplicatas consecutivas
    if output:
        compact = [output[0]]
        for p in output[1:]:
            if p != compact[-1]:
                compact.append(p)
        output = compact

    if output and len(output) >= 2 and output[0] != output[-1]:
        output.append(output[0])
    return output
