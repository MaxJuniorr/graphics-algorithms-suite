import math
import pygame
import pygame_gui
from interface.painel_controle import PainelControle
from interface.area_desenho import AreaDesenho
from algoritmos.bresenham import calcular_linha_bresenham
from algoritmos.circulo_elipse import calcular_circulo, calcular_elipse
from algoritmos.curvas_bezier import rasterizar_curva_bezier
from algoritmos.polilinha import rasterizar_polilinha
import algoritmos.transformacoes as transform

# --- Constantes de Layout ---
LARGURA_TOTAL = 1200
ALTURA_TOTAL = 800
LARGURA_PAINEL = 400
LARGURA_CANVAS = LARGURA_TOTAL - LARGURA_PAINEL
ALTURA_CANVAS = ALTURA_TOTAL
COR_PAINEL = (60, 60, 60)

class Aplicacao:
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

    def executar(self):
        while self.rodando:
            delta_time = self.clock.tick(60) / 1000.0
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.rodando = False
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    if self.proximo_clique_define and evento.pos[0] < LARGURA_CANVAS:
                        coords = self.area_desenho.tela_para_grade(*evento.pos)
                        self.definir_coordenadas_por_clique(coords)
                        self.proximo_clique_define = None
                self.ui_manager.process_events(evento)
                if evento.type == pygame_gui.UI_BUTTON_PRESSED:
                    self.manipular_eventos_ui(evento)
                elif evento.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    if evento.ui_element == self.painel_controle.seletor_figura:
                        self.painel_controle.mostrar_elementos_figura(evento.text)
                elif evento.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
                    if evento.ui_element == self.painel_controle.lista_historico:
                        self.manipular_selecao_historico(evento)
            self.painel_controle.atualizar_historico(self.area_desenho.obter_historico(), self.area_desenho.obter_indice_selecionado())
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

    def _converter_para_polilinha(self, desenho):
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
        tipo_figura, ponto = self.proximo_clique_define
        x_str, y_str = str(coords[0]), str(coords[1])
        if tipo_figura == 'linha':
            self.painel_controle.elementos_linha[f'{ponto}_x'].set_text(x_str)
            self.painel_controle.elementos_linha[f'{ponto}_y'].set_text(y_str)
        elif tipo_figura == 'circulo' or tipo_figura == 'elipse':
            self.painel_controle.elementos_circulo['centro_x'].set_text(x_str)
            self.painel_controle.elementos_circulo['centro_y'].set_text(y_str)
        elif tipo_figura == 'bezier':
            self.painel_controle.elementos_bezier[f'{ponto}_x'].set_text(x_str)
            self.painel_controle.elementos_bezier[f'{ponto}_y'].set_text(y_str)

    def manipular_selecao_historico(self, evento):
        item_selecionado = evento.text
        if not item_selecionado: self.area_desenho.selecionar_desenho(None); return
        try:
            if item_selecionado.startswith('* '): item_selecionado = item_selecionado[2:]
            indice = int(item_selecionado.split('.')[0]) - 1
            self.area_desenho.selecionar_desenho(indice)
        except (ValueError, IndexError): self.area_desenho.selecionar_desenho(None)

    def manipular_eventos_ui(self, evento):
        painel = self.painel_controle
        if evento.ui_element == painel.botao_aplicar_res:
            try:
                self.area_desenho.atualizar_resolucao_grid(int(painel.entrada_largura.get_text()), int(painel.entrada_altura.get_text()))
            except ValueError: print("Erro: A resolução deve ser um número inteiro.")
        
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
        elif evento.ui_element == painel.elementos_polilinha.get('botao'):
            try:
                pontos_str = [p.strip() for p in painel.elementos_polilinha['entrada_pontos'].get_text().split(';')]
                pontos = [tuple(map(int, p.split(','))) for p in pontos_str if p]
                if len(pontos) < 2: print("Erro: A polilinha precisa de pelo menos 2 pontos."); return
                self.area_desenho.adicionar_forma("Polilinha", {'pontos': pontos})
            except ValueError: print("Erro: Formato dos pontos inválido. Use 'x1,y1; x2,y2; ...'")
        
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
            pontos = []
            if desenho.tipo in ["Círculo", "Elipse"]:
                pontos = self._converter_para_polilinha(desenho)
            else:
                _, pontos = self._obter_vertices_selecionados()
            if not pontos: return
            try:
                angulo = float(painel.elementos_transformacao['rot_angulo'].get_text())
                px = int(painel.elementos_transformacao['rot_px'].get_text())
                py = int(painel.elementos_transformacao['rot_py'].get_text())
                novos_pontos = transform.rotacionar(pontos, angulo, (px, py))
                self._atualizar_vertices_desenho(desenho, novos_pontos)
            except ValueError: print("Erro nos parâmetros de rotação.")

        # --- Botões de Definição e Ações Gerais ---
        elif evento.ui_element in [painel.elementos_linha.get(k) for k in ['btn_p1', 'btn_p2']]:
            self.proximo_clique_define = ('linha', 'p1' if evento.ui_element == painel.elementos_linha.get('btn_p1') else 'p2')
        elif evento.ui_element == painel.elementos_circulo.get('btn_centro'): self.proximo_clique_define = ('circulo', 'centro')
        elif evento.ui_element == painel.elementos_elipse.get('btn_centro'): self.proximo_clique_define = ('elipse', 'centro')
        elif evento.ui_element in [painel.elementos_bezier.get(f'btn_p{i}') for i in range(4)]:
            p_map = {painel.elementos_bezier.get(f'btn_p{i}'): f'p{i}' for i in range(4)}
            self.proximo_clique_define = ('bezier', p_map[evento.ui_element])
        elif evento.ui_element == painel.botao_limpar: self.area_desenho.limpar_pixels()
        elif evento.ui_element == painel.botao_desfazer: self.area_desenho.desfazer_ultimo_desenho()
        elif evento.ui_element == painel.botao_excluir_selecao:
            indice = self.area_desenho.obter_indice_selecionado()
            if indice is not None: self.area_desenho.remover_desenho_indice(indice)
