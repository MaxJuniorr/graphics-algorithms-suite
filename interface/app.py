import math
import pygame
import pygame_gui
from interface.painel_controle import PainelControle
from interface.painel_projecoes import PainelProjecoes
from interface.area_desenho import AreaDesenho
from algoritmos.circulo_elipse import calcular_circulo, calcular_elipse
from algoritmos.preenchimento import preencher_scanline, preencher_flood_canvas, preencher_scanline_multi
from algoritmos.recorte import cohen_sutherland_clip, sutherland_hodgman_clip, suth_hodgman_clip_convexo
from algoritmos.projecoes import (
    obter_cubo_padrao, obter_arestas_cubo, projecao_ortogonal,
    projecao_cavalier, projecao_cabinet, projecao_perspectiva
)
from utils.geometria import eh_convexo
import algoritmos.transformacoes as transform

# --- Constantes de Layout ---
LARGURA_TOTAL = 1250
ALTURA_TOTAL = 800
LARGURA_PAINEL = 450
LARGURA_CANVAS = LARGURA_TOTAL - LARGURA_PAINEL
ALTURA_CANVAS = ALTURA_TOTAL
COR_PAINEL = (60, 60, 60)

class Aplicacao:
    # Laço principal da aplicação e roteamento de eventos da UI.
    def __init__(self, largura_grid_inicial, altura_grid_inicial):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA_TOTAL, ALTURA_TOTAL))
        pygame.display.set_caption("Trabalho de Computação Gráfica")
        self.ui_manager = pygame_gui.UIManager((LARGURA_TOTAL, ALTURA_TOTAL))
        self.area_desenho = AreaDesenho(LARGURA_CANVAS, ALTURA_CANVAS, largura_grid_inicial, altura_grid_inicial)
        self.painel_controle = PainelControle(self.ui_manager, LARGURA_PAINEL, ALTURA_TOTAL, LARGURA_CANVAS)
        self.rodando = True
        self.clock = pygame.time.Clock()
        self.proximo_clique_define = None
        self.polilinha_capturando = False
        self.polilinha_pontos = []
        # Captura de janela de recorte poligonal (convexa)
        self.clip_poly_capturando = False
        self.clip_poly_pontos = []
        self.painel_projecoes = None

    def _vertices_para_preenchimento(self, desenho, num_segmentos: int = 72):
        """
        Constrói um conjunto de vértices para preenchimento via Scanline,
        sem alterar o tipo do desenho original.

        Suporta diretamente:
        - Polilinha: retorna a cadeia, garantindo fechamento último→primeiro;
        - Círculo/Elipse: retorna uma aproximação poligonal com num_segmentos.
        """
        params = desenho.parametros
        if desenho.tipo == "Polilinha":
            vertices = list(params.get('pontos', []))
            if len(vertices) < 3:
                return []
            if vertices[0] != vertices[-1]:
                vertices.append(vertices[0])
            return vertices
        if desenho.tipo == "Círculo":
            centro = params.get('centro', (0, 0))
            raio = params.get('raio', 0)
            if raio <= 0:
                return []
            pts = []
            for i in range(num_segmentos):
                ang = 2 * math.pi * i / num_segmentos
                x = centro[0] + raio * math.cos(ang)
                y = centro[1] + raio * math.sin(ang)
                pts.append((round(x), round(y)))
            if pts and pts[0] != pts[-1]:
                pts.append(pts[0])
            return pts
        if desenho.tipo == "Elipse":
            centro = params.get('centro', (0, 0))
            rx = params.get('rx', 0)
            ry = params.get('ry', 0)
            if rx <= 0 or ry <= 0:
                return []
            pts = []
            for i in range(num_segmentos):
                ang = 2 * math.pi * i / num_segmentos
                x = centro[0] + rx * math.cos(ang)
                y = centro[1] + ry * math.sin(ang)
                pts.append((round(x), round(y)))
            if pts and pts[0] != pts[-1]:
                pts.append(pts[0])
            return pts
        return []

    def executar(self):
        """
        Game loop de 60 FPS: coleta eventos, atualiza estados/preview, redesenha.

        Etapas por frame:
        1) process_events: mapeia cliques em canvas/controles e dropdowns;
        2) atualizar_historico: sincroniza lista e painel de recorte;
        3) atualizar janela de recorte visual (retângulo ou polígono) com base
           nos campos de entrada atuais, tolerando valores inválidos;
        4) update + draw: UI e canvas são redesenhados, depois flip no display.
        """
        while self.rodando:
            delta_time = self.clock.tick(60) / 1000.0
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.rodando = False
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    # Clique no canvas define coordenadas para o próximo campo
                    # marcado com "Def" (quando self.proximo_clique_define setado).
                    if self.proximo_clique_define and evento.pos[0] < LARGURA_CANVAS:
                        coords = self.area_desenho.tela_para_grade(*evento.pos)
                        self.definir_coordenadas_por_clique(coords)
                        self.proximo_clique_define = None
                    # Captura de pontos da polilinha por clique
                    elif self.polilinha_capturando and evento.pos[0] < LARGURA_CANVAS:
                        coords = self.area_desenho.tela_para_grade(*evento.pos)
                        self.polilinha_pontos.append((coords[0], coords[1]))
                        # Atualiza a pré-visualização em vermelho
                        self.area_desenho.definir_preview_polilinha(self.polilinha_pontos)
                        # Atualiza preview textual no painel
                        try:
                            texto = '; '.join(f"{x},{y}" for x, y in self.polilinha_pontos)
                            self.painel_controle.elementos_polilinha['entrada_pontos'].set_text(texto)
                        except Exception:
                            pass
                    # Captura de pontos da janela de recorte poligonal por clique
                    elif self.clip_poly_capturando and evento.pos[0] < LARGURA_CANVAS:
                        coords = self.area_desenho.tela_para_grade(*evento.pos)
                        self.clip_poly_pontos.append((coords[0], coords[1]))
                        self.area_desenho.definir_preview_clip_poligono(self.clip_poly_pontos)
                self.ui_manager.process_events(evento)
                if evento.type == pygame_gui.UI_BUTTON_PRESSED:
                    # Qualquer clique em botão da UI é roteado para um handler
                    # único que despacha por elemento.
                    self.manipular_eventos_ui(evento)
                elif evento.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    if evento.ui_element == self.painel_controle.seletor_figura:
                        self.painel_controle.mostrar_elementos_figura(evento.text)
                        # Mostrar prévia apenas quando Polilinha está selecionada
                        if evento.text == 'Polilinha':
                            try:
                                pontos_str = [p.strip() for p in self.painel_controle.elementos_polilinha['entrada_pontos'].get_text().split(';')]
                                pontos = [tuple(map(int, p.split(','))) for p in pontos_str if p]
                                self.area_desenho.definir_preview_polilinha(pontos if len(pontos) >= 2 else None)
                            except Exception:
                                self.area_desenho.limpar_preview_polilinha()
                        else:
                            self.area_desenho.limpar_preview_polilinha()
                
                    # Reage a mudanças de seleção no painel de projeções (se aberto)
                    if self.painel_projecoes is not None and evento.ui_element == self.painel_projecoes.seletor_solido:
                        self.painel_projecoes.atualizar_visibilidade_controles()
                    elif self.painel_projecoes is not None and evento.ui_element == self.painel_projecoes.seletor_projecao:
                        self.painel_projecoes.atualizar_visibilidade_controles()
                elif evento.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
                    if evento.ui_element == self.painel_controle.lista_historico:
                        self.manipular_selecao_historico(evento)
                elif evento.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                    # Atualiza a prévia ao digitar pontos da polilinha
                    if evento.ui_element == self.painel_controle.elementos_polilinha.get('entrada_pontos'):
                        try:
                            pontos_str = [p.strip() for p in self.painel_controle.elementos_polilinha['entrada_pontos'].get_text().split(';')]
                            pontos = [tuple(map(int, p.split(','))) for p in pontos_str if p]
                            self.area_desenho.definir_preview_polilinha(pontos if len(pontos) >= 2 else None)
                        except Exception:
                            self.area_desenho.limpar_preview_polilinha()
                    # Atualiza a prévia da janela poligonal ao digitar
                    if evento.ui_element == self.painel_controle.elementos_recorte.get('entrada_clip_pontos'):
                        try:
                            pts_str = [p.strip() for p in self.painel_controle.elementos_recorte['entrada_clip_pontos'].get_text().split(';')]
                            pts = [tuple(map(int, p.split(','))) for p in pts_str if p]
                            self.clip_poly_pontos = pts
                            self.area_desenho.definir_preview_clip_poligono(pts if len(pts) >= 2 else None)
                        except Exception:
                            self.clip_poly_pontos = []
                            self.area_desenho.limpar_preview_clip_poligono()
            self.painel_controle.atualizar_historico(self.area_desenho.obter_historico(), self.area_desenho.obter_indice_selecionado())
            # Atualiza a janela de recorte (retângulo vermelho ou polígono) a cada frame
            try:
                idx = self.area_desenho.obter_indice_selecionado()
                if idx is not None:
                    d = self.area_desenho.obter_historico()[idx]
                    if d.tipo == "Linha (Bresenham)":
                        self.area_desenho.limpar_preview_clip_poligono()
                        left = int(self.painel_controle.elementos_recorte['left'].get_text())
                        bottom = int(self.painel_controle.elementos_recorte['bottom'].get_text())
                        right = int(self.painel_controle.elementos_recorte['right'].get_text())
                        top = int(self.painel_controle.elementos_recorte['top'].get_text())
                        xmin, xmax = sorted([left, right])
                        ymin, ymax = sorted([bottom, top])
                        self.area_desenho.definir_janela_recorte((xmin, ymin, xmax, ymax))
                    elif d.tipo == "Polilinha":
                        self.area_desenho.limpar_janela_recorte()
                        if not self.clip_poly_capturando:
                            pts_str = [p.strip() for p in self.painel_controle.elementos_recorte['entrada_clip_pontos'].get_text().split(';')]
                            pts = [tuple(map(int, p.split(','))) for p in pts_str if p]
                            self.area_desenho.definir_preview_clip_poligono(pts if len(pts) >= 2 else None)
                            self.clip_poly_pontos = pts
                    else:
                        self.area_desenho.limpar_janela_recorte()
                        self.area_desenho.limpar_preview_clip_poligono()
                else:
                    self.area_desenho.limpar_janela_recorte()
                    self.area_desenho.limpar_preview_clip_poligono()
            except Exception:
                # Em caso de valores inválidos, não desenha a janela nesse frame
                self.area_desenho.limpar_janela_recorte()
                self.area_desenho.limpar_preview_clip_poligono()
            self.ui_manager.update(delta_time)
            self.area_desenho.desenhar(self.tela)
            pygame.draw.rect(self.tela, COR_PAINEL, (LARGURA_CANVAS, 0, LARGURA_PAINEL, ALTURA_TOTAL))
            self.ui_manager.draw_ui(self.tela)
            pygame.display.flip()
        pygame.quit()

    def _obter_vertices_selecionados(self):
        indice = self.area_desenho.obter_indice_selecionado()
        if indice is None:
            print("Nenhum objeto selecionado para transformar.")
            return None, None
        desenho = self.area_desenho.obter_historico()[indice]
        if desenho.tipo == "Linha (Bresenham)":
            pontos = [desenho.parametros['p1'], desenho.parametros['p2']]
        elif desenho.tipo == "Curva de Bézier":
            pontos = [desenho.parametros[f'p{i}'] for i in range(4)]
        elif desenho.tipo == "Polilinha":
            pontos = desenho.parametros.get('pontos', [])
        elif desenho.tipo == "Pontos":
            pontos = desenho.parametros.get('pontos', [])
        else:
            # Para outros tipos como Círculo/Elipse, não há vértices a priori
            return desenho, []
        return desenho, pontos

    def _atualizar_vertices_desenho(self, desenho, novos_pontos):
        if desenho.tipo == "Linha (Bresenham)":
            desenho.parametros['p1'] = novos_pontos[0]
            desenho.parametros['p2'] = novos_pontos[1]
        elif desenho.tipo == "Curva de Bézier":
            for i, ponto in enumerate(novos_pontos):
                desenho.parametros[f'p{i}'] = ponto
        elif desenho.tipo == "Polilinha":
            desenho.parametros['pontos'] = novos_pontos
        elif desenho.tipo == "Pontos":
            desenho.parametros['pontos'] = novos_pontos

    def _converter_para_polilinha(self, desenho):
        # Conversão de figuras paramétricas (Círculo/Elipse) para polilinha
        # para que transformações gerais (escala/rotação não-uniformes) possam
        # ser aplicadas ponto a ponto quando necessário.
        print(f"Convertendo '{desenho.tipo}' para Polilinha.")
        pontos = []
        params = desenho.parametros
        centro = params.get('centro', (0, 0))
        num_segmentos = 36
        if desenho.tipo == "Círculo":
            raio = params.get('raio', 0)
            for i in range(num_segmentos):
                angulo = 2 * math.pi * i / num_segmentos
                x = centro[0] + raio * math.cos(angulo)
                y = centro[1] + raio * math.sin(angulo)
                pontos.append((round(x), round(y)))
        elif desenho.tipo == "Elipse":
            rx, ry = params.get('rx', 0), params.get('ry', 0)
            for i in range(num_segmentos):
                angulo = 2 * math.pi * i / num_segmentos
                x = centro[0] + rx * math.cos(angulo)
                y = centro[1] + ry * math.sin(angulo)
                pontos.append((round(x), round(y)))
        desenho.tipo = "Polilinha"
        desenho.parametros = {'pontos': pontos}
        return pontos

    def definir_coordenadas_por_clique(self, coords):
        """
        Recebe coordenadas em grade a partir de um clique no canvas e injeta
        o valor no campo associado ao último botão "Def" clicado.

        Também suporta um modo especial ('flood') para acionar Flood Fill com
        seed em coordenadas de grade.
        """
        tipo_figura, ponto = self.proximo_clique_define
        x_str, y_str = str(coords[0]), str(coords[1])
        if tipo_figura == 'linha':
            self.painel_controle.elementos_linha[f'{ponto}_x'].set_text(x_str)
            self.painel_controle.elementos_linha[f'{ponto}_y'].set_text(y_str)
        elif tipo_figura == 'circulo':
            self.painel_controle.elementos_circulo['centro_x'].set_text(x_str)
            self.painel_controle.elementos_circulo['centro_y'].set_text(y_str)
        elif tipo_figura == 'elipse':
            self.painel_controle.elementos_elipse['centro_x'].set_text(x_str)
            self.painel_controle.elementos_elipse['centro_y'].set_text(y_str)
        elif tipo_figura == 'bezier':
            self.painel_controle.elementos_bezier[f'{ponto}_x'].set_text(x_str)
            self.painel_controle.elementos_bezier[f'{ponto}_y'].set_text(y_str)
        elif tipo_figura == 'triangulo':
            self.painel_controle.elementos_triangulo[f'{ponto}_x'].set_text(x_str)
            self.painel_controle.elementos_triangulo[f'{ponto}_y'].set_text(y_str)
        elif tipo_figura == 'quadrilatero':
            self.painel_controle.elementos_quadrilatero[f'{ponto}_x'].set_text(x_str)
            self.painel_controle.elementos_quadrilatero[f'{ponto}_y'].set_text(y_str)
        elif tipo_figura == 'pentagono':
            self.painel_controle.elementos_pentagono[f'{ponto}_x'].set_text(x_str)
            self.painel_controle.elementos_pentagono[f'{ponto}_y'].set_text(y_str)
        elif tipo_figura == 'hexagono':
            self.painel_controle.elementos_hexagono[f'{ponto}_x'].set_text(x_str)
            self.painel_controle.elementos_hexagono[f'{ponto}_y'].set_text(y_str)
        elif tipo_figura == 'recorte':
            # Campos de margem: left/right usam X; bottom/top usam Y
            try:
                if ponto in ('left', 'right'):
                    self.painel_controle.elementos_recorte[ponto].set_text(x_str)
                elif ponto in ('bottom', 'top'):
                    self.painel_controle.elementos_recorte[ponto].set_text(y_str)
            except KeyError:
                pass
        elif tipo_figura == 'flood':
            # Flood fill livre no canvas: preenche região vazia conectada à seed
            seed = (coords[0], coords[1])
            historico = self.area_desenho.obter_historico()
            ocupados = set()
            for d in historico:
                pixels = self.area_desenho.rasterizar_desenho(d)
                for p in pixels:
                    ocupados.add(tuple(p))
            # Limites do grid (em coords de grade)
            min_x = - (self.area_desenho.largura_grid // 2)
            max_x = (self.area_desenho.largura_grid // 2)
            min_y = - (self.area_desenho.altura_grid // 2)
            max_y = (self.area_desenho.altura_grid // 2)
            preenchidos = preencher_flood_canvas(ocupados, seed, (min_x, max_x, min_y, max_y))
            if not preenchidos:
                print("Nada a preencher (seed inválida ou célula já ocupada).")
                return
            self.area_desenho.adicionar_forma("Pontos", { 'pontos': preenchidos })
        

    def manipular_selecao_historico(self, evento):
        """
        Alterna seleção no histórico. Um novo clique no item já selecionado
        desseleciona (toggle). A lista de strings tem prefixo "* " no item
        atualmente selecionado, mas o índice é extraído pelo prefixo "N.".
        """
        item_selecionado = evento.text
        if not item_selecionado:
            self.area_desenho.selecionar_desenho(None)
            return
        try:
            if item_selecionado.startswith('* '):
                item_selecionado = item_selecionado[2:]
            indice = int(item_selecionado.split('.')[0]) - 1
            # Toggle: se já está selecionado e clicar de novo, desseleciona
            atual = self.area_desenho.obter_indice_selecionado()
            if atual == indice:
                self.area_desenho.selecionar_desenho(None)
            else:
                self.area_desenho.selecionar_desenho(indice)
        except (ValueError, IndexError):
            self.area_desenho.selecionar_desenho(None)

    def manipular_eventos_ui(self, evento):
        """
        Roteador central de cliques de botões da UI.

        Despacha por elemento, agrupado em blocos:
        - Configurações e Projeções 3D
        - Desenho de figuras
        - Polilinha (texto e por clique)
        - Recorte (margens e janela convexa)
        - Transformações (trans/escala/rotação)
        - Preenchimentos (scanline e flood)
        - Botões de definição (Def) e ações gerais (limpar/desfazer)
        """
        painel = self.painel_controle
        if evento.ui_element == painel.botao_aplicar_res:
            try:
                self.area_desenho.atualizar_resolucao_grid(int(painel.entrada_largura.get_text()), int(painel.entrada_altura.get_text()))
            except ValueError: print("Erro: A resolução deve ser um número inteiro.")
        elif evento.ui_element == painel.elementos_projecao.get('botao'):
            # Abre (ou foca) o painel de Projeções 3D, que contém os controles
            # de tipo de sólido, projeção e parâmetros opcionais.
            if self.painel_projecoes is None or not self.painel_projecoes.alive():
                self.painel_projecoes = PainelProjecoes(self.ui_manager, LARGURA_CANVAS)
            else:
                self.painel_projecoes.focus()
        elif self.painel_projecoes is not None and evento.ui_element == self.painel_projecoes.botao_desenhar:
            # Lê parâmetros do painel e projeta o sólido 3D para 2D, em seguida
            # monta uma cadeia contínua (polilinha única) que percorre arestas.
            if self.painel_projecoes is None or not self.painel_projecoes.alive():
                return  # Painel não está visível

            # A opção selecionada é uma tupla (texto, id), então pegamos o primeiro elemento
            tipo_solido = self.painel_projecoes.seletor_solido.selected_option[0]
            tipo_projecao = self.painel_projecoes.seletor_projecao.selected_option[0]

            vertices_3d = []
            arestas = []

            if tipo_solido == 'Cubo':
                vertices_3d = obter_cubo_padrao(escala=25)
                arestas = obter_arestas_cubo()
            elif tipo_solido == 'Poliedro (Vértices)':
                try:
                    v_str = self.painel_projecoes.entrada_vertices.get_text()
                    vertices_3d = [tuple(map(int, p.split(','))) for p in v_str.split(';') if p.strip()]
                    
                    a_str = self.painel_projecoes.entrada_arestas.get_text()
                    arestas = [tuple(map(int, p.split(','))) for p in a_str.split(';') if p.strip()]

                    if not vertices_3d or not arestas:
                        print("Erro: Vértices ou arestas do poliedro personalizado estão vazios.")
                        return
                except (ValueError, IndexError) as e:
                    print(f"Erro de formato para vértices ou arestas: {e}. Use x,y,z;... e i1,i2;...")
                    return
            
            if not vertices_3d:
                print("Sólido não reconhecido ou sem vértices.")
                return

            try:
                angulo_obliquo = int(self.painel_projecoes.entrada_angulo_obliquo.get_text())
            except (ValueError, AttributeError):
                angulo_obliquo = 45 # Valor padrão em caso de erro

            vertices_2d = []
            try:
                if tipo_projecao == 'Ortogonal':
                    vertices_2d = projecao_ortogonal(vertices_3d, plano='frontal')
                elif tipo_projecao == 'Cavalier':
                    vertices_2d = projecao_cavalier(vertices_3d, angulo_graus=angulo_obliquo)
                elif tipo_projecao == 'Cabinet':
                    vertices_2d = projecao_cabinet(vertices_3d, angulo_graus=angulo_obliquo)
                elif tipo_projecao == 'Perspectiva':
                    try:
                        obs_x = int(self.painel_projecoes.entrada_obs_x.get_text())
                        obs_y = int(self.painel_projecoes.entrada_obs_y.get_text())
                        obs_z = int(self.painel_projecoes.entrada_obs_z.get_text())
                        ponto_observador = (obs_x, obs_y, obs_z)
                        vertices_2d = projecao_perspectiva(vertices_3d, ponto_observador=ponto_observador)
                    except (ValueError, AttributeError) as e:
                        print(f"Erro nos parâmetros do ponto de observação: {e}")
                        # Fallback para projeção padrão se os campos não existirem ou forem inválidos
                        vertices_2d = projecao_perspectiva(vertices_3d)
            except Exception as e:
                print(f"Erro ao calcular projeção: {e}")
                return

            if not vertices_2d:
                print("Falha ao projetar os vértices.")
                return

            # Constrói uma cadeia contínua que percorre todas as arestas (pode
            # repetir vértices/arestas) para representar a projeção inteira como
            # uma única Polilinha.
            try:
                n = len(vertices_2d)
                adj = {i: set() for i in range(n)}
                unused = set()
                for (a, b) in arestas:
                    if a < 0 or b < 0 or a >= n or b >= n:
                        raise IndexError(f"Aresta inválida ({a},{b}) para {n} vértices 2D")
                    adj[a].add(b)
                    adj[b].add(a)
                    key = (min(a, b), max(a, b))
                    unused.add(key)

                # Encontra um vértice de início com alguma aresta
                start = next((i for i in range(n) if adj[i]), None)
                if start is None:
                    print("Sólido sem arestas projetadas.")
                    return

                from collections import deque

                def bfs_to_vertex_with_unused_edge(src):
                    """Encontra caminho por vértices de src até algum vértice com aresta não usada."""
                    q = deque([src])
                    prev = {src: None}
                    target = None
                    while q:
                        v = q.popleft()
                        # Verifica se v possui alguma aresta não usada
                        has_unused = any((min(v, u), max(v, u)) in unused for u in adj[v])
                        if has_unused:
                            target = v
                            break
                        for u in adj[v]:
                            if u not in prev:
                                prev[u] = v
                                q.append(u)
                    if target is None:
                        return []
                    # Reconstrói caminho
                    path = []
                    cur = target
                    while cur is not None:
                        path.append(cur)
                        cur = prev[cur]
                    path.reverse()
                    return path  # lista de índices de vértices

                chain_indices = [start]
                cur = start
                while unused:
                    # Se não há aresta não usada partindo de cur, anda até uma que tenha
                    if not any((min(cur, u), max(cur, u)) in unused for u in adj[cur]):
                        path = bfs_to_vertex_with_unused_edge(cur)
                        if not path:
                            break
                        # já estamos em cur, então adiciona do segundo em diante
                        for v in path[1:]:
                            chain_indices.append(v)
                        cur = chain_indices[-1]
                        continue
                    # Usa uma aresta não usada e avança
                    # Escolhe um vizinho com aresta não usada
                    nxt = next(u for u in adj[cur] if (min(cur, u), max(cur, u)) in unused)
                    unused.discard((min(cur, nxt), max(cur, nxt)))
                    chain_indices.append(nxt)
                    cur = nxt

                chain_points = [vertices_2d[i] for i in chain_indices]
                if len(chain_points) >= 2:
                    self.area_desenho.adicionar_forma("Polilinha", {'pontos': chain_points})
                    print(f"Projeção {tipo_projecao}: cadeia única com {len(chain_points)-1} segmentos.")
                else:
                    print("Projeção resultou em cadeia insuficiente para desenhar.")
            except Exception as e:
                print(f"Erro ao montar polilinha única: {e}")
        
        # --- Lógica de Desenho ---
        elif evento.ui_element == painel.elementos_linha.get('botao'):
            try:
                p1 = (int(painel.elementos_linha['p1_x'].get_text()), int(painel.elementos_linha['p1_y'].get_text()))
                p2 = (int(painel.elementos_linha['p2_x'].get_text()), int(painel.elementos_linha['p2_y'].get_text()))
                self.area_desenho.adicionar_forma("Linha (Bresenham)", {'p1': p1, 'p2': p2})
            except ValueError: print("Erro: As coordenadas da linha devem ser números inteiros.")
        elif evento.ui_element == painel.elementos_circulo.get('botao'):
            try:
                centro = (int(painel.elementos_circulo['centro_x'].get_text()), int(painel.elementos_circulo['centro_y'].get_text()))
                raio = int(painel.elementos_circulo['raio'].get_text())
                self.area_desenho.adicionar_forma("Círculo", {'centro': centro, 'raio': raio})
            except ValueError: print("Erro: As coordenadas do centro e o raio devem ser números inteiros.")
        elif evento.ui_element == painel.elementos_bezier.get('botao'):
            try:
                pontos = [(int(painel.elementos_bezier[f'p{i}_x'].get_text()), int(painel.elementos_bezier[f'p{i}_y'].get_text())) for i in range(4)]
                self.area_desenho.adicionar_forma("Curva de Bézier", {f'p{i}': p for i, p in enumerate(pontos)})
            except ValueError: print("Erro: As coordenadas dos pontos de controle devem ser números inteiros.")
        elif evento.ui_element == painel.elementos_elipse.get('botao'):
            try:
                centro = (int(painel.elementos_elipse['centro_x'].get_text()), int(painel.elementos_elipse['centro_y'].get_text()))
                rx, ry = int(painel.elementos_elipse['rx'].get_text()), int(painel.elementos_elipse['ry'].get_text())
                self.area_desenho.adicionar_forma("Elipse", {'centro': centro, 'rx': rx, 'ry': ry})
            except ValueError: print("Erro: As coordenadas do centro e os raios devem ser números inteiros.")
        elif evento.ui_element == painel.elementos_triangulo.get('botao'):
            try:
                p1 = (int(painel.elementos_triangulo['p1_x'].get_text()), int(painel.elementos_triangulo['p1_y'].get_text()))
                p2 = (int(painel.elementos_triangulo['p2_x'].get_text()), int(painel.elementos_triangulo['p2_y'].get_text()))
                p3 = (int(painel.elementos_triangulo['p3_x'].get_text()), int(painel.elementos_triangulo['p3_y'].get_text()))
                pts = [p1, p2, p3, p1]
                self.area_desenho.adicionar_forma("Polilinha", { 'pontos': pts })
            except ValueError:
                print("Erro: As coordenadas do triângulo devem ser números inteiros.")
        elif evento.ui_element == painel.elementos_quadrilatero.get('botao'):
            try:
                p1 = (int(painel.elementos_quadrilatero['p1_x'].get_text()), int(painel.elementos_quadrilatero['p1_y'].get_text()))
                p2 = (int(painel.elementos_quadrilatero['p2_x'].get_text()), int(painel.elementos_quadrilatero['p2_y'].get_text()))
                p3 = (int(painel.elementos_quadrilatero['p3_x'].get_text()), int(painel.elementos_quadrilatero['p3_y'].get_text()))
                p4 = (int(painel.elementos_quadrilatero['p4_x'].get_text()), int(painel.elementos_quadrilatero['p4_y'].get_text()))
                pts = [p1, p2, p3, p4, p1]
                self.area_desenho.adicionar_forma("Polilinha", { 'pontos': pts })
            except ValueError:
                print("Erro: As coordenadas do quadrilátero devem ser números inteiros.")
        elif evento.ui_element == painel.elementos_pentagono.get('botao'):
            try:
                p1 = (int(painel.elementos_pentagono['p1_x'].get_text()), int(painel.elementos_pentagono['p1_y'].get_text()))
                p2 = (int(painel.elementos_pentagono['p2_x'].get_text()), int(painel.elementos_pentagono['p2_y'].get_text()))
                p3 = (int(painel.elementos_pentagono['p3_x'].get_text()), int(painel.elementos_pentagono['p3_y'].get_text()))
                p4 = (int(painel.elementos_pentagono['p4_x'].get_text()), int(painel.elementos_pentagono['p4_y'].get_text()))
                p5 = (int(painel.elementos_pentagono['p5_x'].get_text()), int(painel.elementos_pentagono['p5_y'].get_text()))
                pts = [p1, p2, p3, p4, p5, p1]
                self.area_desenho.adicionar_forma("Polilinha", { 'pontos': pts })
            except ValueError:
                print("Erro: As coordenadas do pentágono devem ser números inteiros.")
        elif evento.ui_element == painel.elementos_hexagono.get('botao'):
            try:
                p1 = (int(painel.elementos_hexagono['p1_x'].get_text()), int(painel.elementos_hexagono['p1_y'].get_text()))
                p2 = (int(painel.elementos_hexagono['p2_x'].get_text()), int(painel.elementos_hexagono['p2_y'].get_text()))
                p3 = (int(painel.elementos_hexagono['p3_x'].get_text()), int(painel.elementos_hexagono['p3_y'].get_text()))
                p4 = (int(painel.elementos_hexagono['p4_x'].get_text()), int(painel.elementos_hexagono['p4_y'].get_text()))
                p5 = (int(painel.elementos_hexagono['p5_x'].get_text()), int(painel.elementos_hexagono['p5_y'].get_text()))
                p6 = (int(painel.elementos_hexagono['p6_x'].get_text()), int(painel.elementos_hexagono['p6_y'].get_text()))
                pts = [p1, p2, p3, p4, p5, p6, p1]
                self.area_desenho.adicionar_forma("Polilinha", { 'pontos': pts })
            except ValueError:
                print("Erro: As coordenadas do hexágono devem ser números inteiros.")
        elif evento.ui_element == painel.elementos_polilinha.get('botao'):
            try:
                pontos_str = [p.strip() for p in painel.elementos_polilinha['entrada_pontos'].get_text().split(';')]
                pontos = [tuple(map(int, p.split(','))) for p in pontos_str if p]
                if len(pontos) < 2: print("Erro: A polilinha precisa de pelo menos 2 pontos."); return
                self.area_desenho.adicionar_forma("Polilinha", {'pontos': pontos})
            except ValueError: print("Erro: Formato dos pontos inválido. Use 'x1,y1; x2,y2; ...'")
        elif evento.ui_element == painel.elementos_polilinha.get('btn_iniciar_clique'):
            self.polilinha_capturando = True
            self.polilinha_pontos = []
            self.painel_controle.elementos_polilinha['entrada_pontos'].set_text('')
            print("Clique no canvas para adicionar vértices. Clique em 'Finalizar' para concluir.")
            # Limpa a pré-visualização até que pontos sejam adicionados
            self.area_desenho.limpar_preview_polilinha()
        elif evento.ui_element == painel.elementos_polilinha.get('btn_usar_predef'):
            # Gera uma polilinha regular centrada conforme a escolha
            try:
                opc = painel.elementos_polilinha['dropdown_predef'].selected_option
                if isinstance(opc, tuple):
                    opc = opc[0]
            except Exception:
                opc = 'Triângulo'

            lados_map = {
                'Triângulo': 3,
                'Quadrilátero': 4,
                'Pentágono': 5,
                'Hexágono': 6,
            }
            n = lados_map.get(opc, 3)
            # Define um "raio" baseado na grade para caber na tela
            rx = max(8, min(40, self.area_desenho.largura_grid // 6))
            ry = max(8, min(40, self.area_desenho.altura_grid // 6))
            r = min(rx, ry)
            cx, cy = 0, 0
            import math
            pontos = []
            # Orientação: polígono com um vértice para cima (ângulo -90º)
            ang0 = -math.pi / 2
            for i in range(n):
                ang = ang0 + 2 * math.pi * i / n
                x = round(cx + r * math.cos(ang))
                y = round(cy + r * math.sin(ang))
                pontos.append((x, y))
            # fecha a cadeia para facilitar testes
            if pontos and pontos[0] != pontos[-1]:
                pontos.append(pontos[0])
            # Atualiza campo de texto e preview
            try:
                texto = '; '.join(f"{x},{y}" for x, y in pontos)
                painel.elementos_polilinha['entrada_pontos'].set_text(texto)
            except Exception:
                pass
            self.area_desenho.definir_preview_polilinha(pontos if len(pontos) >= 2 else None)
        elif evento.ui_element == painel.elementos_polilinha.get('btn_finalizar_clique'):
            if len(self.polilinha_pontos) < 2:
                print("Polilinha por clique requer pelo menos 2 pontos.")
            else:
                self.area_desenho.adicionar_forma("Polilinha", {'pontos': list(self.polilinha_pontos)})
            self.polilinha_capturando = False
            self.polilinha_pontos = []
            # Remove a prévia após finalizar
            self.area_desenho.limpar_preview_polilinha()
        elif evento.ui_element == painel.elementos_polilinha.get('btn_ligar_primeiro'):
            # Fecha a polilinha ligando o último ponto ao primeiro
            if self.polilinha_capturando:
                if len(self.polilinha_pontos) >= 1 and self.polilinha_pontos[-1] != self.polilinha_pontos[0]:
                    self.polilinha_pontos.append(self.polilinha_pontos[0])
                    try:
                        texto = '; '.join(f"{x},{y}" for x, y in self.polilinha_pontos)
                        self.painel_controle.elementos_polilinha['entrada_pontos'].set_text(texto)
                    except Exception:
                        pass
                    # Atualiza prévia ao fechar
                    self.area_desenho.definir_preview_polilinha(self.polilinha_pontos)
            else:
                try:
                    pontos_str = [p.strip() for p in painel.elementos_polilinha['entrada_pontos'].get_text().split(';')]
                    pontos = [tuple(map(int, p.split(','))) for p in pontos_str if p]
                    if pontos:
                        if pontos[-1] != pontos[0]:
                            pontos.append(pontos[0])
                            texto = '; '.join(f"{x},{y}" for x, y in pontos)
                            self.painel_controle.elementos_polilinha['entrada_pontos'].set_text(texto)
                        # Atualiza prévia baseada no texto ajustado
                        self.area_desenho.definir_preview_polilinha(pontos if len(pontos) >= 2 else None)
                except ValueError:
                    print("Erro: Formato dos pontos inválido. Use 'x1,y1; x2,y2; ...'")

        # --- Recorte por janela poligonal convexa (definida por clique) ---
        elif evento.ui_element == painel.elementos_recorte.get('btn_clip_iniciar'):
            # Inicia captura de janela de recorte por clique
            self.clip_poly_capturando = True
            self.clip_poly_pontos = []
            self.area_desenho.limpar_preview_clip_poligono()
            print("Clique no canvas para definir os vértices da janela (convexa). Clique em 'Finalizar' para aplicar.")
        elif evento.ui_element == painel.elementos_recorte.get('btn_clip_finalizar'):
            # Finaliza captura e aplica recorte se convexa
            if len(self.clip_poly_pontos) < 3:
                print("A janela poligonal requer pelo menos 3 vértices.")
                self.clip_poly_capturando = False
                # mantém a prévia para referência
                return
            # Valida convexidade
            if not eh_convexo(self.clip_poly_pontos):
                print("Janela inválida: o polígono não é convexo. Redefina com pontos convexos.")
                self.clip_poly_capturando = False
                # mantém a prévia para o usuário visualizar o erro
                return

            # Atualiza o campo de texto com os pontos da janela que será usada
            try:
                texto_pontos = '; '.join(f"{x},{y}" for x, y in self.clip_poly_pontos)
                painel.elementos_recorte['entrada_clip_pontos'].set_text(texto_pontos)
            except Exception as e:
                print(f"Erro ao atualizar campo de texto da janela: {e}")

            # Aplica recorte apenas para Polilinha selecionada
            indice_sel = self.area_desenho.obter_indice_selecionado()
            if indice_sel is None:
                print("Selecione uma Polilinha para aplicar o recorte.")
                self.clip_poly_capturando = False
                return
            desenho = self.area_desenho.obter_historico()[indice_sel]
            if desenho.tipo != 'Polilinha':
                print("Recorte poligonal disponível apenas para Polilinha.")
                self.clip_poly_capturando = False
                return
            subject = desenho.parametros.get('pontos', [])
            # Remove fechamento duplicado do sujeito, se houver
            if len(subject) >= 2 and subject[0] == subject[-1]:
                subject = subject[:-1]
            clip_poly = self.clip_poly_pontos[:]
            resultado = suth_hodgman_clip_convexo(subject, clip_poly)
            if resultado:
                # Garante fechamento para rasterização de polilinha
                if resultado[0] != resultado[-1]:
                    resultado.append(resultado[0])
                desenho.parametros['pontos'] = resultado
                print("Polilinha recortada pela janela convexa.")
            else:
                # Nada restou — remove desenho
                self.area_desenho.remover_desenho_indice(indice_sel)
                print("Polilinha completamente fora da janela convexa. Removida.")
            
            # Finaliza o modo de captura, mas mantém a janela (pontos e preview) para referência futura
            self.clip_poly_capturando = False
        
        # --- Lógica de Transformação ---
        elif evento.ui_element == painel.elementos_transformacao.get('btn_trans'):
            indice_selecionado = self.area_desenho.obter_indice_selecionado()
            if indice_selecionado is None: print("Nenhum objeto selecionado."); return
            desenho = self.area_desenho.obter_historico()[indice_selecionado]
            try:
                tx = int(painel.elementos_transformacao['trans_x'].get_text())
                ty = int(painel.elementos_transformacao['trans_y'].get_text())
                if desenho.tipo in ["Círculo", "Elipse"]:
                    cx, cy = desenho.parametros['centro']
                    desenho.parametros['centro'] = (cx + tx, cy + ty)
                elif desenho.tipo == "Pontos":
                    novos = transform.transladar(desenho.parametros.get('pontos', []), tx, ty)
                    desenho.parametros['pontos'] = novos
                else:
                    desenho_v, pontos = self._obter_vertices_selecionados()
                    if not desenho_v: return
                    novos_pontos = transform.transladar(pontos, tx, ty)
                    self._atualizar_vertices_desenho(desenho, novos_pontos)
            except ValueError: print("Erro nos parâmetros de translação.")

        elif evento.ui_element == painel.elementos_transformacao.get('btn_escala'):
            indice_selecionado = self.area_desenho.obter_indice_selecionado()
            if indice_selecionado is None: print("Nenhum objeto selecionado."); return
            desenho = self.area_desenho.obter_historico()[indice_selecionado]
            try:
                sx = float(painel.elementos_transformacao['escala_sx'].get_text())
                sy = float(painel.elementos_transformacao['escala_sy'].get_text())
                cx = int(painel.elementos_transformacao['escala_cx'].get_text())
                cy = int(painel.elementos_transformacao['escala_cy'].get_text())
                ponto_fixo = (cx, cy)

                if desenho.tipo == "Círculo" and sx == sy:
                    print("Aplicando escala uniforme em forma paramétrica.")
                    centro_antigo = desenho.parametros['centro']
                    novo_centro_x = ponto_fixo[0] + (centro_antigo[0] - ponto_fixo[0]) * sx
                    novo_centro_y = ponto_fixo[1] + (centro_antigo[1] - ponto_fixo[1]) * sy
                    desenho.parametros['centro'] = (round(novo_centro_x), round(novo_centro_y))
                    if desenho.tipo == "Círculo":
                        desenho.parametros['raio'] = round(desenho.parametros['raio'] * sx)
                    else:
                        desenho.parametros['rx'] = round(desenho.parametros['rx'] * sx)
                        desenho.parametros['ry'] = round(desenho.parametros['ry'] * sy)
                elif desenho.tipo == "Elipse":
                    print("Aplicando escala uniforme em forma paramétrica.")
                    centro_antigo = desenho.parametros['centro']
                    novo_centro_x = ponto_fixo[0] + (centro_antigo[0] - ponto_fixo[0]) * sx
                    novo_centro_y = ponto_fixo[1] + (centro_antigo[1] - ponto_fixo[1]) * sy
                    desenho.parametros['centro'] = (round(novo_centro_x), round(novo_centro_y))
                    desenho.parametros['rx'] = round(desenho.parametros['rx'] * sx)
                    desenho.parametros['ry'] = round(desenho.parametros['ry'] * sy)
                elif desenho.tipo == "Pontos":
                    novos = transform.escalar(desenho.parametros.get('pontos', []), sx, sy, ponto_fixo)
                    desenho.parametros['pontos'] = novos
                else:
                    pontos = []
                    if desenho.tipo in ["Círculo", "Elipse"]:
                        pontos = self._converter_para_polilinha(desenho)
                    else:
                        _, pontos = self._obter_vertices_selecionados()
                    if not pontos: return
                    novos_pontos = transform.escalar(pontos, sx, sy, ponto_fixo)
                    self._atualizar_vertices_desenho(desenho, novos_pontos)
            except ValueError: print("Erro nos parâmetros de escala.")

        elif evento.ui_element == painel.elementos_transformacao.get('btn_rot'):
            indice_selecionado = self.area_desenho.obter_indice_selecionado()
            if indice_selecionado is None: print("Nenhum objeto selecionado."); return
            desenho = self.area_desenho.obter_historico()[indice_selecionado]
            try:
                angulo = float(painel.elementos_transformacao['rot_angulo'].get_text())
                px = int(painel.elementos_transformacao['rot_px'].get_text())
                py = int(painel.elementos_transformacao['rot_py'].get_text())
                if desenho.tipo == "Círculo":
                    # Rotaciona cada pixel rasterizado do círculo e passa a tratá-lo como 'Pontos'
                    pixels = calcular_circulo(desenho.parametros['centro'], desenho.parametros['raio'])
                    novos_pontos = transform.rotacionar(pixels, angulo, (px, py))
                    desenho.tipo = "Pontos"
                    desenho.parametros = { 'pontos': novos_pontos }
                elif desenho.tipo == "Elipse":
                    pixels = calcular_elipse(desenho.parametros['centro'], desenho.parametros['rx'], desenho.parametros['ry'])
                    novos_pontos = transform.rotacionar(pixels, angulo, (px, py))
                    desenho.tipo = "Pontos"
                    desenho.parametros = { 'pontos': novos_pontos }
                elif desenho.tipo == "Pontos":
                    novos_pontos = transform.rotacionar(desenho.parametros.get('pontos', []), angulo, (px, py))
                    desenho.parametros['pontos'] = novos_pontos
                else:
                    _, pontos = self._obter_vertices_selecionados()
                    if not pontos: return
                    novos_pontos = transform.rotacionar(pontos, angulo, (px, py))
                    self._atualizar_vertices_desenho(desenho, novos_pontos)
            except ValueError: print("Erro nos parâmetros de rotação.")

        elif evento.ui_element == painel.elementos_recorte.get('botao'):
            indice_selecionado = self.area_desenho.obter_indice_selecionado()
            if indice_selecionado is None:
                print("Nenhum objeto selecionado."); return
            desenho = self.area_desenho.obter_historico()[indice_selecionado]
            try:
                # Janela a partir das margens (unificado)
                left = int(painel.elementos_recorte['left'].get_text())
                bottom = int(painel.elementos_recorte['bottom'].get_text())
                right = int(painel.elementos_recorte['right'].get_text())
                top = int(painel.elementos_recorte['top'].get_text())
                xmin, xmax = sorted([left, right])
                ymin, ymax = sorted([bottom, top])

                self.area_desenho.definir_janela_recorte((xmin, ymin, xmax, ymax))

                if desenho.tipo == "Linha (Bresenham)":
                    p1 = desenho.parametros['p1']
                    p2 = desenho.parametros['p2']
                    resultado = cohen_sutherland_clip(p1, p2, xmin, ymin, xmax, ymax)
                    if resultado:
                        desenho.parametros['p1'], desenho.parametros['p2'] = resultado
                        print("Linha recortada com sucesso.")
                    else:
                        self.area_desenho.remover_desenho_indice(indice_selecionado)
                        self.area_desenho.limpar_janela_recorte()
                        print("Linha completamente fora da área de recorte. Removida.")
                elif desenho.tipo == "Polilinha":
                    subject_polygon = desenho.parametros.get('pontos', [])
                    # Remove vértice duplicado de fechamento, se existir, para evitar arestas degeneradas no recorte
                    if len(subject_polygon) >= 2 and subject_polygon[0] == subject_polygon[-1]:
                        subject_polygon = subject_polygon[:-1]
                    clip_window = (xmin, ymin, xmax, ymax)
                    clipped_polygon = sutherland_hodgman_clip(subject_polygon, clip_window)
                    if clipped_polygon:
                        # Garante polígono fechado para não perder a aresta de fechamento na rasterização
                        if len(clipped_polygon) >= 2 and clipped_polygon[0] != clipped_polygon[-1]:
                            clipped_polygon.append(clipped_polygon[0])
                        desenho.parametros['pontos'] = clipped_polygon
                        print("Polígono recortado com sucesso.")
                    else:
                        self.area_desenho.remover_desenho_indice(indice_selecionado)
                        print("Polígono completamente fora da área de recorte. Removido.")
                else:
                    print("Recorte disponível para Linha e Polilinha.")
            except ValueError:
                print("Erro nos parâmetros de recorte.")

    # Botão específico de polígono removido — recorte unificado no botão principal

        elif evento.ui_element == painel.elementos_transformacao.get('btn_preencher_scan'):
            # Preenche via Scanline: suporta Polilinha, Círculo e Elipse.
            indice_selecionado = self.area_desenho.obter_indice_selecionado()
            if indice_selecionado is None:
                # Sem seleção: trata todos os polígonos como um único conjunto (regra par-ímpar global)
                historico = self.area_desenho.obter_historico()
                todos_vertices = []
                for d in historico:
                    if d.tipo in ["Polilinha", "Círculo", "Elipse"]:
                        verts = self._vertices_para_preenchimento(d)
                        if len(verts) >= 3:
                            todos_vertices.append(verts)
                if not todos_vertices:
                    print("Nenhum polígono válido para preencher no canvas.")
                    return
                pixels = preencher_scanline_multi(todos_vertices)
                if not pixels:
                    print("Nada a preencher considerando todos os polígonos.")
                    return
                self.area_desenho.adicionar_forma("Pontos", { 'pontos': pixels })
                print(f"Scanline aplicado tratando {len(todos_vertices)} polígonos como um só.")
                return
            else:
                desenho = self.area_desenho.obter_historico()[indice_selecionado]
                if desenho.tipo not in ["Polilinha", "Círculo", "Elipse"]:
                    print("Scanline disponível para Polilinha, Círculo e Elipse.")
                    return
                vertices = self._vertices_para_preenchimento(desenho)
                if len(vertices) < 3:
                    print("Não há vértices suficientes para preencher.")
                    return
                pixels = preencher_scanline(vertices)
                if not pixels:
                    print("Nada a preencher (verifique se o polígono é simples/fechado).")
                    return
                self.area_desenho.adicionar_forma("Pontos", { 'pontos': pixels })

        elif evento.ui_element == painel.elementos_transformacao.get('btn_preencher_rec'):
            # Ativa modo seed por clique para Flood Fill
            print("Clique no canvas para definir a seed do Flood Fill (área vazia).")
            self.proximo_clique_define = ('flood', None)

        # --- Botões de Definição e Ações Gerais ---
        elif evento.ui_element in [painel.elementos_linha.get(k) for k in ['btn_p1', 'btn_p2']]:
            self.proximo_clique_define = ('linha', 'p1' if evento.ui_element == painel.elementos_linha.get('btn_p1') else 'p2')
        elif evento.ui_element == painel.elementos_circulo.get('btn_centro'): self.proximo_clique_define = ('circulo', 'centro')
        elif evento.ui_element == painel.elementos_elipse.get('btn_centro'): self.proximo_clique_define = ('elipse', 'centro')
        elif evento.ui_element in [painel.elementos_bezier.get(f'btn_p{i}') for i in range(4)]:
            p_map = {painel.elementos_bezier.get(f'btn_p{i}'): f'p{i}' for i in range(4)}
            self.proximo_clique_define = ('bezier', p_map[evento.ui_element])
        elif evento.ui_element in [painel.elementos_triangulo.get(k) for k in ['btn_p1','btn_p2','btn_p3']]:
            btn_map = {
                painel.elementos_triangulo.get('btn_p1'): 'p1',
                painel.elementos_triangulo.get('btn_p2'): 'p2',
                painel.elementos_triangulo.get('btn_p3'): 'p3',
            }
            self.proximo_clique_define = ('triangulo', btn_map[evento.ui_element])
        elif evento.ui_element in [painel.elementos_quadrilatero.get(k) for k in ['btn_p1','btn_p2','btn_p3','btn_p4']]:
            btn_map_q = {
                painel.elementos_quadrilatero.get('btn_p1'): 'p1',
                painel.elementos_quadrilatero.get('btn_p2'): 'p2',
                painel.elementos_quadrilatero.get('btn_p3'): 'p3',
                painel.elementos_quadrilatero.get('btn_p4'): 'p4',
            }
            self.proximo_clique_define = ('quadrilatero', btn_map_q[evento.ui_element])
        elif evento.ui_element in [painel.elementos_pentagono.get(k) for k in ['btn_p1','btn_p2','btn_p3','btn_p4','btn_p5']]:
            btn_map_p = {
                painel.elementos_pentagono.get('btn_p1'): 'p1',
                painel.elementos_pentagono.get('btn_p2'): 'p2',
                painel.elementos_pentagono.get('btn_p3'): 'p3',
                painel.elementos_pentagono.get('btn_p4'): 'p4',
                painel.elementos_pentagono.get('btn_p5'): 'p5',
            }
            self.proximo_clique_define = ('pentagono', btn_map_p[evento.ui_element])
        elif evento.ui_element in [painel.elementos_hexagono.get(k) for k in ['btn_p1','btn_p2','btn_p3','btn_p4','btn_p5','btn_p6']]:
            btn_map_h = {
                painel.elementos_hexagono.get('btn_p1'): 'p1',
                painel.elementos_hexagono.get('btn_p2'): 'p2',
                painel.elementos_hexagono.get('btn_p3'): 'p3',
                painel.elementos_hexagono.get('btn_p4'): 'p4',
                painel.elementos_hexagono.get('btn_p5'): 'p5',
                painel.elementos_hexagono.get('btn_p6'): 'p6',
            }
            self.proximo_clique_define = ('hexagono', btn_map_h[evento.ui_element])
        # Botões Def específicos do recorte (margens)
        elif evento.ui_element in [
            painel.elementos_recorte.get('btn_left'),
            painel.elementos_recorte.get('btn_bottom'),
            painel.elementos_recorte.get('btn_right'),
            painel.elementos_recorte.get('btn_top')
        ]:
            btn_map_r = {
                painel.elementos_recorte.get('btn_left'): 'left',
                painel.elementos_recorte.get('btn_bottom'): 'bottom',
                painel.elementos_recorte.get('btn_right'): 'right',
                painel.elementos_recorte.get('btn_top'): 'top',
            }
            campo = btn_map_r[evento.ui_element]
            self.proximo_clique_define = ('recorte', campo)
        elif evento.ui_element == painel.botao_limpar: self.area_desenho.limpar_pixels()
        elif evento.ui_element == painel.botao_desfazer: self.area_desenho.desfazer_ultimo_desenho()
        elif evento.ui_element == painel.botao_excluir_selecao:
            indice = self.area_desenho.obter_indice_selecionado()
            if indice is not None: self.area_desenho.remover_desenho_indice(indice)
