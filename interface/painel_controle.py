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
        self.elementos_transformacao = {}

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
            options_list=['Linha (Bresenham)', 'Círculo', 'Curva de Bézier', 'Elipse', 'Polilinha', 'Triângulo'],
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

        # Preenchimento (Scanline)
        y_offset = base_y_transf + 210
        self.elementos_transformacao['label_preench'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.largura_canvas + 10, y_offset), (180, 20)),
            text='Preenchimento (Scanline):', manager=self.ui_manager
        )
        self.elementos_transformacao['btn_preencher'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 200, y_offset - 5), (120, 30)),
            text='Preencher', manager=self.ui_manager, object_id='#preencher_scanline'
        )

        # Ações gerais
        self.botao_desfazer = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 10, self.altura_total - 90), (180, 35)),
            text='Desfazer', manager=self.ui_manager, object_id='#botao_desfazer')
        self.botao_limpar = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 10, self.altura_total - 50), (180, 35)),
            text='Limpar Tela', manager=self.ui_manager, object_id='#botao_limpar')

    def mostrar_elementos_figura(self, figura):
        for grupo in [self.elementos_linha, self.elementos_circulo, self.elementos_bezier, self.elementos_elipse, self.elementos_polilinha, self.elementos_triangulo]:
            for comp in grupo.values():
                comp.hide()
        mapping = {
            'Linha (Bresenham)': self.elementos_linha,
            'Círculo': self.elementos_circulo,
            'Curva de Bézier': self.elementos_bezier,
            'Elipse': self.elementos_elipse,
            'Polilinha': self.elementos_polilinha,
            'Triângulo': self.elementos_triangulo
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
        for i, desenho in enumerate(historico):
            prefixo = "* " if i == indice_selecionado else ""
            lista_para_ui.append(f"{prefixo}{i+1}. {desenho.tipo}")

        self.lista_historico.set_item_list(lista_para_ui)