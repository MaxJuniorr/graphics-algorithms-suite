from typing import List, Tuple
import math

Point = Tuple[int, int]

def preencher_scanline(vertices: List[Point]) -> List[Point]:
	"""
	Preenche um polígono simples usando o algoritmo de Scanline.

	- vertices: lista de vértices (x, y) em ordem (horária ou anti-horária).
				O polígono é considerado fechado (liga último ao primeiro).
	- Retorna: lista de pixels (x, y) inteiros no interior (bordas incluídas).
	"""
	if not vertices or len(vertices) < 3:
		return []

	# Garante fechamento
	pts = list(vertices)
	if pts[0] != pts[-1]:
		pts.append(pts[0])

	min_y = min(y for _, y in pts)
	max_y = max(y for _, y in pts)

	preenchidos: List[Point] = []

	for y in range(min_y, max_y + 1):
		xs: List[float] = []
		for i in range(len(pts) - 1):
			x1, y1 = pts[i]
			x2, y2 = pts[i + 1]

			# Ignora arestas horizontais
			if y1 == y2:
				continue

			ymin = min(y1, y2)
			ymax = max(y1, y2)
			# Intervalo semiaberto [ymin, ymax)
			if y >= ymin and y < ymax:
				t = (y - y1) / (y2 - y1)
				x = x1 + t * (x2 - x1)
				xs.append(x)

		if not xs:
			continue

		xs.sort()
		for j in range(0, len(xs), 2):
			if j + 1 >= len(xs):
				break
			x_in = xs[j]
			x_out = xs[j + 1]
			xi = math.ceil(min(x_in, x_out))
			xf = math.floor(max(x_in, x_out))
			for x in range(xi, xf + 1):
				preenchidos.append((x, y))

	# Remove duplicados preservando ordem
	vistos = set()
	unicos: List[Point] = []
	for p in preenchidos:
		if p not in vistos:
			vistos.add(p)
			unicos.append(p)
	return unicos
