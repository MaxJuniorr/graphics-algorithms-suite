import math

# --- Definições de Sólidos ---

def obter_cubo_padrao(escala=20):
    """ Retorna os 8 vértices de um cubo centrado na origem. """
    s = escala
    return [
        (-s, -s, -s), (s, -s, -s), (s, s, -s), (-s, s, -s),
        (-s, -s, s), (s, -s, s), (s, s, s), (-s, s, s)
    ]

def obter_arestas_cubo():
    """ Retorna os pares de índices que formam as 12 arestas do cubo. """
    return [
        (0, 1), (1, 2), (2, 3), (3, 0),  # Face traseira
        (4, 5), (5, 6), (6, 7), (7, 4),  # Face frontal
        (0, 4), (1, 5), (2, 6), (3, 7)   # Arestas de conexão
    ]

# --- Algoritmos de Projeção ---

def projecao_ortogonal(vertices_3d, plano='frontal'):
    """
    Projeta vértices 3D em um plano 2D usando projeção ortogonal.
    - plano 'frontal': descarta Z (projeção no plano XY)
    - plano 'topo': descarta Y (projeção no plano XZ)
    - plano 'lado': descarta X (projeção no plano YZ)
    """
    if plano == 'frontal':
        return [(v[0], v[1]) for v in vertices_3d]
    elif plano == 'topo':
        return [(v[0], v[2]) for v in vertices_3d]
    elif plano == 'lado':
        return [(v[1], v[2]) for v in vertices_3d]
    return []

def projecao_obliqua(vertices_3d, k, angulo_graus=45):
    """
    Projeta vértices 3D usando projeção oblíqua (base para Cavalier e Cabinet).
    k: fator de escala para a profundidade (z).
    """
    angulo_rad = math.radians(angulo_graus)
    cos_a = math.cos(angulo_rad)
    sin_a = math.sin(angulo_rad)
    
    vertices_2d = []
    for x, y, z in vertices_3d:
        x_proj = x + k * z * cos_a
        y_proj = y + k * z * sin_a
        vertices_2d.append((round(x_proj), round(y_proj)))
    return vertices_2d

def projecao_cavalier(vertices_3d, angulo_graus=45):
    """ Projeção Cavalier: k = 1. """
    return projecao_obliqua(vertices_3d, k=1, angulo_graus=angulo_graus)

def projecao_cabinet(vertices_3d, angulo_graus=45):
    """ Projeção Cabinet: k = 0.5. """
    return projecao_obliqua(vertices_3d, k=0.5, angulo_graus=angulo_graus)

def projecao_perspectiva(vertices_3d, ponto_observador=(0, 0, -100), plano_z=0):
    """
    Projeta vértices 3D em um plano 2D usando projeção em perspectiva a partir de um ponto de observação.

    Args:
        vertices_3d (list): Lista de tuplas (x, y, z) dos vértices.
        ponto_observador (tuple): Coordenadas (cx, cy, cz) do ponto de observação (câmera).
        plano_z (float): A posição do plano de projeção no eixo Z.

    Returns:
        list: Lista de tuplas (x, y) dos vértices projetados.
    """
    cx, cy, cz = ponto_observador
    vertices_2d = []

    for x, y, z in vertices_3d:
        # A distância do ponto ao observador no eixo Z é (cz - z)
        # Se for zero, o ponto está no mesmo plano perpendicular ao eixo Z que o observador,
        # o que resultaria em uma divisão por zero (raio de projeção paralelo ao plano).
        dist_z = cz - z
        if abs(dist_z) < 1e-6:
            # Ponto está muito perto do plano do observador, projeção é indefinida.
            # Poderíamos retornar um ponto muito grande ou simplesmente ignorar.
            # Por simplicidade, vamos projetar ortogonalmente neste caso.
            vertices_2d.append((round(x), round(y)))
            continue

        # A distância do plano de projeção ao observador no eixo Z
        dist_plano = cz - plano_z

        # Usando semelhança de triângulos:
        # (x_proj - cx) / dist_plano = (x - cx) / dist_z
        # x_proj = cx + (x - cx) * dist_plano / dist_z
        x_proj = cx + (x - cx) * dist_plano / dist_z
        y_proj = cy + (y - cy) * dist_plano / dist_z
        
        vertices_2d.append((round(x_proj), round(y_proj)))
        
    return vertices_2d
