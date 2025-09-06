import pygame
import pygame_gui

class PainelControle:
    def __init__(self, ui_manager, largura_painel, altura_total, largura_canvas):
        self.ui_manager = ui_manager
        self.largura_painel = largura_painel
        self.altura_total = altura_total
        self.largura_canvas = largura_canvas
        
        # Dicionários para armazenar elementos de cada tipo de figura
        self.elementos_linha = {}
        self.elementos_circulo = {}
        self.elementos_bezier = {}
        self.elementos_elipse = {}
        
        self.construir_interface()
        
    def mostrar_elementos_figura(self, figura_selecionada):
        """Mostra os elementos da figura selecionada e esconde os outros."""
        # Esconde todos os elementos primeiro
        for elementos in [self.elementos_linha, self.elementos_circulo, 
                         self.elementos_bezier, self.elementos_elipse]:
            for elemento in elementos.values():
                elemento.hide()
        
        # Mostra os elementos da figura selecionada
        elementos_mostrar = {
            'Linha (Bresenham)': self.elementos_linha,
            'Círculo': self.elementos_circulo,
            'Curva de Bézier': self.elementos_bezier,
            'Elipse': self.elementos_elipse
        }.get(figura_selecionada, {})
        
        for elemento in elementos_mostrar.values():
            elemento.show()

    def construir_interface(self):
        """Cria os elementos da GUI no painel de controle."""
        # --- Seção de Histórico (Canto superior direito) ---
        margem_direita = 10
        posicao_x = self.largura_canvas + self.largura_painel - 180 - margem_direita
        
        # Título do histórico
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((posicao_x, 10), (180, 20)),
            text='Histórico de Desenhos',
            manager=self.ui_manager
        )

        # Área de texto para o histórico
        self.historico_texto = pygame_gui.elements.UITextBox(
            html_text="Nenhum desenho realizado",
            relative_rect=pygame.Rect((posicao_x, 40), (180, 150)),
            manager=self.ui_manager
        )

        # --- Seção de Resolução (Canto superior esquerdo) ---
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
            manager=self.ui_manager,
            object_id='#largura_grid'
        )
        
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.largura_canvas + 10, 80), (80, 20)),
            text='Altura:',
            manager=self.ui_manager
        )
        
        self.entrada_altura = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 90, 80), (100, 30)),
            manager=self.ui_manager,
            object_id='#altura_grid'
        )
        
        self.entrada_largura.set_text('80')  # Valor inicial
        self.entrada_altura.set_text('80')   # Valor inicial
        
        self.botao_aplicar_res = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 10, 120), (180, 40)),
            text='Aplicar Resolução',
            manager=self.ui_manager,
            object_id='#botao_aplicar_res'
        )

        # --- Seção de Seleção de Figura ---
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

        # Base position for figure parameters
        base_y = 260  # Posição base para os parâmetros da figura selecionada
        
        # --- Elementos para Linha (Bresenham) ---
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
            
        self.elementos_linha['p1_x'].set_text('10')
        self.elementos_linha['p1_y'].set_text('5')
        self.elementos_linha['p2_x'].set_text('70')
        self.elementos_linha['p2_y'].set_text('45')
        
        self.elementos_linha['botao'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 80), (180, 40)),
            text='Desenhar Linha',
            manager=self.ui_manager,
            object_id='#botao_bresenham')

        # --- Elementos para Círculo ---
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
            text='Desenhar Círculo',
            manager=self.ui_manager,
            object_id='#botao_circulo')
        
        # --- Elementos para Curva de Bézier ---
        pontos_bezier = ['P0', 'P1', 'P2', 'P3']
        coords_iniciais = [('10', '60'), ('25', '10'), ('55', '90'), ('70', '50')]
        
        for i, (ponto, coords) in enumerate(zip(pontos_bezier, coords_iniciais)):
            y_offset = base_y + (i * 40)
            
            self.elementos_bezier[f'label_{ponto.lower()}'] = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((self.largura_canvas + 10, y_offset), (30, 20)),
                text=f'{ponto}:',
                manager=self.ui_manager
            )
            
            self.elementos_bezier[f'{ponto.lower()}_x'] = pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect((self.largura_canvas + 40, y_offset), (70, 30)),
                manager=self.ui_manager
            )
            
            self.elementos_bezier[f'{ponto.lower()}_y'] = pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect((self.largura_canvas + 120, y_offset), (70, 30)),
                manager=self.ui_manager
            )
            
            self.elementos_bezier[f'{ponto.lower()}_x'].set_text(coords[0])
            self.elementos_bezier[f'{ponto.lower()}_y'].set_text(coords[1])
        
        self.elementos_bezier['botao'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 170), (180, 40)),
            text='Desenhar Curva',
            manager=self.ui_manager,
            object_id='#botao_bezier')

        # --- Elementos para Elipse ---
        self.elementos_elipse['label_centro'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y), (60, 20)),
            text='Centro:', manager=self.ui_manager)
            
        self.elementos_elipse['centro_x'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 70, base_y), (55, 30)),
            manager=self.ui_manager)
            
        self.elementos_elipse['centro_y'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 135, base_y), (55, 30)),
            manager=self.ui_manager)
            
        self.elementos_elipse['label_rx'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 40), (35, 20)),
            text='RX:', manager=self.ui_manager)
            
        self.elementos_elipse['rx'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 45, base_y + 40), (60, 30)),
            manager=self.ui_manager)
            
        self.elementos_elipse['label_ry'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.largura_canvas + 115, base_y + 40), (35, 20)),
            text='RY:', manager=self.ui_manager)
            
        self.elementos_elipse['ry'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.largura_canvas + 150, base_y + 40), (60, 30)),
            manager=self.ui_manager)
            
        self.elementos_elipse['centro_x'].set_text('40')
        self.elementos_elipse['centro_y'].set_text('40')
        self.elementos_elipse['rx'].set_text('30')
        self.elementos_elipse['ry'].set_text('20')
        
        self.elementos_elipse['botao'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 10, base_y + 80), (180, 40)),
            text='Desenhar Elipse',
            manager=self.ui_manager,
            object_id='#botao_elipse')

        # Botão para desfazer último desenho
        self.botao_desfazer = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 10, self.altura_total - 90), (180, 35)),
            text='Desfazer',
            manager=self.ui_manager,
            object_id='#botao_desfazer'
        )

        # Botão para limpar a tela
        self.botao_limpar = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura_canvas + 10, self.altura_total - 50), (180, 35)),
            text='Limpar Tela',
            manager=self.ui_manager,
            object_id='#botao_limpar'
        )
            
        # Inicializa mostrando apenas os elementos da linha (opção padrão)
        self.mostrar_elementos_figura('Linha (Bresenham)')
        
    def atualizar_historico(self, historico):
        """Atualiza o texto do histórico com os desenhos realizados."""
        if not historico:
            self.historico_texto.html_text = "Nenhum desenho realizado"
            self.historico_texto.rebuild()
            return
        
        texto_historico = "<body>"
        for i, desenho in enumerate(historico, 1):
            texto_historico += f"<b>{i}. {desenho.tipo}</b><br>"
            # Formata os parâmetros de forma mais legível
            if desenho.tipo == "Linha (Bresenham)":
                p1 = desenho.parametros['p1']
                p2 = desenho.parametros['p2']
                texto_historico += f"P1: ({p1[0]}, {p1[1]})<br>"
                texto_historico += f"P2: ({p2[0]}, {p2[1]})<br>"
            elif desenho.tipo == "Círculo":
                centro = desenho.parametros['centro']
                raio = desenho.parametros['raio']
                texto_historico += f"Centro: ({centro[0]}, {centro[1]})<br>"
                texto_historico += f"Raio: {raio}<br>"
            elif desenho.tipo == "Curva de Bézier":
                for i, p in enumerate(['p0', 'p1', 'p2', 'p3']):
                    ponto = desenho.parametros[p]
                    texto_historico += f"P{i}: ({ponto[0]}, {ponto[1]})<br>"
            elif desenho.tipo == "Elipse":
                centro = desenho.parametros['centro']
                texto_historico += f"Centro: ({centro[0]}, {centro[1]})<br>"
                texto_historico += f"RX: {desenho.parametros['rx']}, RY: {desenho.parametros['ry']}<br>"
            
            texto_historico += f"<small>Hora: {desenho.timestamp.strftime('%H:%M:%S')}</small><br><br>"
        
        texto_historico += "</body>"
        self.historico_texto.html_text = texto_historico
        self.historico_texto.rebuild()