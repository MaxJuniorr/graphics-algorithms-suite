"""
Roteiro de apresentação – Preenchimento

1) Problema
	- Preencher a área interna de um polígono (scanline) ou regiões vazias (flood fill).

2) Algoritmo Scanline (polígono)
	- Varre linhas y; encontra interseções com arestas; aplica regra par-ímpar.
	- Tratar arestas horizontais e contagem semiaberta [ymin, ymax) evita duplicar interseções.

3) Versão Multi (vários polígonos)
	- Junta todas as arestas e varre de uma vez para aplicar regra par-ímpar global.

4) Flood Fill (DFS/BFS)
	- Expande a partir de uma semente por vizinhança (4-conexa), respeitando limites/bordas.

5) Dicas de demonstração
	- Mostrar diferença entre borda aberta/fechada e o fechamento automático do polígono.
	- Ilustrar por que ignorar horizontais e usar [ymin, ymax) evita artefatos.
	- Flood: mostrar escolha automática de seed (centro da bbox) e limitação por bounds.
"""

from typing import List, Tuple, Optional, Set  # tipos usados para clareza
import math

Point = Tuple[int, int]  # alias para coordenada inteira (x, y)

def preencher_scanline(vertices: List[Point]) -> List[Point]:
	"""
	Preenche um polígono simples usando o algoritmo de Scanline.

	- vertices: lista de vértices (x, y) em ordem (horária ou anti-horária).
				O polígono é considerado fechado (liga último ao primeiro).
	- Retorna: lista de pixels (x, y) inteiros no interior (bordas incluídas).
	"""
	if not vertices or len(vertices) < 3:
		return []

	# Garante fechamento (evita depender de último==primeiro)
	pts = list(vertices)  # cópia mutável dos vértices de entrada
	if pts[0] != pts[-1]:
		pts.append(pts[0])

	min_y = min(y for _, y in pts)  # menor y dentre os vértices (limite inferior da varredura)
	max_y = max(y for _, y in pts)  # maior y dentre os vértices (limite superior da varredura)

	preenchidos: List[Point] = []  # lista final de pixels preenchidos

	# Loop principal de varredura (scanline): percorre cada linha horizontal entre min_y e max_y.
	# Invariante: para cada y, vamos coletar interseções com as arestas e preencher pares [entrada, saída].
	for y in range(min_y, max_y + 1):
		xs: List[float] = []  # interseções em x com a linha de varredura corrente
		# Para cada aresta (par de vértices consecutivos), verifica se intersecta a linha y atual.
		for i in range(len(pts) - 1):
			x1, y1 = pts[i]       # ponto inicial da aresta
			x2, y2 = pts[i + 1]   # ponto final da aresta

			# Ignora arestas horizontais (não contribuem com interseções em y fixo)
			if y1 == y2:
				continue

			ymin = min(y1, y2)     # y mínimo da aresta
			ymax = max(y1, y2)     # y máximo da aresta
			# Intervalo semiaberto [ymin, ymax): evita dupla contagem no vértice superior
			if y >= ymin and y < ymax:
				t = (y - y1) / (y2 - y1)  # parâmetro de interpolação ao longo da aresta
				x = x1 + t * (x2 - x1)    # abscissa do ponto de interseção
				xs.append(x)

		if not xs:
			continue

		xs.sort()  # ordena interseções em x para formar pares
		for j in range(0, len(xs), 2):
			if j + 1 >= len(xs):
				break
			x_in = xs[j]         # entrada no interior do polígono
			x_out = xs[j + 1]    # saída do interior do polígono
			# Ceil/Floor para cobrir integralmente os pixels entre as interseções
			xi = math.ceil(min(x_in, x_out))  # primeiro pixel cheio no intervalo
			xf = math.floor(max(x_in, x_out)) # último pixel cheio no intervalo
			for x in range(xi, xf + 1):
				preenchidos.append((x, y))

	# Remove duplicados preservando ordem: percorre a lista e usa um set para filtrar repetidos.
	vistos = set()              # pixels já vistos
	unicos: List[Point] = []    # pixels únicos na ordem de preenchimento
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
	# Filtra e normaliza polígonos válidos (fecha e decompõe em segmentos)
	segmentos = []  # lista de pares ((x1,y1),(x2,y2)) representando todas as arestas
	min_y_glb = None  # menor y entre todos os segmentos (varredura global)
	max_y_glb = None  # maior y entre todos os segmentos (varredura global)
	# Normaliza cada polígono de entrada: fecha (se necessário) e coleta suas arestas.
	for verts in poligonos:
		if not verts or len(verts) < 3:
			continue
		pts = list(verts)  # cópia dos vértices do polígono atual
		if pts[0] != pts[-1]:
			pts.append(pts[0])
		# Decompõe o polígono em segmentos (arestas contíguas) e atualiza faixa global de y.
		for i in range(len(pts) - 1):
			a = pts[i]
			b = pts[i + 1]
			segmentos.append((a, b))  # adiciona aresta (a->b) à lista global
			# Atualiza faixa global de varredura
			ay, by = a[1], b[1]  # coordenadas y dos extremos
			lo = min(ay, by)     # y mínimo da aresta
			hi = max(ay, by)     # y máximo da aresta
			if min_y_glb is None or lo < min_y_glb:
				min_y_glb = lo
			if max_y_glb is None or hi > max_y_glb:
				max_y_glb = hi

	if not segmentos or min_y_glb is None or max_y_glb is None:
		return []

	preenchidos: List[Point] = []  # pixels preenchidos resultado da varredura global

	# Varredura global (multi-polígono): mesmo princípio do scanline simples, agora considerando todas as arestas juntas.
	for y in range(min_y_glb, max_y_glb + 1):
		xs: List[float] = []  # interseções com a linha y atual
		# Para cada segmento, acumula a interseção (se houver) com a linha y corrente.
		for (x1, y1), (x2, y2) in segmentos:
			# Ignora arestas horizontais
			if y1 == y2:
				continue
			ymin = min(y1, y2)  # y inferior do segmento
			ymax = max(y1, y2)  # y superior do segmento
			# Intervalo semiaberto [ymin, ymax)
			if y >= ymin and y < ymax:
				t = (y - y1) / (y2 - y1)  # parâmetro de interpolação
				x = x1 + t * (x2 - x1)    # ponto de interseção em x
				xs.append(x)

		if not xs:
			continue

		xs.sort()
		for j in range(0, len(xs), 2):
			if j + 1 >= len(xs):
				break
			x_in = xs[j]        # entrada no interior
			x_out = xs[j + 1]   # saída do interior
			# Idem ao caso simples: usa ceil/floor para cobrir pixels inteiros
			xi = math.ceil(min(x_in, x_out))  # limite inteiro à esquerda
			xf = math.floor(max(x_in, x_out)) # limite inteiro à direita
			for x in range(xi, xf + 1):
				preenchidos.append((x, y))

	# Remove duplicados preservando ordem (mesmo procedimento do caso simples).
	vistos = set()            # pixels já vistos
	unicos: List[Point] = []  # saída sem duplicatas
	for p in preenchidos:
		if p not in vistos:
			vistos.add(p)
			unicos.append(p)
	return unicos


def _ponto_em_segmento(p: Point, a: Point, b: Point) -> bool:
	"""Retorna True se o ponto p está exatamente no segmento [a,b]."""
	(x, y), (x1, y1), (x2, y2) = p, a, b  # ponto testado e extremos do segmento
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
	pts = list(vertices)  # cópia para permitir fechamento sem alterar entrada
	if pts[0] != pts[-1]:
		pts.append(pts[0])

	# Borda conta como dentro (útil para preenchimento aderir ao contorno).
	# Checa cada aresta; se p estiver exatamente sobre o segmento, retorna True.
	for i in range(len(pts) - 1):
		if _ponto_em_segmento(p, pts[i], pts[i + 1]):
			return True

	x, y = p             # coordenadas do ponto a testar
	dentro = False       # estado do ray casting (par-ímpar)
	# Ray casting: para cada aresta, alterna o estado 'dentro' quando há cruzamento à direita do ponto.
	for i in range(len(pts) - 1):
		x1, y1 = pts[i]
		x2, y2 = pts[i + 1]
		# Verifica interseção com a semi-reta à direita
		cond_y = (y1 > y) != (y2 > y)  # aresta cruza a horizontal do ponto?
		if not cond_y:
			continue
		xinters = (x2 - x1) * (y - y1) / (y2 - y1) + x1  # abscissa do cruzamento
		if x < xinters:
			dentro = not dentro
	return dentro


def _escolher_seed(vertices: List[Point]) -> Optional[Point]:
	"""Escolhe um ponto interno ao polígono, tentando centro da bbox e varredura se necessário."""
	if not vertices:
		return None
	xs = [x for x, _ in vertices]  # lista de xs para bbox
	ys = [y for _, y in vertices]  # lista de ys para bbox
	min_x, max_x = min(xs), max(xs)
	min_y, max_y = min(ys), max(ys)
	# Centro aproximado (bom palpite; se falhar, varre a bbox)
	cx = (min_x + max_x) // 2  # centro aproximado em x
	cy = (min_y + max_y) // 2  # centro aproximado em y
	candidato = (cx, cy)
	if _ponto_dentro_poligono(candidato, vertices):
		return candidato
	# Varre caixa delimitadora para achar ponto interno
	# Busca exaustiva dentro da bbox: percorre y e x até encontrar um ponto interno.
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
	pts = []  # polígono normalizado sem duplicatas consecutivas
	for v in vertices:
		if not pts or pts[-1] != v:
			pts.append(v)
	if pts[0] != pts[-1]:
		pts.append(pts[0])

	# BBox para limitar busca
	xs = [x for x, _ in pts]  # xs da bbox
	ys = [y for _, y in pts]  # ys da bbox
	min_x, max_x = min(xs), max(xs)
	min_y, max_y = min(ys), max(ys)

	# Escolhe seed se necessário
	s = seed or _escolher_seed(pts)  # escolhe semente se não for fornecida
	if s is None:
		return []

	preenchidos: List[Point] = []  # acumula pixels preenchidos
	visitados: Set[Point] = set()  # marca o que já foi processado
	pilha: List[Point] = [s]       # estrutura LIFO para DFS

	# DFS iterativo (poderia ser BFS); 4-vizinhos para não vazar em diagonais.
	# Invariante: cada ponto entra na pilha no máximo uma vez e é marcado em 'visitados' ao ser processado.
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
		# 4-vizinhos (N, S, L, O)
		pilha.append((x + 1, y))
		pilha.append((x - 1, y))
		pilha.append((x, y + 1))
		pilha.append((x, y - 1))

	# Remove duplicados preservando ordem.
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

	visitados: Set[Point] = set()  # marca pixels já processados
	preenchidos: List[Point] = []  # resultado do flood
	pilha: List[Point] = [seed]    # pilha inicial com a semente

	# Flood fill no canvas (sem polígono): mesmo laço DFS com verificação de bounds e células ocupadas.
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

	# Remove duplicados preservando ordem.
	vistos = set()
	unicos: List[Point] = []
	for p in preenchidos:
		if p not in vistos:
			vistos.add(p)
			unicos.append(p)
	return unicos
