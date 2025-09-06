import pygame
import pygame_gui

class PainelControle:
    def __init__(self, ui_manager, largura_painel, altura_total, largura_canvas):
        self.ui_manager = ui_manager
        self.largura_painel = largura_painel
        self.altura_total = altura_total
        self.largura_canvas = largura_canvas

        self.construir_interface()

    def construir_interface(self):
        """Cria os elementos da GUI no painel de controle."""
        # --- Seção de Resolução ---
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((self.largura_canvas + 10, 10), (180, 20)), text='Configuração da Grade', manager=self.ui_manager)
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((self.largura_canvas + 10, 40), (80, 20)), text='Largura:', manager=self.ui_manager)
        self.entrada_largura = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 90, 40), (100, 30)), manager=self.ui_manager, object_id='#largura_grid')
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((self.largura_canvas + 10, 80), (80, 20)), text='Altura:', manager=self.ui_manager)
        self.entrada_altura = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 90, 80), (100, 30)), manager=self.ui_manager, object_id='#altura_grid')
        self.entrada_largura.set_text('80')  # Valor inicial
        self.entrada_altura.set_text('80')   # Valor inicial
        self.botao_aplicar_res = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.largura_canvas + 10, 120), (180, 40)), text='Aplicar Resolução', manager=self.ui_manager, object_id='#botao_aplicar_res')

        # --- Seção para o Algoritmo de Bresenham ---
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((self.largura_canvas + 10, 180), (180, 20)), text='Bresenham (Linha)', manager=self.ui_manager)
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((self.largura_canvas + 10, 210), (30, 20)), text='P1:', manager=self.ui_manager)
        self.entrada_p1_x = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 40, 210), (70, 30)), manager=self.ui_manager, object_id='#p1_x')
        self.entrada_p1_y = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 120, 210), (70, 30)), manager=self.ui_manager, object_id='#p1_y')
        self.entrada_p1_x.set_text('10'); self.entrada_p1_y.set_text('5')
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((self.largura_canvas + 10, 250), (30, 20)), text='P2:', manager=self.ui_manager)
        self.entrada_p2_x = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 40, 250), (70, 30)), manager=self.ui_manager, object_id='#p2_x')
        self.entrada_p2_y = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 120, 250), (70, 30)), manager=self.ui_manager, object_id='#p2_y')
        self.entrada_p2_x.set_text('70'); self.entrada_p2_y.set_text('45')
        self.botao_bresenham = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.largura_canvas + 10, 290), (180, 40)), text='Desenhar Linha', manager=self.ui_manager, object_id='#botao_bresenham')

        # --- Seção para o Algoritmo de Círculo ---
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((self.largura_canvas + 10, 350), (180, 20)), text='Ponto Médio (Círculo)', manager=self.ui_manager)
        
        # Centro
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((self.largura_canvas + 10, 380), (60, 20)), text='Centro:', manager=self.ui_manager)
        self.entrada_centro_x = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 70, 380), (55, 30)), manager=self.ui_manager, object_id='#centro_x')
        self.entrada_centro_y = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 135, 380), (55, 30)), manager=self.ui_manager, object_id='#centro_y')
        self.entrada_centro_x.set_text('40') # Valor inicial
        self.entrada_centro_y.set_text('30') # Valor inicial

        # Raio
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((self.largura_canvas + 10, 420), (60, 20)), text='Raio:', manager=self.ui_manager)
        self.entrada_raio = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 70, 420), (120, 30)), manager=self.ui_manager, object_id='#raio')
        self.entrada_raio.set_text('20') # Valor inicial

        # Botão para desenhar
        self.botao_circulo = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.largura_canvas + 10, 460), (180, 40)), text='Desenhar Círculo', manager=self.ui_manager, object_id='#botao_circulo')
        
        # --- Seção para Curvas de Bézier ---
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((self.largura_canvas + 10, 520), (200, 20)), text='Curva de Bézier (Cúbica)', manager=self.ui_manager)
        # P0
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((self.largura_canvas + 10, 550), (30, 20)), text='P0:', manager=self.ui_manager)
        self.entrada_b_p0_x = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 40, 550), (70, 30)), manager=self.ui_manager)
        self.entrada_b_p0_y = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 120, 550), (70, 30)), manager=self.ui_manager)
        self.entrada_b_p0_x.set_text('10')
        self.entrada_b_p0_y.set_text('60')
        # P1
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((self.largura_canvas + 10, 590), (30, 20)), text='P1:', manager=self.ui_manager)
        self.entrada_b_p1_x = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 40, 590), (70, 30)), manager=self.ui_manager)
        self.entrada_b_p1_y = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 120, 590), (70, 30)), manager=self.ui_manager)
        self.entrada_b_p1_x.set_text('25')
        self.entrada_b_p1_y.set_text('10')
        # P2
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((self.largura_canvas + 10, 630), (30, 20)), text='P2:', manager=self.ui_manager)
        self.entrada_b_p2_x = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 40, 630), (70, 30)), manager=self.ui_manager)
        self.entrada_b_p2_y = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 120, 630), (70, 30)), manager=self.ui_manager)
        self.entrada_b_p2_x.set_text('55')
        self.entrada_b_p2_y.set_text('90')
        # P3
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((self.largura_canvas + 10, 670), (30, 20)), text='P3:', manager=self.ui_manager)
        self.entrada_b_p3_x = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 40, 670), (70, 30)), manager=self.ui_manager)
        self.entrada_b_p3_y = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((self.largura_canvas + 120, 670), (70, 30)), manager=self.ui_manager)
        self.entrada_b_p3_x.set_text('70')
        self.entrada_b_p3_y.set_text('50')
        self.botao_bezier = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.largura_canvas + 10, 710), (180, 40)), text='Desenhar Curva', manager=self.ui_manager, object_id='#botao_bezier')

        # --- Botão para limpar a tela (movido para o final) ---
        self.botao_limpar = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.largura_canvas + 10, 760), (180, 40)), text='Limpar Tela', manager=self.ui_manager, object_id='#botao_limpar')