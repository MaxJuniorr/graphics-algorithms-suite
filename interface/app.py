# interface/app.py
import pygame
import pygame_gui

# --- Constantes de Cores ---
COR_FUNDO = (20, 20, 20)
COR_GRADE = (40, 40, 40)
COR_PAINEL = (60, 60, 60)
COR_PIXEL = (255, 255, 255)

# --- Constantes de Layout ---
LARGURA_TOTAL = 1000
ALTURA_TOTAL = 800
LARGURA_PAINEL = 200  # Largura do painel de controle à direita
LARGURA_CANVAS = LARGURA_TOTAL - LARGURA_PAINEL
ALTURA_CANVAS = ALTURA_TOTAL

class Aplicacao:
    def __init__(self, largura_grid_inicial, altura_grid_inicial):
        pygame.init()

        # Janela principal
        self.tela = pygame.display.set_mode((LARGURA_TOTAL, ALTURA_TOTAL))
        pygame.display.set_caption("Trabalho de Computação Gráfica")

        # Superfície de Desenho (Canvas)
        # É aqui que a grade e os algoritmos serão desenhados
        self.canvas_surface = pygame.Surface((LARGURA_CANVAS, ALTURA_CANVAS))

        # Gerenciador da Interface Gráfica (GUI)
        self.ui_manager = pygame_gui.UIManager((LARGURA_TOTAL, ALTURA_TOTAL))
        self.construir_interface()
        
        # Estado da aplicação
        self.rodando = True
        self.clock = pygame.time.Clock()
        
        # Inicializa a grade com os valores passados
        self.largura_grid = 0
        self.altura_grid = 0
        self.tamanho_celula_x = 0
        self.tamanho_celula_y = 0
        self.atualizar_resolucao_grid(largura_grid_inicial, altura_grid_inicial)


    def construir_interface(self):
        """Cria os elementos da GUI no painel de controle."""
        # --- Seção de Resolução ---
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((LARGURA_CANVAS + 10, 10), (180, 20)),
            text='Configuração da Grade', manager=self.ui_manager)
        
        # Largura
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((LARGURA_CANVAS + 10, 40), (80, 20)),
            text='Largura:', manager=self.ui_manager)
        self.entrada_largura = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((LARGURA_CANVAS + 90, 40), (100, 30)),
            manager=self.ui_manager, object_id='#largura_grid')
        
        # Altura
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((LARGURA_CANVAS + 10, 80), (80, 20)),
            text='Altura:', manager=self.ui_manager)
        self.entrada_altura = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((LARGURA_CANVAS + 90, 80), (100, 30)),
            manager=self.ui_manager, object_id='#altura_grid')

        # Botão para aplicar
        self.botao_aplicar = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((LARGURA_CANVAS + 10, 120), (180, 40)),
            text='Aplicar Resolução', manager=self.ui_manager, object_id='#botao_aplicar')
    
    def atualizar_resolucao_grid(self, nova_largura, nova_altura):
        """Recalcula as propriedades da grade com base em uma nova resolução."""
        print(f"Atualizando resolução para {nova_largura}x{nova_altura}")
        self.largura_grid = nova_largura
        self.altura_grid = nova_altura
        
        # Preenche os campos de texto com os valores atuais
        self.entrada_largura.set_text(str(self.largura_grid))
        self.entrada_altura.set_text(str(self.altura_grid))
        
        # Evitar divisão por zero se a resolução for 0
        if self.largura_grid > 0:
            self.tamanho_celula_x = LARGURA_CANVAS / self.largura_grid
        if self.altura_grid > 0:
            self.tamanho_celula_y = ALTURA_CANVAS / self.altura_grid

    def desenhar_grade(self):
        """Desenha as linhas da grade no canvas."""
        for x in range(0, self.largura_grid + 1):
            pos_x = x * self.tamanho_celula_x
            pygame.draw.line(self.canvas_surface, COR_GRADE, (pos_x, 0), (pos_x, ALTURA_CANVAS))
            
        for y in range(0, self.altura_grid + 1):
            pos_y = y * self.tamanho_celula_y
            pygame.draw.line(self.canvas_surface, COR_GRADE, (0, pos_y), (LARGURA_CANVAS, pos_y))

    def desenhar_pixel(self, x_grid, y_grid, cor=COR_PIXEL):
        """Desenha uma célula da grade no canvas."""
        if self.tamanho_celula_x <= 0 or self.tamanho_celula_y <= 0: return

        x_tela = x_grid * self.tamanho_celula_x
        y_tela = y_grid * self.tamanho_celula_y

        retangulo_pixel = pygame.Rect(x_tela, y_tela, self.tamanho_celula_x, self.tamanho_celula_y)
        pygame.draw.rect(self.canvas_surface, cor, retangulo_pixel)

    def executar(self):
        """Inicia o loop principal da aplicação."""
        while self.rodando:
            delta_time = self.clock.tick(60) / 1000.0

            # --- Tratamento de Eventos ---
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.rodando = False
                
                # Processa eventos da interface
                if evento.type == pygame_gui.UI_BUTTON_PRESSED:
                    if evento.ui_element == self.botao_aplicar:
                        try:
                            nova_largura = int(self.entrada_largura.get_text())
                            nova_altura = int(self.entrada_altura.get_text())
                            self.atualizar_resolucao_grid(nova_largura, nova_altura)
                        except ValueError:
                            print("Erro: A resolução deve ser um número inteiro.")
                
                self.ui_manager.process_events(evento)
            
            # --- Lógica de Atualização da GUI ---
            self.ui_manager.update(delta_time)

            # --- Lógica de Desenho ---
            # 1. Limpa o canvas
            self.canvas_surface.fill(COR_FUNDO)
            
            # 2. Desenha a grade e os algoritmos no canvas
            self.desenhar_grade()
            self.desenhar_pixel(self.largura_grid // 2, self.altura_grid // 2)

            # 3. Desenha o canvas na tela principal
            self.tela.blit(self.canvas_surface, (0, 0))
            
            # 4. Desenha o painel de controle e a GUI por cima
            pygame.draw.rect(self.tela, COR_PAINEL, (LARGURA_CANVAS, 0, LARGURA_PAINEL, ALTURA_TOTAL))
            self.ui_manager.draw_ui(self.tela)

            # --- Atualização Final ---
            pygame.display.flip()

        pygame.quit()