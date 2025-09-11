"""Funções auxiliares de geometria."""

def dot(v1, v2):
    """Calcula o produto escalar de dois vetores."""
    return v1[0] * v2[0] + v1[1] * v2[1]

def subtract(p2, p1):
    """Retorna o vetor que representa a diferença entre dois pontos (p2 - p1)."""
    return (p2[0] - p1[0], p2[1] - p1[1])
