import math

"""
Roteiro de apresentação – Projeções 3D → 2D

1) Sólidos
   - Vértices do cubo centrado na origem; arestas como pares de índices.

2) Projeções
   - Ortogonal: descarta um eixo conforme o plano escolhido.
   - Oblíqua (Cavalier/Cabinet): desloca x/y por k*z em direção do ângulo.
   - Perspectiva: semelhança de triângulos a partir do observador.
"""

# --- Definições de Sólidos ---

def obter_cubo_padrao(escala=20):
    """Retorna os 8 vértices de um cubo centrado na origem.

    escala: lado/2 do cubo; s será somado/subtraído em cada eixo.
    """
    s = escala
    return [
        (-s, -s, -s), (s, -s, -s), (s, s, -s), (-s, s, -s),
        (-s, -s, s), (s, -s, s), (s, s, s), (-s, s, s)
    ]

def obter_arestas_cubo():
    """Retorna os pares de índices que formam as 12 arestas do cubo."""
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
    # vertices_3d: lista de (x,y,z)
    # plano: string que define qual eixo será descartado
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
    k: fator de escala para a profundidade (z); 1.0 (Cavalier), 0.5 (Cabinet).
    """
    angulo_rad = math.radians(angulo_graus)  # converte graus → radianos
    cos_a = math.cos(angulo_rad)             # cos do ângulo de direção do desvio
    sin_a = math.sin(angulo_rad)             # sin do ângulo de direção do desvio
    
    vertices_2d = []                         # lista (x,y) projetada
    # Loop pelos vértices 3D: aplica deslocamento proporcional a z na direção do ângulo
    for x, y, z in vertices_3d:
        x_proj = x + k * z * cos_a
        y_proj = y + k * z * sin_a
        vertices_2d.append((round(x_proj), round(y_proj)))
    return vertices_2d

def projecao_cavalier(vertices_3d, angulo_graus=45):
    """Projeção Cavalier: k = 1."""
    return projecao_obliqua(vertices_3d, k=1, angulo_graus=angulo_graus)

def projecao_cabinet(vertices_3d, angulo_graus=45):
    """Projeção Cabinet: k = 0.5."""
    return projecao_obliqua(vertices_3d, k=0.5, angulo_graus=angulo_graus)

def projecao_perspectiva(vertices_3d, ponto_observador=(0, 0, -100), plano_z=0):
    """
    Projeta vértices 3D em um plano 2D usando projeção em perspectiva a partir de um ponto de observação.

    Args:
        vertices_3d (list): Lista de tuplas (x, y, z) dos vértices.
        ponto_observador (tuple): (cx, cy, cz) da câmera/observador.
        plano_z (float): Posição z do plano de projeção.

    Returns:
        list: Lista de tuplas (x, y) dos vértices projetados.
    """
    cx, cy, cz = ponto_observador   # posição da câmera
    vertices_2d = []                # lista de (x,y) projetada

    # Loop por todos os pontos 3D e projeta usando semelhança de triângulos
    for x, y, z in vertices_3d:
        # Distância ao observador no eixo Z; se muito pequena, evita divisão por zero
        dist_z = cz - z
        if abs(dist_z) < 1e-6:
            # fallback simples: projeta ortogonalmente
            vertices_2d.append((round(x), round(y)))
            continue

        # Distância do plano ao observador
        dist_plano = cz - plano_z

        # Semelhança: (x_proj - cx) / dist_plano = (x - cx) / dist_z
        x_proj = cx + (x - cx) * dist_plano / dist_z
        y_proj = cy + (y - cy) * dist_plano / dist_z
        
        vertices_2d.append((round(x_proj), round(y_proj)))
        
    return vertices_2d
