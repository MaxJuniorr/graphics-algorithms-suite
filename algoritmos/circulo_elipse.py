# algoritmos/circulo_elipse.py
"""
Roteiro de apresentação – Círculo e Elipse (Algoritmo do Ponto Médio)

1) Problema que resolve
    - Rasterizar círculos e elipses em grade de pixels sem usar floats por pixel.

2) Ideia principal (círculo)
    - Simetria em 8 octantes; calculamos apenas um e espelhamos.
    - Variável de decisão p decide se mantemos y ou decrementamos y ao avançar x.

3) Ideia principal (elipse)
    - Duas regiões: onde |dy/dx| > 1 e onde |dy/dx| ≤ 1, com critérios diferentes.
    - Simetria em 4 quadrantes; calculamos um e espelhamos.

4) Dicas de apresentação
    - Mostrar a evolução de p (círculo) e p1/p2 (elipse) e quando y decrementa/incrementa.
    - Destacar espelhamento para cobrir octantes/quadrantes.
"""

def calcular_circulo(centro, raio):
    """
    Calcula os pixels de um círculo usando o Algoritmo do Ponto Médio.

    Args:
        centro (tuple): Uma tupla (xc, yc) com as coordenadas do centro.
        raio (int): O raio do círculo.

    Returns:
        list: Uma lista de tuplas [(x, y), ...], representando os pixels do círculo.
    """
    xc, yc = centro           # xc, yc: coordenadas do centro do círculo
    x = 0                     # começamos no ponto mais à direita do eixo vertical superior do octante
    y = raio                  # y inicial no topo do círculo
    p = 1 - raio              # parâmetro de decisão inicial (p0)

    pixels = []               # acumula todos os pixels do círculo (sem deduplicação)

    def adicionar_pixels_simetricos(x, y):
        """Adiciona os 8 pixels simétricos para o octante calculado."""
        # Espelhamentos: (±x, ±y) e trocas (x<->y) para cobrir 8 octantes
        pixels.append((xc + x, yc + y))
        pixels.append((xc - x, yc + y))
        pixels.append((xc + x, yc - y))
        pixels.append((xc - x, yc - y))
        pixels.append((xc + y, yc + x))
        pixels.append((xc - y, yc + x))
        pixels.append((xc + y, yc - x))
        pixels.append((xc - y, yc - x))

    # Loop do octante: avança x até x ultrapassar y (linha de 45°); invariante: (x,y) permanece no contorno do octante.
    # - Se p < 0: próximo pixel (x+1, y) ainda está mais perto do círculo ideal.
    # - Se p ≥ 0: decrementamos y (subimos um pixel) para aproximar do contorno.
    while x <= y:
        adicionar_pixels_simetricos(x, y)
        x += 1                 # passo base: avançamos uma coluna para a direita
        if p < 0:              # dentro do círculo: apenas ajusta p
            p += 2 * x + 1     # atualização incremental para o próximo x
        else:                  # cruzou a fronteira: ajusta y também
            y -= 1
            p += 2 * (x - y) + 1
            
    return pixels

def calcular_elipse(centro, rx, ry):
    """
    Calcula os pixels de uma elipse usando o Algoritmo do Ponto Médio.

    Args:
        centro (tuple): Uma tupla (xc, yc) com as coordenadas do centro.
        rx (int): O raio no eixo X.
        ry (int): O raio no eixo Y.

    Returns:
        list: Uma lista de tuplas [(x, y), ...], representando os pixels da elipse.
    """
    xc, yc = centro           # centro da elipse
    pixels = []               # lista de pixels acumulados

    def adicionar_pixels_simetricos(x, y):
        """Adiciona os 4 pixels simétricos para o quadrante calculado."""
        # Espelha nos quatro quadrantes (±x, ±y)
        pixels.append((xc + x, yc + y))
        pixels.append((xc - x, yc + y))
        pixels.append((xc + x, yc - y))
        pixels.append((xc - x, yc - y))

    # --- Região 1 ---
    x = 0                      # começa no topo do quadrante
    y = ry
    # p1: decisão na Região 1 (onde dx < dy), derivado da equação implícita da elipse
    p1 = (ry**2) - (rx**2 * ry) + (0.25 * rx**2)
    dx = 2 * (ry**2) * x       # derivadas incrementais em x
    dy = 2 * (rx**2) * y       # derivadas incrementais em y

    # Região 1: variação em x domina (pendente < -1 ou > 1 em termos de derivadas)
    while dx < dy:
        adicionar_pixels_simetricos(x, y)
        x += 1
        dx = 2 * (ry**2) * x
        if p1 < 0:                 # próximo ponto ainda acima da curva: não reduz y
            p1 += dx + (ry**2)
        else:                       # cruza a curva: reduz y
            y -= 1
            dy = 2 * (rx**2) * y
            p1 += dx - dy + (ry**2)

    # --- Região 2 ---
    # p2: decisão na Região 2 (onde dx ≥ dy), continuando de (x,y) da região anterior
    p2 = (ry**2 * (x + 0.5)**2) + (rx**2 * (y - 1)**2) - (rx**2 * ry**2)
    
    # Região 2: variação em y domina (agora diminuímos y a cada passo base)
    while y >= 0:
        adicionar_pixels_simetricos(x, y)
        y -= 1
        dy = 2 * (rx**2) * y
        if p2 > 0:                 # permanece do mesmo lado: não aumenta x
            p2 += (rx**2) - dy
        else:                       # cruza a curva: aumenta x
            x += 1
            dx = 2 * (ry**2) * x
            p2 += dx - dy + (rx**2)
            
    return pixels