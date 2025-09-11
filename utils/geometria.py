"""Funções auxiliares de geometria."""

from typing import List, Tuple

Ponto = Tuple[int, int]


def _cross(ax: int, ay: int, bx: int, by: int) -> int:
	return ax * by - ay * bx


def area_orientada(pontos: List[Ponto]) -> int:
	"""Retorna 2*área orientada (Shoelace). >0 se CCW, <0 se CW."""
	if not pontos:
		return 0
	soma = 0
	for i in range(len(pontos)):
		x1, y1 = pontos[i]
		x2, y2 = pontos[(i + 1) % len(pontos)]
		soma += x1 * y2 - y1 * x2
	return soma


def eh_convexo(pontos: List[Ponto]) -> bool:
	"""Verifica se um polígono (não necessariamente fechado) é convexo.
	Aceita colinearidade. Requer >= 3 vértices.
	"""
	pts = pontos[:]
	if len(pts) < 3:
		return False
	# Remove fechamento duplicado, se houver
	if pts[0] == pts[-1]:
		pts = pts[:-1]
	n = len(pts)
	sinal = 0
	for i in range(n):
		x0, y0 = pts[i]
		x1, y1 = pts[(i + 1) % n]
		x2, y2 = pts[(i + 2) % n]
		cx = _cross(x1 - x0, y1 - y0, x2 - x1, y2 - y1)
		if cx != 0:
			if sinal == 0:
				sinal = 1 if cx > 0 else -1
			elif (cx > 0 and sinal < 0) or (cx < 0 and sinal > 0):
				return False
	return True


def garantir_ccw(pontos: List[Ponto]) -> List[Ponto]:
	"""Retorna os pontos em ordem CCW (anti-horária)."""
	pts = pontos[:]
	if len(pts) >= 3 and area_orientada(pts) < 0:
		pts.reverse()
	return pts