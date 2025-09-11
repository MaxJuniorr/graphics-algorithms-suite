"""Implementação de algoritmos de recorte de linha."""
from utils.geometria import dot, subtract

def is_convex(vertices):
    """Verifica se um polígono é convexo."""
    if len(vertices) < 3:
        return False
    
    got_negative = False
    got_positive = False
    num_points = len(vertices)
    for i in range(num_points):
        p1 = vertices[i]
        p2 = vertices[(i + 1) % num_points]
        p3 = vertices[(i + 2) % num_points]
        
        dx1 = p2[0] - p1[0]
        dy1 = p2[1] - p1[1]
        dx2 = p3[0] - p2[0]
        dy2 = p3[1] - p2[1]
        
        cross_product = dx1 * dy2 - dy1 * dx2
        
        if cross_product < 0:
            got_negative = True
        elif cross_product > 0:
            got_positive = True
            
        if got_negative and got_positive:
            return False
            
    return True

def cyrus_beck_clip(p1, p2, vertices):
    """
    Recorta uma linha (p1, p2) para uma janela convexa.

    Args:
        p1 (tuple): Ponto inicial da linha (x1, y1).
        p2 (tuple): Ponto final da linha (x2, y2).
        vertices (list): Lista de vértices do polígono convexo.

    Returns:
        tuple: Uma tupla (p1, p2) com as novas coordenadas da linha recortada,
               ou None se a linha estiver completamente fora da janela.
    """
    te = 0.0
    tl = 1.0
    ds = subtract(p2, p1)

    for i in range(len(vertices)):
        p_i = vertices[i]
        p_j = vertices[(i + 1) % len(vertices)]
        
        # Calcula a normal externa
        normal = (p_j[1] - p_i[1], p_i[0] - p_j[0])
        
        w = subtract(p1, p_i)
        
        w_dot_n = dot(w, normal)
        ds_dot_n = dot(ds, normal)
        
        if ds_dot_n == 0:  # Linha paralela à aresta
            if w_dot_n < 0:  # Linha está fora da aresta
                return None
            else:  # Linha está dentro ou sobre a aresta, continue
                continue

        if ds_dot_n != 0:
            t = -w_dot_n / ds_dot_n
            if ds_dot_n < 0:  # Linha entrando na aresta
                te = max(te, t)
            elif ds_dot_n > 0:  # Linha saindo da aresta
                tl = min(tl, t)
    
    if te > tl:
        return None

    clipped_p1 = (p1[0] + ds[0] * te, p1[1] + ds[1] * te)
    clipped_p2 = (p1[0] + ds[0] * tl, p1[1] + ds[1] * tl)
    
    return ( (round(clipped_p1[0]), round(clipped_p1[1])), (round(clipped_p2[0]), round(clipped_p2[1])) )