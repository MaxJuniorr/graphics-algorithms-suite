# interface/app.py
import pygame
import pygame_gui
from algoritmos.bresenham import calcular_linha_bresenham
from algoritmos.circulo_elipse import calcular_circulo

# --- Constantes de Cores ---
COR_FUNDO = (20, 20, 20)
COR_GRADE = (40, 40, 40)
COR_PAINEL = (60, 60, 60)
COR_PIXEL = (255, 255, 255)

# --- Constantes de Layout ---
LARGURA_TOTAL = 800
ALTURA_TOTAL = 600
LARGURA_PAINEL = 200
LARGURA_CANVAS = LARGURA_TOTAL - LARGURA_PAINEL
ALTURA_CANVAS = ALTURA_TOTAL

class Aplicacao:
    def __init__(self, largura_grid_inicial, altura_grid_inicial):
        pygame.init()

        self.tela = pygame.display.set_mode((LARGURA_TOTAL, ALTURA_TOTAL))
        pygame.display.set_caption("Trabalho de Computação Gráfica")
        self.canvas_surface = pygame.Surface((LARGURA_CANVAS, ALTURA_CANVAS))
        self.ui_manager = pygame_gui.UIManager((LARGURA_TOTAL, ALTURA_TOTAL))
        
        self.pixels_a_desenhar = []
        
        self.construir_interface()
        
        self.rodando = True
        self.clock = pygame.time.Clock()
        
        self.largura_grid = 0
        self.altura_grid = 0
        self.tamanho_celula_x = 0
        self.tamanho_celula_y = 0
        self.atualizar_resolucao_grid(largura_grid_inicial, altura_grid_inicial)


    def construir_interface(self):
        """Cria os elementos da GUI no painel de controle."""
        # --- Seção de Resolução ---
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((LARGURA_CANVAS + 10, 10), (180, 20)), text='Configuração da Grade', manager=self.ui_manager)
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((LARGURA_CANVAS + 10, 40), (80, 20)), text='Largura:', manager=self.ui_manager)
        self.entrada_largura = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((LARGURA_CANVAS + 90, 40), (100, 30)), manager=self.ui_manager, object_id='#largura_grid')
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((LARGURA_CANVAS + 10, 80), (80, 20)), text='Altura:', manager=self.ui_manager)
        self.entrada_altura = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((LARGURA_CANVAS + 90, 80), (100, 30)), manager=self.ui_manager, object_id='#altura_grid')
        self.botao_aplicar_res = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((LARGURA_CANVAS + 10, 120), (180, 40)), text='Aplicar Resolução', manager=self.ui_manager, object_id='#botao_aplicar_res')

        # --- Seção para o Algoritmo de Bresenham ---
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((LARGURA_CANVAS + 10, 180), (180, 20)), text='Bresenham (Linha)', manager=self.ui_manager)
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((LARGURA_CANVAS + 10, 210), (30, 20)), text='P1:', manager=self.ui_manager)
        self.entrada_p1_x = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((LARGURA_CANVAS + 40, 210), (70, 30)), manager=self.ui_manager, object_id='#p1_x')
        self.entrada_p1_y = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((LARGURA_CANVAS + 120, 210), (70, 30)), manager=self.ui_manager, object_id='#p1_y')
        self.entrada_p1_x.set_text('10'); self.entrada_p1_y.set_text('5')
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((LARGURA_CANVAS + 10, 250), (30, 20)), text='P2:', manager=self.ui_manager)
        self.entrada_p2_x = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((LARGURA_CANVAS + 40, 250), (70, 30)), manager=self.ui_manager, object_id='#p2_x')
        self.entrada_p2_y = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((LARGURA_CANVAS + 120, 250), (70, 30)), manager=self.ui_manager, object_id='#p2_y')
        self.entrada_p2_x.set_text('70'); self.entrada_p2_y.set_text('45')
        self.botao_bresenham = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((LARGURA_CANVAS + 10, 290), (180, 40)), text='Desenhar Linha', manager=self.ui_manager, object_id='#botao_bresenham')

        # --- Seção para o Algoritmo de Círculo ---
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((LARGURA_CANVAS + 10, 350), (180, 20)), text='Ponto Médio (Círculo)', manager=self.ui_manager)
        
        # Centro
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((LARGURA_CANVAS + 10, 380), (60, 20)), text='Centro:', manager=self.ui_manager)
        self.entrada_centro_x = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((LARGURA_CANVAS + 70, 380), (55, 30)), manager=self.ui_manager, object_id='#centro_x')
        self.entrada_centro_y = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((LARGURA_CANVAS + 135, 380), (55, 30)), manager=self.ui_manager, object_id='#centro_y')
        self.entrada_centro_x.set_text('40') # Valor inicial
        self.entrada_centro_y.set_text('30') # Valor inicial

        # Raio
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((LARGURA_CANVAS + 10, 420), (60, 20)), text='Raio:', manager=self.ui_manager)
        self.entrada_raio = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((LARGURA_CANVAS + 70, 420), (120, 30)), manager=self.ui_manager, object_id='#raio')
        self.entrada_raio.set_text('20') # Valor inicial

        # Botão para desenhar
        self.botao_circulo = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((LARGURA_CANVAS + 10, 460), (180, 40)), text='Desenhar Círculo', manager=self.ui_manager, object_id='#botao_circulo')
        
        # --- Botão para limpar a tela (movido para o final) ---
        self.botao_limpar = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((LARGURA_CANVAS + 10, 520), (180, 40)), text='Limpar Tela', manager=self.ui_manager, object_id='#botao_limpar')

    def atualizar_resolucao_grid(self, nova_largura, nova_altura):
        print(f"Atualizando resolução para {nova_largura}x{nova_altura}")
        self.largura_grid = nova_largura
        self.altura_grid = nova_altura
        self.entrada_largura.set_text(str(self.largura_grid))
        self.entrada_altura.set_text(str(self.altura_grid))
        if self.largura_grid > 0: self.tamanho_celula_x = LARGURA_CANVAS / self.largura_grid
        if self.altura_grid > 0: self.tamanho_celula_y = ALTURA_CANVAS / self.altura_grid
        self.pixels_a_desenhar.clear()

    def desenhar_grade(self):
        for x in range(0, self.largura_grid + 1):
            pos_x = x * self.tamanho_celula_x
            pygame.draw.line(self.canvas_surface, COR_GRADE, (pos_x, 0), (pos_x, ALTURA_CANVAS))
        for y in range(0, self.altura_grid + 1):
            pos_y = y * self.tamanho_celula_y
            pygame.draw.line(self.canvas_surface, COR_GRADE, (0, pos_y), (LARGURA_CANVAS, pos_y))

    def desenhar_pixel(self, x_grid, y_grid, cor=COR_PIXEL):
        if self.tamanho_celula_x <= 0 or self.tamanho_celula_y <= 0: return
        # Verifica se o pixel está dentro dos limites da grade
        if not (0 <= x_grid < self.largura_grid and 0 <= y_grid < self.altura_grid):
            return # Não desenha pixels fora da área visível
        
        x_tela = x_grid * self.tamanho_celula_x
        y_tela = y_grid * self.tamanho_celula_y
        retangulo_pixel = pygame.Rect(x_tela, y_tela, self.tamanho_celula_x, self.tamanho_celula_y)
        pygame.draw.rect(self.canvas_surface, cor, retangulo_pixel)

    def executar(self):
        while self.rodando:
            delta_time = self.clock.tick(60) / 1000.0

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.rodando = False
                
                if evento.type == pygame_gui.UI_BUTTON_PRESSED:
                    # Botão Aplicar Resolução
                    if evento.ui_element == self.botao_aplicar_res:
                        try:
                            self.atualizar_resolucao_grid(int(self.entrada_largura.get_text()), int(self.entrada_altura.get_text()))
                        except ValueError:
                            print("Erro: A resolução deve ser um número inteiro.")
                    
                    # Botão Bresenham
                    elif evento.ui_element == self.botao_bresenham:
                        try:
                            p1 = (int(self.entrada_p1_x.get_text()), int(self.entrada_p1_y.get_text()))
                            p2 = (int(self.entrada_p2_x.get_text()), int(self.entrada_p2_y.get_text()))
                            self.pixels_a_desenhar.extend(calcular_linha_bresenham(p1, p2))
                        except ValueError:
                            print("Erro: As coordenadas da linha devem ser números inteiros.")

                    # Lógica do botão de desenhar Círculo
                    elif evento.ui_element == self.botao_circulo:
                        try:
                            centro = (int(self.entrada_centro_x.get_text()), int(self.entrada_centro_y.get_text()))
                            raio = int(self.entrada_raio.get_text())
                            self.pixels_a_desenhar.extend(calcular_circulo(centro, raio))
                        except ValueError:
                             print("Erro: As coordenadas do centro e o raio devem ser números inteiros.")
                            
                    # Botão Limpar
                    elif evento.ui_element == self.botao_limpar:
                        self.pixels_a_desenhar.clear()

                self.ui_manager.process_events(evento)
            
            self.ui_manager.update(delta_time)
            self.canvas_surface.fill(COR_FUNDO)
            self.desenhar_grade()
            if self.pixels_a_desenhar:
                for pixel in self.pixels_a_desenhar:
                    self.desenhar_pixel(pixel[0], pixel[1])
            self.tela.blit(self.canvas_surface, (0, 0))
            pygame.draw.rect(self.tela, COR_PAINEL, (LARGURA_CANVAS, 0, LARGURA_PAINEL, ALTURA_TOTAL))
            self.ui_manager.draw_ui(self.tela)
            pygame.display.flip()

        pygame.quit()