# interface/app.py
import pygame
import pygame_gui
# ### NOVO ### - Importa a nossa função do algoritmo
from algoritmos.bresenham import calcular_linha_bresenham

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
        
        # ### NOVO ### - Lista para guardar todos os pixels que devem ser desenhados
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

        # ### NOVO ### - Seção para o Algoritmo de Bresenham
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((LARGURA_CANVAS + 10, 180), (180, 20)), text='Algoritmo de Bresenham', manager=self.ui_manager)
        
        # Ponto 1
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((LARGURA_CANVAS + 10, 210), (30, 20)), text='P1:', manager=self.ui_manager)
        self.entrada_p1_x = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((LARGURA_CANVAS + 40, 210), (70, 30)), manager=self.ui_manager, object_id='#p1_x')
        self.entrada_p1_y = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((LARGURA_CANVAS + 120, 210), (70, 30)), manager=self.ui_manager, object_id='#p1_y')
        self.entrada_p1_x.set_text('10') # Valor inicial
        self.entrada_p1_y.set_text('5') # Valor inicial

        # Ponto 2
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((LARGURA_CANVAS + 10, 250), (30, 20)), text='P2:', manager=self.ui_manager)
        self.entrada_p2_x = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((LARGURA_CANVAS + 40, 250), (70, 30)), manager=self.ui_manager, object_id='#p2_x')
        self.entrada_p2_y = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((LARGURA_CANVAS + 120, 250), (70, 30)), manager=self.ui_manager, object_id='#p2_y')
        self.entrada_p2_x.set_text('70') # Valor inicial
        self.entrada_p2_y.set_text('45') # Valor inicial

        # Botão para desenhar
        self.botao_bresenham = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((LARGURA_CANVAS + 10, 290), (180, 40)), text='Desenhar Linha', manager=self.ui_manager, object_id='#botao_bresenham')

        # ### NOVO ### - Botão para limpar a tela
        self.botao_limpar = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((LARGURA_CANVAS + 10, 340), (180, 40)), text='Limpar Tela', manager=self.ui_manager, object_id='#botao_limpar')


    def atualizar_resolucao_grid(self, nova_largura, nova_altura):
        print(f"Atualizando resolução para {nova_largura}x{nova_altura}")
        self.largura_grid = nova_largura
        self.altura_grid = nova_altura
        self.entrada_largura.set_text(str(self.largura_grid))
        self.entrada_altura.set_text(str(self.altura_grid))
        if self.largura_grid > 0: self.tamanho_celula_x = LARGURA_CANVAS / self.largura_grid
        if self.altura_grid > 0: self.tamanho_celula_y = ALTURA_CANVAS / self.altura_grid
        # ### NOVO ### - Limpa a tela ao mudar a resolução
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
                
                # ### MODIFICADO ### - Processa eventos da interface para os novos botões
                if evento.type == pygame_gui.UI_BUTTON_PRESSED:
                    if evento.ui_element == self.botao_aplicar_res:
                        try:
                            self.atualizar_resolucao_grid(int(self.entrada_largura.get_text()), int(self.entrada_altura.get_text()))
                        except ValueError:
                            print("Erro: A resolução deve ser um número inteiro.")
                    
                    # ### NOVO ### - Lógica do botão de desenhar Bresenham
                    elif evento.ui_element == self.botao_bresenham:
                        try:
                            p1_x = int(self.entrada_p1_x.get_text())
                            p1_y = int(self.entrada_p1_y.get_text())
                            p2_x = int(self.entrada_p2_x.get_text())
                            p2_y = int(self.entrada_p2_y.get_text())
                            
                            # Chama o algoritmo e guarda os pixels
                            linha_pixels = calcular_linha_bresenham((p1_x, p1_y), (p2_x, p2_y))
                            self.pixels_a_desenhar.extend(linha_pixels) # Adiciona a nova linha sem apagar as antigas
                        except ValueError:
                            print("Erro: As coordenadas dos pontos devem ser números inteiros.")
                            
                    # ### NOVO ### - Lógica do botão de limpar
                    elif evento.ui_element == self.botao_limpar:
                        self.pixels_a_desenhar.clear()

                self.ui_manager.process_events(evento)
            
            self.ui_manager.update(delta_time)

            # --- Lógica de Desenho ---
            self.canvas_surface.fill(COR_FUNDO)
            self.desenhar_grade()
            
            # ### MODIFICADO ### - Desenha todos os pixels da lista
            if self.pixels_a_desenhar:
                for pixel in self.pixels_a_desenhar:
                    self.desenhar_pixel(pixel[0], pixel[1])

            self.tela.blit(self.canvas_surface, (0, 0))
            pygame.draw.rect(self.tela, COR_PAINEL, (LARGURA_CANVAS, 0, LARGURA_PAINEL, ALTURA_TOTAL))
            self.ui_manager.draw_ui(self.tela)
            pygame.display.flip()

        pygame.quit()