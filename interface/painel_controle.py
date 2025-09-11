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
        self.elementos_polilinha = {}
        self.elementos_triangulo = {}
        self.elementos_quadrilatero = {}
        self.elementos_pentagono = {}
        self.elementos_hexagono = {}
        self.elementos_transformacao = {}
        self.elementos_recorte = {}
        self.elementos_projecao = {}

        # Cache do histórico
        self._historico_cache_str = None

        # Estado do triângulo regular
        self.triangulo_sentido_horario = False

        # Monta a interface e mostra os elementos padrão
        self.construir_interface()
        self.mostrar_elementos_figura('Linha (Bresenham)')

    def construir_interface(self):
        # Histórico (painel à direita)
        margem_direita = 10
        self.largura_historico = 200
        self.altura_historico = 260
        self.posicao_x_historico = self.largura_canvas + self.largura_painel - self.largura_historico - margem_direita

        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.posicao_x_historico, 10), (self.largura_historico, 20)),
            text='Histórico de Desenhos',
            manager=self.ui_manager
        )
        self.lista_historico = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect((self.posicao_x_historico, 40), (self.largura_historico, self.altura_historico - 50)),
            item_list=[],
            manager=self.ui_manager,
            object_id='#lista_historico'
        )
        self.botao_excluir_selecao = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.posicao_x_historico, self.altura_historico), (self.largura_historico, 30)),
            text='Excluir Seleção',
            manager=self.ui_manager,
            object_id='#botao_excluir_selecao'
        )

        # Recorte (abaixo do histórico)
        y_recorte = self.altura_historico + 40
        x_hist = self.posicao_x_historico
        # Título
        self.elementos_recorte['titulo'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((x_hist, y_recorte), (self.largura_historico, 20)),
            text='Recorte', manager=self.ui_manager
        )
        # Campos para recorte de Linha via margens (Cohen–Sutherland) — ficam logo abaixo do título
        y_line = y_recorte + 25
        linha_alt = 35
        self.elementos_recorte['label_left'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((x_hist, y_line), (90, 20)), text='left:', manager=self.ui_manager)
        self.elementos_recorte['left'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((x_hist + 95, y_line), (60, 30)), manager=self.ui_manager)
        self.elementos_recorte['btn_left'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((x_hist + 160, y_line), (40, 30)), text='Def', manager=self.ui_manager, object_id='#recorte_set_left')
        y_line += linha_alt
        self.elementos_recorte['label_bottom'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((x_hist, y_line), (90, 20)), text='bottom:', manager=self.ui_manager)
        self.elementos_recorte['bottom'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((x_hist + 95, y_line), (60, 30)), manager=self.ui_manager)
        self.elementos_recorte['btn_bottom'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((x_hist + 160, y_line), (40, 30)), text='Def', manager=self.ui_manager, object_id='#recorte_set_bottom')
        y_line += linha_alt
        self.elementos_recorte['label_right'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((x_hist, y_line), (90, 20)), text='right:', manager=self.ui_manager)
        self.elementos_recorte['right'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((x_hist + 95, y_line), (60, 30)), manager=self.ui_manager)
        self.elementos_recorte['btn_right'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((x_hist + 160, y_line), (40, 30)), text='Def', manager=self.ui_manager, object_id='#recorte_set_right')
        y_line += linha_alt
        self.elementos_recorte['label_top'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((x_hist, y_line), (90, 20)), text='top:', manager=self.ui_manager)
        self.elementos_recorte['top'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((x_hist + 95, y_line), (60, 30)), manager=self.ui_manager)
        self.elementos_recorte['btn_top'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((x_hist + 160, y_line), (40, 30)), text='Def', manager=self.ui_manager, object_id='#recorte_set_top')
        y_line += 40
        botao_recorte_linha = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((x_hist, y_line), (self.largura_historico, 30)),
            text='Aplicar Recorte', manager=self.ui_manager, object_id='#botao_recorte'
        )

        # Botões e entrada para janela poligonal (Sutherland–Hodgman), ancorados sob o título
        self._construir_recorte_poligonal(x_hist, y_recorte)
        # Registrar botão com duas chaves para compatibilidade
        self.elementos_recorte['botao'] = botao_recorte_linha
        self.elementos_recorte['btn_recorte'] = botao_recorte_linha
        # Defaults e esconder por padrão
        defaults_rec = {
            'left': '-20', 'bottom': '-20', 'right': '20', 'top': '20'
        }
        for k, v in defaults_rec.items():
            self.elementos_recorte[k].set_text(v)
        # Interface antiga de polígono removida em favor das margens/polígono unificados
        for comp in self.elementos_recorte.values():
            comp.hide()

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
            options_list=['Linha (Bresenham)', 'Círculo', 'Curva de Bézier', 'Elipse', 'Polilinha'],
            starting_option='Linha (Bresenham)',
            relative_rect=pygame.Rect((self.largura_canvas + 10, 210), (180, 30)),
            manager=self.ui_manager
        )

        base_y = 260
        # --- Linha ---
        self.elementos_linha['label_p1'] = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((self.largura_canvas + 10, base_y), (30, 20)), text='P1:', manager=self.ui_manager)
        self.elementos_linha['p1_x'] = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 40, base_y), (50, 30)), manager=self.ui_manager)
        self.elementos_linha['p1_y'] = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 95, base_y), (50, 30)), manager=self.ui_manager)
        self.elementos_linha['btn_p1'] = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.largura_canvas + 150, base_y), (40, 30)), text='Def', manager=self.ui_manager, object_id='#linha_set_p1')

        self.elementos_linha['label_p2'] = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 40), (30, 20)), text='P2:', manager=self.ui_manager)
        self.elementos_linha['p2_x'] = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 40, base_y + 40), (50, 30)), manager=self.ui_manager)
        self.elementos_linha['p2_y'] = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 95, base_y + 40), (50, 30)), manager=self.ui_manager)
        self.elementos_linha['btn_p2'] = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.largura_canvas + 150, base_y + 40), (40, 30)), text='Def', manager=self.ui_manager, object_id='#linha_set_p2')

        for k, v in [('p1_x', '-30'), ('p1_y', '-30'), ('p2_x', '30'), ('p2_y', '30')]:
            self.elementos_linha[k].set_text(v)
        self.elementos_linha['botao'] = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 80), (180, 40)), text='Desenhar Linha', manager=self.ui_manager, object_id='#botao_bresenham')

        # --- Círculo ---
        self.elementos_circulo['label_centro'] = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((self.largura_canvas + 10, base_y), (60, 20)), text='Centro:', manager=self.ui_manager)
        self.elementos_circulo['centro_x'] = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 70, base_y), (50, 30)), manager=self.ui_manager)
        self.elementos_circulo['centro_y'] = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 125, base_y), (50, 30)), manager=self.ui_manager)
        self.elementos_circulo['btn_centro'] = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.largura_canvas + 180, base_y), (40, 30)), text='Def', manager=self.ui_manager, object_id='#circulo_set_centro')

        self.elementos_circulo['label_raio'] = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 40), (60, 20)), text='Raio:', manager=self.ui_manager)
        self.elementos_circulo['raio'] = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 70, base_y + 40), (150, 30)), manager=self.ui_manager)
        for k, v in [('centro_x', '0'), ('centro_y', '0'), ('raio', '25')]:
            self.elementos_circulo[k].set_text(v)
        self.elementos_circulo['botao'] = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 80), (210, 40)), text='Desenhar Círculo', manager=self.ui_manager, object_id='#botao_circulo')

        # --- Curva de Bézier ---
        pontos_bezier = ['P0', 'P1', 'P2', 'P3']
        coords_ini = [('-30', '-10'), ('-10', '30'), ('10', '-30'), ('30', '10')]
        for i, (p, coords) in enumerate(zip(pontos_bezier, coords_ini)):
            y_off = base_y + i * 40
            self.elementos_bezier[f'label_{p.lower()}'] = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((self.largura_canvas + 10, y_off), (30, 20)), text=f'{p}:', manager=self.ui_manager)
            self.elementos_bezier[f'{p.lower()}_x'] = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 40, y_off), (50, 30)), manager=self.ui_manager)
            self.elementos_bezier[f'{p.lower()}_y'] = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 95, y_off), (50, 30)), manager=self.ui_manager)
            self.elementos_bezier[f'btn_{p.lower()}'] = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.largura_canvas + 150, y_off), (40, 30)), text='Def', manager=self.ui_manager, object_id=f'#bezier_set_{p.lower()}')
            self.elementos_bezier[f'{p.lower()}_x'].set_text(coords[0])
            self.elementos_bezier[f'{p.lower()}_y'].set_text(coords[1])
        self.elementos_bezier['botao'] = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 170), (180, 40)), text='Desenhar Curva', manager=self.ui_manager, object_id='#botao_bezier')

        # --- Elipse ---
        self.elementos_elipse['label_centro'] = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((self.largura_canvas + 10, base_y), (60, 20)), text='Centro:', manager=self.ui_manager)
        self.elementos_elipse['centro_x'] = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 70, base_y), (50, 30)), manager=self.ui_manager)
        self.elementos_elipse['centro_y'] = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 125, base_y), (50, 30)), manager=self.ui_manager)
        self.elementos_elipse['btn_centro'] = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.largura_canvas + 180, base_y), (40, 30)), text='Def', manager=self.ui_manager, object_id='#elipse_set_centro')

        self.elementos_elipse['label_raios'] = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 40), (60, 20)), text='Raios:', manager=self.ui_manager)
        self.elementos_elipse['rx'] = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 70, base_y + 40), (70, 30)), manager=self.ui_manager)
        self.elementos_elipse['ry'] = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 145, base_y + 40), (75, 30)), manager=self.ui_manager)
        for k, v in [('centro_x', '0'), ('centro_y', '0'), ('rx', '30'), ('ry', '20')]:
            self.elementos_elipse[k].set_text(v)
        self.elementos_elipse['botao'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 80), (210, 40)),
            text='Desenhar Elipse', manager=self.ui_manager, object_id='#botao_elipse'
        )

        # --- Triângulo (por 3 pontos) ---
        self.elementos_triangulo['label_p1'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y), (30, 20)), text='P1:', manager=self.ui_manager)
        self.elementos_triangulo['p1_x'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 40, base_y), (50, 30)), manager=self.ui_manager)
        self.elementos_triangulo['p1_y'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 95, base_y), (50, 30)), manager=self.ui_manager)
        self.elementos_triangulo['btn_p1'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 150, base_y), (40, 30)), text='Def', manager=self.ui_manager, object_id='#tri_set_p1')

        self.elementos_triangulo['label_p2'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 40), (30, 20)), text='P2:', manager=self.ui_manager)
        self.elementos_triangulo['p2_x'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 40, base_y + 40), (50, 30)), manager=self.ui_manager)
        self.elementos_triangulo['p2_y'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 95, base_y + 40), (50, 30)), manager=self.ui_manager)
        self.elementos_triangulo['btn_p2'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 150, base_y + 40), (40, 30)), text='Def', manager=self.ui_manager, object_id='#tri_set_p2')

        self.elementos_triangulo['label_p3'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 80), (30, 20)), text='P3:', manager=self.ui_manager)
        self.elementos_triangulo['p3_x'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 40, base_y + 80), (50, 30)), manager=self.ui_manager)
        self.elementos_triangulo['p3_y'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 95, base_y + 80), (50, 30)), manager=self.ui_manager)
        self.elementos_triangulo['btn_p3'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 150, base_y + 80), (40, 30)), text='Def', manager=self.ui_manager, object_id='#tri_set_p3')

        # Botão para desenhar (fecha automaticamente p3->p1)
        self.elementos_triangulo['botao'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 120), (180, 40)),
            text='Desenhar Triângulo', manager=self.ui_manager, object_id='#botao_triangulo')

        # Defaults
        for k, v in [('p1_x', '-20'), ('p1_y', '-10'), ('p2_x', '20'), ('p2_y', '-10'), ('p3_x', '0'), ('p3_y', '20')]:
            self.elementos_triangulo[k].set_text(v)

    # --- Polilinha ---
        self.elementos_polilinha['label'] = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((self.largura_canvas + 10, base_y), (220, 20)), text='Pontos (x1,y1; x2,y2; ...):', manager=self.ui_manager)
        self.elementos_polilinha['entrada_pontos'] = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 30), (210, 30)), manager=self.ui_manager)
        self.elementos_polilinha['entrada_pontos'].set_text('-10,-10; 0,20; 10,-10; 20,20')
        self.elementos_polilinha['botao'] = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 70), (210, 40)), text='Desenhar Polilinha', manager=self.ui_manager, object_id='#botao_polilinha')
        # Botões para desenhar por clique
        self.elementos_polilinha['btn_iniciar_clique'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 115), (100, 28)),
            text='Iniciar clique', manager=self.ui_manager, object_id='#polilinha_iniciar_clique')
        self.elementos_polilinha['btn_finalizar_clique'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 120, base_y + 115), (100, 28)),
            text='Finalizar', manager=self.ui_manager, object_id='#polilinha_finalizar_clique')

        # Botão para ligar ao primeiro vértice (fechar polilinha)
        self.elementos_polilinha['btn_ligar_primeiro'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 150), (210, 28)),
            text='Ligar ao primeiro', manager=self.ui_manager, object_id='#polilinha_ligar_primeiro')

    # (Removido) Recorte duplicado no bloco principal — substituído pelo painel de margens acima

    # --- Quadrilátero (por 4 pontos) ---
        self.elementos_quadrilatero['label_p1'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y), (30, 20)), text='P1:', manager=self.ui_manager)
        self.elementos_quadrilatero['p1_x'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 40, base_y), (50, 30)), manager=self.ui_manager)
        self.elementos_quadrilatero['p1_y'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 95, base_y), (50, 30)), manager=self.ui_manager)
        self.elementos_quadrilatero['btn_p1'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 150, base_y), (40, 30)), text='Def', manager=self.ui_manager, object_id='#quad_set_p1')

        self.elementos_quadrilatero['label_p2'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 40), (30, 20)), text='P2:', manager=self.ui_manager)
        self.elementos_quadrilatero['p2_x'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 40, base_y + 40), (50, 30)), manager=self.ui_manager)
        self.elementos_quadrilatero['p2_y'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 95, base_y + 40), (50, 30)), manager=self.ui_manager)
        self.elementos_quadrilatero['btn_p2'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 150, base_y + 40), (40, 30)), text='Def', manager=self.ui_manager, object_id='#quad_set_p2')

        self.elementos_quadrilatero['label_p3'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 80), (30, 20)), text='P3:', manager=self.ui_manager)
        self.elementos_quadrilatero['p3_x'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 40, base_y + 80), (50, 30)), manager=self.ui_manager)
        self.elementos_quadrilatero['p3_y'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 95, base_y + 80), (50, 30)), manager=self.ui_manager)
        self.elementos_quadrilatero['btn_p3'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 150, base_y + 80), (40, 30)), text='Def', manager=self.ui_manager, object_id='#quad_set_p3')

        self.elementos_quadrilatero['label_p4'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 120), (30, 20)), text='P4:', manager=self.ui_manager)
        self.elementos_quadrilatero['p4_x'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 40, base_y + 120), (50, 30)), manager=self.ui_manager)
        self.elementos_quadrilatero['p4_y'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 95, base_y + 120), (50, 30)), manager=self.ui_manager)
        self.elementos_quadrilatero['btn_p4'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 150, base_y + 120), (40, 30)), text='Def', manager=self.ui_manager, object_id='#quad_set_p4')

        self.elementos_quadrilatero['botao'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 160), (180, 40)),
            text='Desenhar Quadrilátero', manager=self.ui_manager, object_id='#botao_quadrilatero')

        for k, v in [('p1_x','-20'),('p1_y','-20'),('p2_x','20'),('p2_y','-20'),('p3_x','20'),('p3_y','20'),('p4_x','-20'),('p4_y','20')]:
            self.elementos_quadrilatero[k].set_text(v)

        # --- Pentágono (por 5 pontos) ---
        self.elementos_pentagono['label_p1'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y), (30, 20)), text='P1:', manager=self.ui_manager)
        self.elementos_pentagono['p1_x'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 40, base_y), (50, 30)), manager=self.ui_manager)
        self.elementos_pentagono['p1_y'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 95, base_y), (50, 30)), manager=self.ui_manager)
        self.elementos_pentagono['btn_p1'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 150, base_y), (40, 30)), text='Def', manager=self.ui_manager, object_id='#pent_set_p1')

        self.elementos_pentagono['label_p2'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 40), (30, 20)), text='P2:', manager=self.ui_manager)
        self.elementos_pentagono['p2_x'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 40, base_y + 40), (50, 30)), manager=self.ui_manager)
        self.elementos_pentagono['p2_y'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 95, base_y + 40), (50, 30)), manager=self.ui_manager)
        self.elementos_pentagono['btn_p2'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 150, base_y + 40), (40, 30)), text='Def', manager=self.ui_manager, object_id='#pent_set_p2')

        self.elementos_pentagono['label_p3'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 80), (30, 20)), text='P3:', manager=self.ui_manager)
        self.elementos_pentagono['p3_x'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 40, base_y + 80), (50, 30)), manager=self.ui_manager)
        self.elementos_pentagono['p3_y'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 95, base_y + 80), (50, 30)), manager=self.ui_manager)
        self.elementos_pentagono['btn_p3'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 150, base_y + 80), (40, 30)), text='Def', manager=self.ui_manager, object_id='#pent_set_p3')

        self.elementos_pentagono['label_p4'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 120), (30, 20)), text='P4:', manager=self.ui_manager)
        self.elementos_pentagono['p4_x'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 40, base_y + 120), (50, 30)), manager=self.ui_manager)
        self.elementos_pentagono['p4_y'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 95, base_y + 120), (50, 30)), manager=self.ui_manager)
        self.elementos_pentagono['btn_p4'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 150, base_y + 120), (40, 30)), text='Def', manager=self.ui_manager, object_id='#pent_set_p4')

        self.elementos_pentagono['label_p5'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 160), (30, 20)), text='P5:', manager=self.ui_manager)
        self.elementos_pentagono['p5_x'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 40, base_y + 160), (50, 30)), manager=self.ui_manager)
        self.elementos_pentagono['p5_y'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 95, base_y + 160), (50, 30)), manager=self.ui_manager)
        self.elementos_pentagono['btn_p5'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 150, base_y + 160), (40, 30)), text='Def', manager=self.ui_manager, object_id='#pent_set_p5')

        self.elementos_pentagono['botao'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 200), (180, 40)),
            text='Desenhar Pentágono', manager=self.ui_manager, object_id='#botao_pentagono')

        for k, v in [
            ('p1_x','-20'),('p1_y','-10'),
            ('p2_x','0'),('p2_y','20'),
            ('p3_x','20'),('p3_y','-10'),
            ('p4_x','10'),('p4_y','-25'),
            ('p5_x','-10'),('p5_y','-25'),
        ]:
            self.elementos_pentagono[k].set_text(v)

        # --- Hexágono (por 6 pontos) ---
        hex_base = base_y - 40  # sobe um pouco para não colidir com as transformações
        self.elementos_hexagono['label_p1'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.largura_canvas + 10, hex_base), (30, 20)), text='P1:', manager=self.ui_manager)
        self.elementos_hexagono['p1_x'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 40, hex_base), (50, 30)), manager=self.ui_manager)
        self.elementos_hexagono['p1_y'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 95, hex_base), (50, 30)), manager=self.ui_manager)
        self.elementos_hexagono['btn_p1'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 150, hex_base), (40, 30)), text='Def', manager=self.ui_manager, object_id='#hex_set_p1')

        for i in range(2, 7):
            y_off = hex_base + (i - 1) * 40
            self.elementos_hexagono[f'label_p{i}'] = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((self.largura_canvas + 10, y_off), (30, 20)), text=f'P{i}:', manager=self.ui_manager)
            self.elementos_hexagono[f'p{i}_x'] = pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect((self.largura_canvas + 40, y_off), (50, 30)), manager=self.ui_manager)
            self.elementos_hexagono[f'p{i}_y'] = pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect((self.largura_canvas + 95, y_off), (50, 30)), manager=self.ui_manager)
            self.elementos_hexagono[f'btn_p{i}'] = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((self.largura_canvas + 150, y_off), (40, 30)), text='Def', manager=self.ui_manager, object_id=f'#hex_set_p{i}')

        self.elementos_hexagono['botao'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 10, hex_base + 240), (180, 40)),
            text='Desenhar Hexágono', manager=self.ui_manager, object_id='#botao_hexagono')

        # Defaults para formar um hexágono aproximado
        defaults_hex = {
            'p1_x': '-20', 'p1_y': '0',
            'p2_x': '-10', 'p2_y': '17',
            'p3_x': '10',  'p3_y': '17',
            'p4_x': '20',  'p4_y': '0',
            'p5_x': '10',  'p5_y': '-17',
            'p6_x': '-10', 'p6_y': '-17',
        }
        for k, v in defaults_hex.items():
            self.elementos_hexagono[k].set_text(v)

        # --- Polilinha: Predefinidas (abaixo dos controles de polilinha), ajustadas para não invadir transformações ---
        # Área atual de polilinha vai até base_y + 178; transformações começam em 500.
        # Vamos usar 438..500 (62px) com componentes compactos (18/22/22 px).
        predef_y = base_y + 178  # 260 + 178 = 438
        self.elementos_polilinha['label_predef'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.largura_canvas + 10, predef_y), (220, 18)),
            text='Polilinha Predefinida:', manager=self.ui_manager
        )
        self.elementos_polilinha['dropdown_predef'] = pygame_gui.elements.UIDropDownMenu(
            options_list=['Triângulo', 'Quadrilátero', 'Pentágono', 'Hexágono'],
            starting_option='Triângulo',
            relative_rect=pygame.Rect((self.largura_canvas + 10, predef_y + 18), (210, 22)),
            manager=self.ui_manager
        )
        self.elementos_polilinha['btn_usar_predef'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 10, predef_y + 40), (210, 22)),
            text='Usar predefinida', manager=self.ui_manager, object_id='#polilinha_usar_predef'
        )

        # --- Transformações 2D ---
        base_y_transf = 500
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y_transf), (380, 20)),
            text='--- Transformações 2D (no selecionado) ---',
            manager=self.ui_manager
        )

        # Translação
        y_offset = base_y_transf + 30
        self.elementos_transformacao['label_trans'] = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((self.largura_canvas + 10, y_offset), (140, 20)), text='Translação (dx, dy):', manager=self.ui_manager)
        self.elementos_transformacao['trans_x'] = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 150, y_offset), (50, 30)), manager=self.ui_manager)
        self.elementos_transformacao['trans_y'] = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 205, y_offset), (50, 30)), manager=self.ui_manager)
        self.elementos_transformacao['btn_trans'] = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.largura_canvas + 260, y_offset), (60, 30)), text='Aplicar', manager=self.ui_manager, object_id='#trans_aplicar')
        self.elementos_transformacao['trans_x'].set_text('10')
        self.elementos_transformacao['trans_y'].set_text('5')

        # Escala
        y_offset = base_y_transf + 70
        self.elementos_transformacao['label_escala'] = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((self.largura_canvas + 10, y_offset), (140, 20)), text='Escala (sx, sy):', manager=self.ui_manager)
        self.elementos_transformacao['escala_sx'] = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 150, y_offset), (50, 30)), manager=self.ui_manager)
        self.elementos_transformacao['escala_sy'] = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 205, y_offset), (50, 30)), manager=self.ui_manager)
        self.elementos_transformacao['label_ponto_fixo'] = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((self.largura_canvas + 10, y_offset + 30), (140, 20)), text='Ponto Fixo (cx, cy):', manager=self.ui_manager)
        self.elementos_transformacao['escala_cx'] = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 150, y_offset + 30), (50, 30)), manager=self.ui_manager)
        self.elementos_transformacao['escala_cy'] = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 205, y_offset + 30), (50, 30)), manager=self.ui_manager)
        self.elementos_transformacao['btn_escala'] = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.largura_canvas + 260, y_offset), (60, 60)), text='Aplicar', manager=self.ui_manager, object_id='#escala_aplicar')
        self.elementos_transformacao['escala_sx'].set_text('1.5')
        self.elementos_transformacao['escala_sy'].set_text('1.5')
        self.elementos_transformacao['escala_cx'].set_text('0')
        self.elementos_transformacao['escala_cy'].set_text('0')

        # Rotação
        y_offset = base_y_transf + 140
        self.elementos_transformacao['label_rot'] = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((self.largura_canvas + 10, y_offset), (140, 20)), text='Rotação (ângulo):', manager=self.ui_manager)
        self.elementos_transformacao['rot_angulo'] = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 150, y_offset), (105, 30)), manager=self.ui_manager)
        self.elementos_transformacao['label_pivo'] = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((self.largura_canvas + 10, y_offset + 30), (140, 20)), text='Pivô (px, py):', manager=self.ui_manager)
        self.elementos_transformacao['rot_px'] = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 150, y_offset + 30), (50, 30)), manager=self.ui_manager)
        self.elementos_transformacao['rot_py'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 205, y_offset + 30), (50, 30)),
            manager=self.ui_manager
        )
        self.elementos_transformacao['btn_rot'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 260, y_offset), (60, 60)),
            text='Aplicar', manager=self.ui_manager, object_id='#rot_aplicar'
        )
        self.elementos_transformacao['rot_angulo'].set_text('45')
        self.elementos_transformacao['rot_px'].set_text('0')
        self.elementos_transformacao['rot_py'].set_text('0')

        

        # Ações, Preenchimento e Módulo 3D
        y_acoes_base = self.altura_total - 130 # Posição inicial para o bloco inferior
        
        # Ações Gerais
        self.botao_desfazer = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 10, y_acoes_base), (180, 35)),
            text='Desfazer', manager=self.ui_manager, object_id='#botao_desfazer')
        self.botao_limpar = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 10, y_acoes_base + 40), (180, 35)),
            text='Limpar Tela', manager=self.ui_manager, object_id='#botao_limpar')

        # Preenchimento (alinhado com os botões de Ações)
        gap = 10
        label_x = self.largura_canvas + 10 + 180 + gap
        self.elementos_transformacao['label_preench'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((label_x, y_acoes_base), (180, 20)),
            text='Preenchimento:', manager=self.ui_manager
        )
        btn_w, btn_h = 95, 35
        scan_x = label_x
        flood_x = scan_x + btn_w + gap
        self.elementos_transformacao['btn_preencher_scan'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((scan_x, y_acoes_base + 30), (btn_w, btn_h)),
            text='Scanline', manager=self.ui_manager, object_id='#preencher_scanline'
        )
        self.elementos_transformacao['btn_preencher_rec'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((flood_x, y_acoes_base + 30), (btn_w, btn_h)),
            text='Flood Fill', manager=self.ui_manager, object_id='#preencher_recursao'
        )

        # Módulo 3D
        self.botao_projecoes = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 10, y_acoes_base + 80), (180, 35)),
            text='Projeções 3D',
            manager=self.ui_manager,
            object_id='#botao_projecoes'
        )

    def _construir_recorte_poligonal(self, x_hist: int, y_recorte: int) -> None:
        """Cria os controles de janela poligonal (convexa) para Sutherland–Hodgman,
        ancorados imediatamente abaixo do título de Recorte.
        """
        y = y_recorte + 25
        self.elementos_recorte['label_clip_poly'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((x_hist, y), (self.largura_historico, 20)),
            text='Janela por clique (convexa):', manager=self.ui_manager
        )
        y += 25
        btn_w, btn_h, gap = 90, 28, 10
        start_x = x_hist + 5
        self.elementos_recorte['btn_clip_iniciar'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((start_x, y), (btn_w, btn_h)), text='Iniciar', manager=self.ui_manager, object_id='#clip_poly_iniciar')
        self.elementos_recorte['btn_clip_finalizar'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((start_x + btn_w + gap, y), (btn_w, btn_h)), text='Finalizar', manager=self.ui_manager, object_id='#clip_poly_finalizar')
        y += btn_h + 8
        self.elementos_recorte['label_clip_pontos'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((x_hist, y), (self.largura_historico, 20)), text='Pontos (x1,y1; ...):', manager=self.ui_manager)
        y += 22
        self.elementos_recorte['entrada_clip_pontos'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((x_hist, y), (self.largura_historico, 30)), manager=self.ui_manager)
        self.elementos_recorte['entrada_clip_pontos'].set_text('-20,-20; 20,-20; 20,20; -20,20')

    def mostrar_elementos_figura(self, figura):
        for grupo in [self.elementos_linha, self.elementos_circulo, self.elementos_bezier, self.elementos_elipse, self.elementos_polilinha, self.elementos_triangulo, self.elementos_quadrilatero, self.elementos_pentagono, self.elementos_hexagono]:
            for comp in grupo.values():
                comp.hide()
        mapping = {
            'Linha (Bresenham)': self.elementos_linha,
            'Círculo': self.elementos_circulo,
            'Curva de Bézier': self.elementos_bezier,
            'Elipse': self.elementos_elipse,
            'Polilinha': self.elementos_polilinha
        }.get(figura, {})
        for comp in mapping.values():
            comp.show()

    def atualizar_historico(self, historico, indice_selecionado):
        assinatura_desenhos = '|'.join(str(d.timestamp) for d in historico)
        assinatura_completa = f"{len(historico)}:{indice_selecionado}:{assinatura_desenhos}"

        if self._historico_cache_str == assinatura_completa:
            return
        self._historico_cache_str = assinatura_completa

        lista_para_ui = []
        show_recorte_linha = False
        show_recorte_poligono = False
        if indice_selecionado is not None and 0 <= indice_selecionado < len(historico):
            desenho_selecionado = historico[indice_selecionado]
            if desenho_selecionado.tipo == 'Linha (Bresenham)':
                show_recorte_linha = True
            elif desenho_selecionado.tipo == 'Polilinha':
                show_recorte_poligono = True

        # Atualiza o título com o algoritmo correspondente
        if 'titulo' in self.elementos_recorte:
            if show_recorte_linha:
                self.elementos_recorte['titulo'].set_text('Recorte: Cohen-Sutherland')
            elif show_recorte_poligono:
                self.elementos_recorte['titulo'].set_text('Recorte: Sutherland-Hodgman')
            else:
                self.elementos_recorte['titulo'].set_text('Recorte')

        for i, desenho in enumerate(historico):
            prefixo = "* " if i == indice_selecionado else ""
            lista_para_ui.append(f"{prefixo}{i+1}. {desenho.tipo}")

        self.lista_historico.set_item_list(lista_para_ui)

        # Mostrar a interface de margens para linhas e a interface poligonal para polilinhas
        margin_keys = {
            'label_left','left','btn_left',
            'label_bottom','bottom','btn_bottom',
            'label_right','right','btn_right',
            'label_top','top','btn_top',
            'botao','btn_recorte'
        }

        polyclip_keys = {
            'label_clip_poly','btn_clip_iniciar','btn_clip_finalizar',
            'label_clip_pontos','entrada_clip_pontos'
        }

        for key, comp in self.elementos_recorte.items():
            if key == 'titulo':
                comp.show() if (show_recorte_linha or show_recorte_poligono) else comp.hide()
            elif key in margin_keys:
                comp.show() if show_recorte_linha else comp.hide()
            elif key in polyclip_keys:
                comp.show() if show_recorte_poligono else comp.hide()
            else:
                comp.hide()