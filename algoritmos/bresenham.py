# algoritmos/bresenham.py

"""
Roteiro de apresentação – Algoritmo de Bresenham (Linha)

1) Problema que resolve
    - Desenhar uma linha em grid de pixels usando apenas inteiros.
    - Escolher o pixel "mais próximo" da reta ideal a cada passo.

2) Ideia principal
    - Erro incremental p (ou decisão) que indica quando subir/ descer no eixo menor.
    - Tratamos todos os octantes convertendo o problema com |dx| e |dy|.

3) Passo a passo (para citar enquanto mostra o código)
    - Calcular dx, dy e os sinais de incremento (sinal_x, sinal_y).
    - Decidir se a linha é mais "deitada" (dx > dy) ou "em pé" (dx ≤ dy).
    - Inicializar p e iterar acumulando pontos, ajustando p e (x,y) a cada passo.

4) Complexidade e vantagens
    - O(n) com n = comprimento em pixels; só soma e subtração (inteiros).
    - Rápido, simples, amplamente usado em rasterização de linhas.

5) Dicas de demonstração
    - Mostrar um caso dx>dy e outro dy≥dx.
    - Destacar quando p ultrapassa 0 e o eixo menor é atualizado.
"""

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
    x1, y1 = ponto_inicial  # ponto inicial (inteiros)
    x2, y2 = ponto_final    # ponto final (inteiros)
    
    pixels = []  # lista de (x,y) acumulados do traçado
    
    # Deltas (variação entre pontos)
    dx = x2 - x1           # variação em x (pode ser negativa)
    dy = y2 - y1           # variação em y (pode ser negativa)

    # Define os sinais do incremento (direção de avanço)
    sinal_x = 1 if dx > 0 else -1  # direção do avanço em x
    sinal_y = 1 if dy > 0 else -1  # direção do avanço em y
    
    # Trabalhamos com os valores absolutos para decidir o eixo dominante
    dx = abs(dx)  # módulo para decidir octante dominante
    dy = abs(dy)

    # Octante: decide o eixo dominante (X ou Y) para percorrer
    if dx > dy:
        # A variação em X é maior: avançamos em X e corrigimos Y quando p ≥ 0
        # Derivação rápida da variável de decisão p:
        # - Reta ideal: y = y0 + m(x - x0), m = dy/dx.
        # - Comparamos duas escolhas de pixel consecutivo: (x+1, y) vs (x+1, y+sinal_y).
        # - p acumula o erro proporcional a (2*dy - 2*dx*delta_y) para evitar floats.
        # Inicialização clássica: p0 = 2*dy - dx.
        p = 2 * dy - dx     # variável de decisão inicial
        x, y = x1, y1       # ponto corrente a ser emitido
        # Loop: avança dx+1 passos, emitindo um pixel por coluna
        for _ in range(dx + 1):
            pixels.append((x, y))
            if p >= 0:
                # p >= 0 => erro passou do meio entre as duas opções, então ajustamos Y
                y += sinal_y
                p -= 2 * dx
            x += sinal_x
            # Avanço base sempre aumenta 2*dy no acumulador
            p += 2 * dy
    else:
        # A variação em Y é maior ou igual: avançamos em Y e corrigimos X quando p ≥ 0
        # Simétrico ao caso acima (trocando papéis de x e y)
        p = 2 * dx - dy     # variável de decisão inicial
        x, y = x1, y1       # ponto corrente a ser emitido
        # Loop: avança dy+1 passos, emitindo um pixel por linha
        for _ in range(dy + 1):
            pixels.append((x, y))
            if p >= 0:
                # Critério de desempate: p >= 0 decide subir/baixar em X
                x += sinal_x
                p -= 2 * dy
            y += sinal_y
            p += 2 * dx
            
    return pixels