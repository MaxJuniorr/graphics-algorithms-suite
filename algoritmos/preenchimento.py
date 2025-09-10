from typing import List, Tuple, Optional, Set
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


def preencher_scanline_multi(poligonos: List[List[Point]]) -> List[Point]:
	"""
	Aplica Scanline considerando múltiplos polígonos ao mesmo tempo (regra par-ímpar).

	- poligonos: lista de polígonos; cada polígono é uma lista de vértices (x,y) em ordem.
	- Retorna: lista de pixels (x, y) inteiros preenchidos considerando todos como um só conjunto.
	"""
	# Filtra e normaliza polígonos válidos
	segmentos = []  # lista de pares ((x1,y1),(x2,y2))
	min_y_glb = None
	max_y_glb = None
	for verts in poligonos:
		if not verts or len(verts) < 3:
			continue
		pts = list(verts)
		if pts[0] != pts[-1]:
			pts.append(pts[0])
		for i in range(len(pts) - 1):
			a = pts[i]
			b = pts[i + 1]
			segmentos.append((a, b))
			# Atualiza faixa global de varredura
			ay, by = a[1], b[1]
			lo = min(ay, by)
			hi = max(ay, by)
			if min_y_glb is None or lo < min_y_glb:
				min_y_glb = lo
			if max_y_glb is None or hi > max_y_glb:
				max_y_glb = hi

	if not segmentos or min_y_glb is None or max_y_glb is None:
		return []

	preenchidos: List[Point] = []

	for y in range(min_y_glb, max_y_glb + 1):
		xs: List[float] = []
		for (x1, y1), (x2, y2) in segmentos:
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


def _ponto_em_segmento(p: Point, a: Point, b: Point) -> bool:
	"""Retorna True se o ponto p está exatamente no segmento [a,b]."""
	(x, y), (x1, y1), (x2, y2) = p, a, b
	# Colinearidade via área do triângulo (determinante == 0)
	det = (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)
	if det != 0:
		return False
	# Dentro do retângulo delimitador
	return min(x1, x2) <= x <= max(x1, x2) and min(y1, y2) <= y <= max(y1, y2)


def _ponto_dentro_poligono(p: Point, vertices: List[Point]) -> bool:
	"""Teste de ponto-em-polígono (ray casting). Considera borda como dentro."""
	if not vertices or len(vertices) < 3:
		return False

	# Fecha polígono
	pts = list(vertices)
	if pts[0] != pts[-1]:
		pts.append(pts[0])

	# Borda conta como dentro
	for i in range(len(pts) - 1):
		if _ponto_em_segmento(p, pts[i], pts[i + 1]):
			return True

	x, y = p
	dentro = False
	for i in range(len(pts) - 1):
		x1, y1 = pts[i]
		x2, y2 = pts[i + 1]
		# Verifica interseção com a semi-reta à direita
		cond_y = (y1 > y) != (y2 > y)
		if not cond_y:
			continue
		xinters = (x2 - x1) * (y - y1) / (y2 - y1) + x1
		if x < xinters:
			dentro = not dentro
	return dentro


def _escolher_seed(vertices: List[Point]) -> Optional[Point]:
	"""Escolhe um ponto interno ao polígono, tentando centro da bbox e varredura se necessário."""
	if not vertices:
		return None
	xs = [x for x, _ in vertices]
	ys = [y for _, y in vertices]
	min_x, max_x = min(xs), max(xs)
	min_y, max_y = min(ys), max(ys)
	# Centro aproximado
	cx = (min_x + max_x) // 2
	cy = (min_y + max_y) // 2
	candidato = (cx, cy)
	if _ponto_dentro_poligono(candidato, vertices):
		return candidato
	# Varre caixa delimitadora para achar ponto interno
	for yy in range(min_y, max_y + 1):
		for xx in range(min_x, max_x + 1):
			if _ponto_dentro_poligono((xx, yy), vertices):
				return (xx, yy)
	return None


def preencher_recursao(vertices: List[Point], seed: Optional[Point] = None) -> List[Point]:
	"""Preenche área interna via flood fill (DFS iterativo) delimitada pelo polígono.

	- vertices: polígono simples (fechado implicitamente)
	- seed: ponto inicial; se None, será escolhido automaticamente
	Retorna lista de pontos preenchidos (inclui borda).
	"""
	if not vertices or len(vertices) < 3:
		return []

	# Normaliza/fecha polígono e remove duplicados consecutivos
	pts = []
	for v in vertices:
		if not pts or pts[-1] != v:
			pts.append(v)
	if pts[0] != pts[-1]:
		pts.append(pts[0])

	# BBox para limitar busca
	xs = [x for x, _ in pts]
	ys = [y for _, y in pts]
	min_x, max_x = min(xs), max(xs)
	min_y, max_y = min(ys), max(ys)

	# Escolhe seed se necessário
	s = seed or _escolher_seed(pts)
	if s is None:
		return []

	preenchidos: List[Point] = []
	visitados: Set[Point] = set()
	pilha: List[Point] = [s]

	while pilha:
		x, y = pilha.pop()
		if (x, y) in visitados:
			continue
		visitados.add((x, y))

		if x < min_x or x > max_x or y < min_y or y > max_y:
			continue
		if not _ponto_dentro_poligono((x, y), pts):
			continue

		preenchidos.append((x, y))
		# 4-vizinhos
		pilha.append((x + 1, y))
		pilha.append((x - 1, y))
		pilha.append((x, y + 1))
		pilha.append((x, y - 1))

	# Remove duplicados preservando ordem
	vistos = set()
	unicos: List[Point] = []
	for p in preenchidos:
		if p not in vistos:
			vistos.add(p)
			unicos.append(p)
	return unicos


def preencher_flood_canvas(ocupados: Set[Point], seed: Point, bounds: Tuple[int, int, int, int]) -> List[Point]:
	"""Flood fill genérico no canvas, preenchendo todas as células vazias conectadas à seed.

	- ocupados: conjunto de pontos já ocupados (bordas/desenhos existentes)
	- seed: ponto inicial do preenchimento
	- bounds: (min_x, max_x, min_y, max_y) limites inclusivos do grid
	Retorna lista de pontos preenchidos.
	"""
	min_x, max_x, min_y, max_y = bounds
	sx, sy = seed
	if sx < min_x or sx > max_x or sy < min_y or sy > max_y:
		return []
	if seed in ocupados:
		return []

	visitados: Set[Point] = set()
	preenchidos: List[Point] = []
	pilha: List[Point] = [seed]

	while pilha:
		x, y = pilha.pop()
		if (x, y) in visitados:
			continue
		visitados.add((x, y))

		if x < min_x or x > max_x or y < min_y or y > max_y:
			continue
		if (x, y) in ocupados:
			continue

		preenchidos.append((x, y))
		pilha.append((x + 1, y))
		pilha.append((x - 1, y))
		pilha.append((x, y + 1))
		pilha.append((x, y - 1))

	# Remove duplicados preservando ordem
	vistos = set()
	unicos: List[Point] = []
	for p in preenchidos:
		if p not in vistos:
			vistos.add(p)
			unicos.append(p)
	return unicos
