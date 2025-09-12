"""
Roteiro de apresentação – Recorte (Clipping)

1) Problema
    - Recortar primitivas (linhas/polígonos) para caber dentro de uma janela de visualização.

2) Linhas: Cohen–Sutherland (retângulo)
    - Atribui códigos de região (LEFT/RIGHT/BOTTOM/TOP); aceita/rejeita trivialmente ou intersecta iterativamente.
    - Vantagem: rápido para janelas retangulares; simples de implementar.

3) Polígonos: Sutherland–Hodgman
    - Recorta iterativamente contra cada borda do retângulo (ou polígono convexo).
    - Mantém a ordem dos vértices; produz polígono resultante.

4) Dicas de demonstração
    - Mostrar casos: aceitação trivial, rejeição trivial e recorte parcial.
    - Em polígonos, destacar a sequência de recortes (esquerda, direita, baixo, topo).
"""

# Códigos de região para o algoritmo de Cohen-Sutherland (bitmask de 4 bits)
# Bit 0 (1)  -> LEFT   : ponto está à esquerda de xmin
# Bit 1 (2)  -> RIGHT  : ponto está à direita de xmax
# Bit 2 (4)  -> BOTTOM : ponto está abaixo de ymin
# Bit 3 (8)  -> TOP    : ponto está acima de ymax
INSIDE = 0  # 0000 (dentro; nenhum bit setado)
LEFT = 1    # 0001
RIGHT = 2   # 0010
BOTTOM = 4  # 0100
TOP = 8     # 1000

def _compute_outcode(x, y, xmin, ymin, xmax, ymax):
    """Calcula o código de região (outcode) para um ponto.

    Parâmetros
    - x, y: coordenadas do ponto testado.
    - xmin, ymin, xmax, ymax: limites do retângulo de recorte.

    Retorno
    - code: inteiro com bits combinando LEFT/RIGHT/BOTTOM/TOP indicando fora de qual lado.
    """
    code = INSIDE  # começa assumindo "dentro" (sem bits setados)
    if x < xmin:        # à esquerda da janela
        code |= LEFT
    elif x > xmax:      # à direita da janela
        code |= RIGHT
    if y < ymin:        # abaixo da janela
        code |= BOTTOM
    elif y > ymax:      # acima da janela
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
    # Desempacota os pontos finais da linha
    x1, y1 = p1  # ponto inicial
    x2, y2 = p2  # ponto final
    # Códigos de região (onde cada ponto está em relação ao retângulo)
    outcode1 = _compute_outcode(x1, y1, xmin, ymin, xmax, ymax)
    outcode2 = _compute_outcode(x2, y2, xmin, ymin, xmax, ymax)
    accept = False  # flag de aceitação final

    # Loop principal de recorte iterativo:
    # - Invariante: (x1,y1) e (x2,y2) são os extremos atuais da linha possivelmente recortada.
    # - A cada iteração, aceitamos, rejeitamos, ou movemos um extremo para a interseção com a borda apropriada.
    # - Termina quando ambos os pontos estão dentro (aceitação trivial) ou quando compartilham um mesmo lado externo (rejeição trivial).
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
            x, y = 0, 0  # variáveis para coordenadas de interseção a calcular
            # Escolhe o "ponto fora" (aquele cujo outcode != INSIDE)
            outcode_out = outcode1 if outcode1 else outcode2  # se outcode1==0, pega outcode2

            # Encontra o ponto de interseção com a borda correspondente
            # A linha é y = y1 + slope * (x - x1), x = x1 + (y - y1) / slope
            if outcode_out & TOP:  # Interseção com a borda superior: y = ymax
                # Fórmula paramétrica da linha: y = y1 + m * (x - x1) -> rearranjada para x na interseção
                x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
                y = ymax
            elif outcode_out & BOTTOM:  # Interseção com a borda inferior: y = ymin
                x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
                y = ymin
            elif outcode_out & RIGHT:  # Interseção com a borda direita: x = xmax
                x = xmax
                y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
            elif outcode_out & LEFT:  # Interseção com a borda esquerda: x = xmin
                x = xmin
                y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)

            # Atualiza o ponto que estava fora com a nova interseção e recomputa código
            if outcode_out == outcode1:
                # substitui o ponto inicial pela interseção calculada
                x1, y1 = round(x), round(y)
                outcode1 = _compute_outcode(x1, y1, xmin, ymin, xmax, ymax)
            else:
                # substitui o ponto final pela interseção calculada
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
    # Limites da janela de recorte retangular
    xmin, ymin, xmax, ymax = clip_window  # valores inteiros ou floats; usamos arredondamento nas interseções
    
    def clip_left(vertices):
        # Recorta contra a borda esquerda x = xmin
        # vertices: lista [(x,y), ...] do polígono intermediário
        clipped = []
        # Loop sobre todas as arestas do polígono sujeito (p1->p2), fechando com módulo:
        # - Invariante: p1 é o vértice atual; p2 é o próximo (ou o primeiro se i for o último).
        # - Objetivo: decidir para cada aresta se estamos entrando/saindo da região válida e
        #   adicionar a interseção e/ou o vértice conforme os quatro casos de Sutherland–Hodgman.
        for i in range(len(vertices)):
            p1 = vertices[i]                   # vértice corrente
            p2 = vertices[(i + 1) % len(vertices)]  # próximo vértice (fecha ciclo com módulo)
            p1_inside = p1[0] >= xmin          # p1 está à direita/na borda esquerda?
            p2_inside = p2[0] >= xmin          # p2 está à direita/na borda esquerda?

            if p1_inside and p2_inside: # Ambos dentro: mantém p2
                clipped.append(p2)
            elif p1_inside and not p2_inside: # P1 dentro, P2 fora: guarda interseção
                x = xmin                                       # x na borda
                y = p1[1] + (p2[1] - p1[1]) * (xmin - p1[0]) / (p2[0] - p1[0])  # y da interseção
                clipped.append((round(x), round(y)))           # adiciona ponto de saída
            elif not p1_inside and p2_inside: # P1 fora, P2 dentro: interseção + p2
                x = xmin
                y = p1[1] + (p2[1] - p1[1]) * (xmin - p1[0]) / (p2[0] - p1[0])
                clipped.append((round(x), round(y)))          # ponto de entrada
                clipped.append(p2)                             # mantém p2 (dentro)
        return clipped

    def clip_right(vertices):
        # Recorta contra a borda direita x = xmax
        clipped = []
        # Loop sobre arestas p1->p2 do polígono atual, utilizando fechamento com módulo.
        # - Invariante: construímos "clipped" apenas com pontos dentro ou interseções.
        for i in range(len(vertices)):
            p1 = vertices[i]
            p2 = vertices[(i + 1) % len(vertices)]
            p1_inside = p1[0] <= xmax
            p2_inside = p2[0] <= xmax

            if p1_inside and p2_inside:  # Ambos dentro
                clipped.append(p2)
            elif p1_inside and not p2_inside:  # Saindo: adiciona interseção
                x = xmax
                y = p1[1] + (p2[1] - p1[1]) * (xmax - p1[0]) / (p2[0] - p1[0])
                clipped.append((round(x), round(y)))
            elif not p1_inside and p2_inside:  # Entrando: interseção + p2
                x = xmax
                y = p1[1] + (p2[1] - p1[1]) * (xmax - p1[0]) / (p2[0] - p1[0])
                clipped.append((round(x), round(y)))
                clipped.append(p2)
        return clipped

    def clip_bottom(vertices):
        # Recorta contra a borda inferior y = ymin
        clipped = []
        # Loop de varredura das arestas p1->p2 do polígono corrente.
        # - Objetivo: manter apenas o que está acima/na borda inferior y=ymin.
        for i in range(len(vertices)):
            p1 = vertices[i]
            p2 = vertices[(i + 1) % len(vertices)]
            p1_inside = p1[1] >= ymin
            p2_inside = p2[1] >= ymin

            if p1_inside and p2_inside:  # Ambos dentro
                clipped.append(p2)
            elif p1_inside and not p2_inside:  # Saindo: interseção
                y = ymin
                x = p1[0] + (p2[0] - p1[0]) * (ymin - p1[1]) / (p2[1] - p1[1])
                clipped.append((round(x), round(y)))
            elif not p1_inside and p2_inside:  # Entrando: interseção + p2
                y = ymin
                x = p1[0] + (p2[0] - p1[0]) * (ymin - p1[1]) / (p2[1] - p1[1])
                clipped.append((round(x), round(y)))
                clipped.append(p2)
        return clipped

    def clip_top(vertices):
        # Recorta contra a borda superior y = ymax
        clipped = []
        # Loop de arestas p1->p2 para aplicar a regra de entrada/saída na borda superior.
        for i in range(len(vertices)):
            p1 = vertices[i]
            p2 = vertices[(i + 1) % len(vertices)]
            p1_inside = p1[1] <= ymax
            p2_inside = p2[1] <= ymax

            if p1_inside and p2_inside:  # Ambos dentro
                clipped.append(p2)
            elif p1_inside and not p2_inside:  # Saindo: interseção
                y = ymax
                x = p1[0] + (p2[0] - p1[0]) * (ymax - p1[1]) / (p2[1] - p1[1])
                clipped.append((round(x), round(y)))
            elif not p1_inside and p2_inside:  # Entrando: interseção + p2
                y = ymax
                x = p1[0] + (p2[0] - p1[0]) * (ymax - p1[1]) / (p2[1] - p1[1])
                clipped.append((round(x), round(y)))
                clipped.append(p2)
        return clipped

    # Normaliza entrada: remove fechamento duplicado se existir
    # subject_polygon: lista [(x,y), ...]; se último == primeiro, remove o último
    if subject_polygon and len(subject_polygon) >= 2 and subject_polygon[0] == subject_polygon[-1]:
        subject_polygon = subject_polygon[:-1]
    # Recortes sucessivos
    clipped_polygon = clip_left(subject_polygon)
    clipped_polygon = clip_right(clipped_polygon)
    clipped_polygon = clip_bottom(clipped_polygon)
    clipped_polygon = clip_top(clipped_polygon)

    # Remove vértices redundantes consecutivos (ex.: iguais)
    if clipped_polygon:
        compact = [clipped_polygon[0]]   # lista final sem duplicatas consecutivas
        # Loop para remover duplicatas consecutivas: compara cada vértice "p" com o último do "compact".
        for p in clipped_polygon[1:]:    # p: vértice atual
            if p != compact[-1]:         # se diferente do último adicionado
                compact.append(p)
        clipped_polygon = compact

    # Garante polígono fechado quando há pelo menos 2 vértices
    if clipped_polygon and len(clipped_polygon) >= 2 and clipped_polygon[0] != clipped_polygon[-1]:
        clipped_polygon.append(clipped_polygon[0])  # fecha repetindo o primeiro

    return clipped_polygon


def suth_hodgman_clip_convexo(subject_polygon, clip_polygon):
    """Recorta um polígono arbitrário contra uma janela de recorte poligonal convexa.

    subject_polygon: lista de (x,y) do polígono a recortar (aberto ou fechado).
    clip_polygon: lista de (x,y) do polígono convexo da janela (aberto ou fechado).
    Retorna lista de (x,y) do polígono resultante (fechado se houver pelo menos 2 vértices).
    """
    from utils.geometria import garantir_ccw  # garante orientação CCW do polígono de recorte

    def intersect(p1, p2, q1, q2):
        # Interseção de segmentos p1->p2 e q1->q2 (tratados como linhas infinitas)
        x1, y1 = p1; x2, y2 = p2  # coordenadas do primeiro segmento
        x3, y3 = q1; x4, y4 = q2  # coordenadas do segundo segmento
        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)  # denominador do cruzamento (determinante)
        if den == 0:
            return p2  # paralelos/colineares; devolve p2 para manter continuidade da cadeia
        # Fórmulas de interseção (usando determinantes)
        px = ((x1*y2 - y1*x2)*(x3 - x4) - (x1 - x2)*(x3*y4 - y3*x4)) / den
        py = ((x1*y2 - y1*x2)*(y3 - y4) - (y1 - y2)*(x3*y4 - y3*x4)) / den
        return (round(px), round(py))  # arredonda para grid de pixels

    def inside(p, a, b):
        # Considerando borda a->b com polígono clip CCW, lado interno é à esquerda (cross >= 0)
        ax, ay = a; bx, by = b; px, py = p
        # Produto vetorial 2D: (b-a) x (p-a) >= 0 -> p está à esquerda/na borda -> dentro
        return (bx - ax) * (py - ay) - (by - ay) * (px - ax) >= 0

    # Normaliza: remove fechamento duplicado
    S = subject_polygon[:]  # cópia dos vértices do polígono sujeito (para não mutar a entrada)
    if len(S) >= 2 and S[0] == S[-1]:
        S = S[:-1]  # remove fechamento duplicado
    C = clip_polygon[:]  # cópia da janela de recorte convexa
    if len(C) >= 2 and C[0] == C[-1]:
        C = C[:-1]
    if len(C) < 3 or len(S) < 3:
        return []  # precisa de pelo menos 3 vértices em cada polígono
    C = garantir_ccw(C)  # assegura sentido anti-horário (CCW) em C

    output = S  # lista de vértices resultante após cada etapa de recorte
    # Loop externo: percorre cada borda do polígono de recorte convexo (a->b)
    # - Invariante: após a i-ésima iteração, "output" é o polígono sujeito recortado pelas i primeiras bordas.
    # - Se "output" esvaziar em qualquer etapa, podemos interromper (nenhuma área resta).
    for i in range(len(C)):
        a = C[i]                       # vértice corrente da borda de recorte
        b = C[(i + 1) % len(C)]        # próximo vértice (borda a->b)
        input_list = output            # polígono a ser recortado contra a borda atual
        if not input_list:             # se esvaziou, pode interromper
            break
        output = []                    # acumulará o polígono recortado da etapa
        # Loop interno: varre todas as arestas s->e do polígono sujeito atual.
        # - Para cada aresta, decidimos entre manter e, inserir interseção, ou descartar ambos fora.
        for j in range(len(input_list)):
            s = input_list[j]                         # vértice inicial do lado do sujeito
            e = input_list[(j + 1) % len(input_list)] # vértice final
            s_in = inside(s, a, b)                    # s está dentro em relação à borda a->b?
            e_in = inside(e, a, b)                    # e está dentro?
            if s_in and e_in:
                output.append(e)                      # mantém e
            elif s_in and not e_in:
                output.append(intersect(s, e, a, b))  # saindo: adiciona ponto de saída
            elif (not s_in) and e_in:
                output.append(intersect(s, e, a, b))  # entrando: interseção + e
                output.append(e)
            # ambos fora: adiciona nada

    # Remove duplicatas consecutivas
    if output:
        compact = [output[0]]                 # remove duplicações consecutivas
        # Loop de compactação: ignora vértices repetidos consecutivos em "output".
        for p in output[1:]:
            if p != compact[-1]:
                compact.append(p)
        output = compact

    if output and len(output) >= 2 and output[0] != output[-1]:
        output.append(output[0])  # fecha polígono
    return output
