import pygame
import pygame_gui


class PainelControle:
    def __init__(self, ui_manager, largura_painel, altura_total, largura_canvas):
        self.ui_manager = ui_manager
        self.largura_painel = largura_painel
        self.altura_total = altura_total
        self.largura_canvas = largura_canvas

        # Dicionários para armazenar elementos
        self.elementos_linha = {}
        self.elementos_circulo = {}
        self.elementos_bezier = {}
        self.elementos_elipse = {}

        self._historico_cache_str = None
        self._historico_itens = []

        self.construir_interface()
        self.mostrar_elementos_figura('Linha (Bresenham)')

    # ---------------- Interface -----------------
    def construir_interface(self):
        # Histórico (painel à direita)
        margem_direita = 10
        self.largura_historico = 200
        self.altura_historico = 260
        self.posicao_x_historico = self.largura_canvas + self.largura_painel - self.largura_historico - margem_direita

        self.historico_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((self.posicao_x_historico, 10), (self.largura_historico, self.altura_historico)),
            manager=self.ui_manager,
            object_id='#painel_historico'
        )

        self.historico_titulo = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, 2), (self.largura_historico, 20)),
            text='Histórico de Desenhos',
            manager=self.ui_manager,
            container=self.historico_panel
        )

        self.historico_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect((0, 24), (self.largura_historico, self.altura_historico - 30)),
            manager=self.ui_manager,
            container=self.historico_panel,
            allow_scroll_x=False,
            allow_scroll_y=True
        )

        # Configuração de grade
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.largura_canvas + 10, 10), (180, 20)),
            text='Configuração da Grade',
            manager=self.ui_manager
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.largura_canvas + 10, 40), (80, 20)),
            text='Largura:',
            manager=self.ui_manager
        )
        self.entrada_largura = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 90, 40), (100, 30)),
            manager=self.ui_manager, object_id='#largura_grid'
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.largura_canvas + 10, 80), (80, 20)),
            text='Altura:',
            manager=self.ui_manager
        )
        self.entrada_altura = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 90, 80), (100, 30)),
            manager=self.ui_manager, object_id='#altura_grid'
        )
        self.entrada_largura.set_text('80')
        self.entrada_altura.set_text('80')
        self.botao_aplicar_res = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 10, 120), (180, 40)),
            text='Aplicar Resolução',
            manager=self.ui_manager, object_id='#botao_aplicar_res'
        )

        # Seleção de figura
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.largura_canvas + 10, 180), (180, 20)),
            text='Selecione a Figura',
            manager=self.ui_manager
        )
        self.seletor_figura = pygame_gui.elements.UIDropDownMenu(
            options_list=['Linha (Bresenham)', 'Círculo', 'Curva de Bézier', 'Elipse'],
            starting_option='Linha (Bresenham)',
            relative_rect=pygame.Rect((self.largura_canvas + 10, 210), (180, 30)),
            manager=self.ui_manager
        )

        base_y = 260
        # Linha
        self.elementos_linha['label_p1'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y), (30, 20)),
            text='P1:', manager=self.ui_manager)
        self.elementos_linha['p1_x'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 40, base_y), (70, 30)),
            manager=self.ui_manager, object_id='#p1_x')
        self.elementos_linha['p1_y'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 120, base_y), (70, 30)),
            manager=self.ui_manager, object_id='#p1_y')
        self.elementos_linha['label_p2'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 40), (30, 20)),
            text='P2:', manager=self.ui_manager)
        self.elementos_linha['p2_x'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 40, base_y + 40), (70, 30)),
            manager=self.ui_manager, object_id='#p2_x')
        self.elementos_linha['p2_y'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 120, base_y + 40), (70, 30)),
            manager=self.ui_manager, object_id='#p2_y')
        for k,v in [('p1_x','10'),('p1_y','5'),('p2_x','70'),('p2_y','45')]:
            self.elementos_linha[k].set_text(v)
        self.elementos_linha['botao'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 80), (180, 40)),
            text='Desenhar Linha', manager=self.ui_manager, object_id='#botao_bresenham')

        # Circulo
        self.elementos_circulo['label_centro'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y), (60, 20)),
            text='Centro:', manager=self.ui_manager)
        self.elementos_circulo['centro_x'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 70, base_y), (55, 30)),
            manager=self.ui_manager, object_id='#centro_x')
        self.elementos_circulo['centro_y'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 135, base_y), (55, 30)),
            manager=self.ui_manager, object_id='#centro_y')
        self.elementos_circulo['label_raio'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 40), (60, 20)),
            text='Raio:', manager=self.ui_manager)
        self.elementos_circulo['raio'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 70, base_y + 40), (120, 30)),
            manager=self.ui_manager, object_id='#raio')
        self.elementos_circulo['centro_x'].set_text('40')
        self.elementos_circulo['centro_y'].set_text('30')
        self.elementos_circulo['raio'].set_text('20')
        self.elementos_circulo['botao'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 80), (180, 40)),
            text='Desenhar Círculo', manager=self.ui_manager, object_id='#botao_circulo')

        # Bezier
        pontos_bezier = ['P0','P1','P2','P3']
        coords_ini = [('10','60'),('25','10'),('55','90'),('70','50')]
        for i,(p,coords) in enumerate(zip(pontos_bezier,coords_ini)):
            y_off = base_y + i*40
            self.elementos_bezier[f'label_{p.lower()}'] = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((self.largura_canvas + 10, y_off), (30,20)),
                text=f'{p}:', manager=self.ui_manager)
            self.elementos_bezier[f'{p.lower()}_x'] = pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect((self.largura_canvas + 40, y_off), (70,30)), manager=self.ui_manager)
            self.elementos_bezier[f'{p.lower()}_y'] = pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect((self.largura_canvas + 120, y_off), (70,30)), manager=self.ui_manager)
            self.elementos_bezier[f'{p.lower()}_x'].set_text(coords[0])
            self.elementos_bezier[f'{p.lower()}_y'].set_text(coords[1])
        self.elementos_bezier['botao'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 170), (180, 40)),
            text='Desenhar Curva', manager=self.ui_manager, object_id='#botao_bezier')

        # Elipse
        self.elementos_elipse['label_centro'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y), (180, 20)),
            text='Centro (x, y):', manager=self.ui_manager)
        self.elementos_elipse['centro_x'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 25), (80,30)), manager=self.ui_manager)
        self.elementos_elipse['centro_y'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 95, base_y + 25), (80,30)), manager=self.ui_manager)
        self.elementos_elipse['label_rx'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 60), (180, 20)),
            text='Raios (rx, ry):', manager=self.ui_manager)
        self.elementos_elipse['rx'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 85), (80,30)), manager=self.ui_manager)
        self.elementos_elipse['ry'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 95, base_y + 85), (80,30)), manager=self.ui_manager)
        self.elementos_elipse['centro_x'].set_text('40')
        self.elementos_elipse['centro_y'].set_text('40')
        self.elementos_elipse['rx'].set_text('30')
        self.elementos_elipse['ry'].set_text('20')
        self.elementos_elipse['botao'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 125), (180, 40)),
            text='Desenhar Elipse', manager=self.ui_manager, object_id='#botao_elipse')

        # Ações gerais
        self.botao_desfazer = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 10, self.altura_total - 90), (180, 35)),
            text='Desfazer', manager=self.ui_manager, object_id='#botao_desfazer')
        self.botao_limpar = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 10, self.altura_total - 50), (180, 35)),
            text='Limpar Tela', manager=self.ui_manager, object_id='#botao_limpar')

    # ---------------- Visibilidade -----------------
    def mostrar_elementos_figura(self, figura):
        for grupo in [self.elementos_linha, self.elementos_circulo, self.elementos_bezier, self.elementos_elipse]:
            for comp in grupo.values():
                comp.hide()
        mapping = {
            'Linha (Bresenham)': self.elementos_linha,
            'Círculo': self.elementos_circulo,
            'Curva de Bézier': self.elementos_bezier,
            'Elipse': self.elementos_elipse
        }.get(figura, {})
        for comp in mapping.values():
            comp.show()

    # ---------------- Histórico -----------------
    def atualizar_historico(self, historico):
        # cache simples
        assinatura = f"{len(historico)}:" + '|'.join(d.timestamp.isoformat() for d in historico)
        if assinatura == self._historico_cache_str:
            return
        self._historico_cache_str = assinatura

        # limpar antigo
        for item in self._historico_itens:
            for w in item.get('widgets', []):
                w.kill()
        self._historico_itens.clear()

        viewport_w = self.historico_container.relative_rect.width
        linha_h = 24
        padding_block = 6
        botao_w = 20
        gap = 2
        text_x = botao_w + gap  # texto logo após botão
        text_w = viewport_w - text_x
        y = 0

        if not historico:
            vazio = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((0, y), (viewport_w, linha_h)),
                text='(nenhum desenho)', manager=self.ui_manager, container=self.historico_container
            )
            self._historico_itens.append({'widgets': [vazio]})
            self.historico_container.set_scrollable_area_dimensions((viewport_w, linha_h + 4))
            return

        for idx_visual, desenho in enumerate(reversed(historico)):
            indice_real = len(historico) - 1 - idx_visual
            widgets = []
            botao = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((0, y), (botao_w, linha_h)),
                text='X', manager=self.ui_manager, container=self.historico_container,
                object_id=f'#hist_x_{idx_visual}'
            )
            botao.indice_historico_real = indice_real
            titulo = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((text_x, y), (text_w, linha_h)),
                text=f"{idx_visual+1}. {desenho.tipo}", manager=self.ui_manager, container=self.historico_container
            )
            widgets.extend([botao, titulo])
            y += linha_h

            if desenho.tipo == 'Linha (Bresenham)':
                p1 = desenho.parametros.get('p1'); p2 = desenho.parametros.get('p2')
                linhas = [f"P1: {p1}", f"P2: {p2}"]
            elif desenho.tipo == 'Círculo':
                c = desenho.parametros.get('centro'); r = desenho.parametros.get('raio')
                linhas = [f"Centro: {c}", f"Raio: {r}"]
            elif desenho.tipo == 'Curva de Bézier':
                linhas = [f"P{i}: {desenho.parametros.get(f'p{i}')}" for i in range(4)]
            elif desenho.tipo == 'Elipse':
                c = desenho.parametros.get('centro'); rx = desenho.parametros.get('rx'); ry = desenho.parametros.get('ry')
                linhas = [f"Centro: {c}", f"RX: {rx}", f"RY: {ry}"]
            else:
                linhas = []

            for linha in linhas:
                lbl = pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect((text_x, y), (text_w, linha_h)),
                    text=linha, manager=self.ui_manager, container=self.historico_container
                )
                widgets.append(lbl)
                y += linha_h

            hora_lbl = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((text_x, y), (text_w, linha_h)),
                text=f"Hora: {desenho.timestamp.strftime('%H:%M:%S')}", manager=self.ui_manager, container=self.historico_container
            )
            widgets.append(hora_lbl)
            y += linha_h + padding_block
            self._historico_itens.append({'widgets': widgets, 'indice': indice_real})

        altura_total = max(y, self.altura_historico - 30)
        self.historico_container.set_scrollable_area_dimensions((viewport_w, altura_total))