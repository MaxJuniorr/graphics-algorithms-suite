# algoritmos/circulo_elipse.py

def calcular_circulo(centro, raio):
    """
    Calcula os pixels de um círculo usando o Algoritmo do Ponto Médio.

    Args:
        centro (tuple): Uma tupla (xc, yc) com as coordenadas do centro.
        raio (int): O raio do círculo.

    Returns:
        list: Uma lista de tuplas [(x, y), ...], representando os pixels do círculo.
    """
    xc, yc = centro
    x = 0
    y = raio
    p = 1 - raio  # Parâmetro de decisão inicial

    pixels = []

    def adicionar_pixels_simetricos(x, y):
        """Adiciona os 8 pixels simétricos para o octante calculado."""
        pixels.append((xc + x, yc + y))
        pixels.append((xc - x, yc + y))
        pixels.append((xc + x, yc - y))
        pixels.append((xc - x, yc - y))
        pixels.append((xc + y, yc + x))
        pixels.append((xc - y, yc + x))
        pixels.append((xc + y, yc - x))
        pixels.append((xc - y, yc - x))

    # O loop calcula os pixels para um octante, e a função acima espelha para os outros 7
    while x <= y:
        adicionar_pixels_simetricos(x, y)
        x += 1
        if p < 0:
            p += 2 * x + 1
        else:
            y -= 1
            p += 2 * (x - y) + 1
            
    return pixels