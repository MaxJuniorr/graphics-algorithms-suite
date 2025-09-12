# algoritmos/curvas_bezier.py
"""
Roteiro de apresentação – Curvas de Bézier Cúbicas

1) Problema que resolve
    - Interpolar suavemente entre p0 e p3 usando dois pontos de controle (p1, p2).

2) Ideia principal
    - Fórmula paramétrica cúbica B(t) = Σ B_i(t) * P_i, t ∈ [0, 1].
    - Amostramos t em passos (num_segmentos) e conectamos com linhas (polilinha).

3) Passo a passo (para narrar)
    - Calcular pontos da curva para t = 0..1 (coeficientes b0..b3).
    - Arredondar para grid, evitar duplicatas consecutivas.
    - Usar Bresenham para rasterizar cada segmento consecutivo.

4) Complexidade e observações
    - O(num_segmentos) para amostragem + Bresenham por segmento.
    - Quanto maior num_segmentos, mais suave (trade-off custo x qualidade).

5) Dicas de demo
    - Mostrar efeito de mover p1/p2 nas tangentes iniciais/finais.
    - Comparar poucas vs. muitas amostras.
"""

from .bresenham import calcular_linha_bresenham  # usamos a linha de Bresenham para rasterizar os segmentos da curva


def calcular_pontos_bezier_cubica(p0, p1, p2, p3, num_segmentos=20):
    """
    Calcula uma lista de pontos ao longo de uma Curva de Bézier Cúbica.

    Args:
        p0, p1, p2, p3 (tuple): Pontos inicial, de controle 1, de controle 2 e final.
        num_segmentos (int): A "resolução" da curva. Mais segmentos = mais suave.

    Returns:
        list: Uma lista de pontos [(x, y), ...] que formam a curva.
    """
    # p0, p1, p2, p3: cada um é uma tupla (x, y) representando, respectivamente,
    #   - p0: ponto inicial
    #   - p1: ponto de controle que define a tangente inicial
    #   - p2: ponto de controle que define a tangente final
    #   - p3: ponto final
    # num_segmentos: inteiro que define quantas divisões de t em [0,1] faremos; controla a suavidade

    pontos_da_curva = []  # lista de tuplas (x, y) inteiras amostradas ao longo da curva

    # Amostragem uniforme de t em [0, 1]
    for i in range(num_segmentos + 1):
        # i: índice da amostra, varia de 0 até num_segmentos (inclusive)
        t = i / num_segmentos  # t: parâmetro contínuo da curva no intervalo [0.0, 1.0]

        # Fórmula da Curva de Bézier Cúbica (coeficientes de Bernstein)
        um_menos_t = 1 - t  # ajuda para computar potências sem repetir subtração

        # Coeficientes da combinação convexa (dependem de t)
        # b0..b3 somam 1.0 (partição da unidade), ponderando cada ponto de controle
        b0 = um_menos_t ** 3             # contribuição de p0 quando t é pequeno
        b1 = 3 * t * (um_menos_t ** 2)   # contribuição de p1, controla tangente inicial
        b2 = 3 * (t ** 2) * um_menos_t   # contribuição de p2, controla tangente final
        b3 = t ** 3                      # contribuição de p3 quando t é grande

        # Calcula o ponto (x, y) contínuo e arredonda para o grid inteiro de pixels
        x_cont = b0 * p0[0] + b1 * p1[0] + b2 * p2[0] + b3 * p3[0]  # x(t) real
        y_cont = b0 * p0[1] + b1 * p1[1] + b2 * p2[1] + b3 * p3[1]  # y(t) real
        x = round(x_cont)  # x: inteiro no grid
        y = round(y_cont)  # y: inteiro no grid

        # Evita duplicar pontos iguais consecutivos (mesma célula de pixel)
        if not pontos_da_curva or pontos_da_curva[-1] != (x, y):
            pontos_da_curva.append((x, y))  # adiciona ponto amostrado inteiro

    return pontos_da_curva


def rasterizar_curva_bezier(p0, p1, p2, p3, num_segmentos=20):
    """
    Calcula os pontos da curva e usa Bresenham para gerar os pixels.

    Returns:
        list: A lista final de pixels a serem desenhados.
    """
    # pixels_finais: lista de tuplas (x, y) de todos os pixels dos segmentos rasterizados
    pixels_finais = []

    # 1. Calcula os vértices da polilinha que aproxima a curva
    # pontos_da_curva: lista de vértices (x, y) inteiros conectados em sequência
    pontos_da_curva = calcular_pontos_bezier_cubica(p0, p1, p2, p3, num_segmentos)

    # 2. Usa Bresenham entre cada par consecutivo de amostras
    for i in range(len(pontos_da_curva) - 1):
        # i: índice do segmento atual da polilinha (de 0 até n-2)
        ponto_atual = pontos_da_curva[i]        # vértice i
        proximo_ponto = pontos_da_curva[i + 1]  # vértice i+1

        # Rasteriza o segmento com Bresenham (lista de pixels inteiros)
        segmento = calcular_linha_bresenham(ponto_atual, proximo_ponto)
        # segmento: lista de (x, y) do traçado entre ponto_atual e proximo_ponto
        pixels_finais.extend(segmento)  # concatena os pixels deste segmento

    # Remove duplicados que podem ocorrer nas junções dos segmentos
    # set: elimina repetidos; list(...) retransforma em lista
    return list(set(pixels_finais))