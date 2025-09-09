import pygame
from utils.historico import Historico

COR_FUNDO = (20, 20, 20)
COR_GRADE = (40, 40, 40)
COR_PIXEL = (255, 255, 255)

class AreaDesenho:
    def __init__(self, largura, altura, largura_grid, altura_grid):
        self.largura = largura
        self.altura = altura
        self.surface = pygame.Surface((largura, altura))
        self.pixels_a_desenhar = []
        self.historico = Historico()
        self.atualizar_resolucao_grid(largura_grid, altura_grid)

    def atualizar_resolucao_grid(self, nova_largura, nova_altura):
        print(f"Atualizando resolução para {nova_largura}x{nova_altura}")
        self.largura_grid = nova_largura
        self.altura_grid = nova_altura
        if self.largura_grid > 0:
            self.tamanho_celula_x = self.largura / self.largura_grid
        if self.altura_grid > 0:
            self.tamanho_celula_y = self.altura / self.altura_grid
        self.limpar_pixels()

    def desenhar_grade(self):
        for x in range(0, self.largura_grid + 1):
            pos_x = x * self.tamanho_celula_x
            pygame.draw.line(self.surface, COR_GRADE, (pos_x, 0), (pos_x, self.altura))
        for y in range(0, self.altura_grid + 1):
            pos_y = y * self.tamanho_celula_y
            pygame.draw.line(self.surface, COR_GRADE, (0, pos_y), (self.largura, pos_y))

    def desenhar_pixel(self, x_grid, y_grid, cor=COR_PIXEL):
        if self.tamanho_celula_x <= 0 or self.tamanho_celula_y <= 0: return
        if not (0 <= x_grid < self.largura_grid and 0 <= y_grid < self.altura_grid):
            return
        
        x_tela = x_grid * self.tamanho_celula_x
        y_tela = y_grid * self.tamanho_celula_y
        retangulo_pixel = pygame.Rect(x_tela, y_tela, self.tamanho_celula_x, self.tamanho_celula_y)
        pygame.draw.rect(self.surface, cor, retangulo_pixel)

    def adicionar_pixels(self, pixels, tipo_desenho=None, parametros=None):
        """Adiciona pixels ao desenho e registra no histórico."""
        self.pixels_a_desenhar.extend(pixels)
        if tipo_desenho:  # Se foi especificado um tipo, registra no histórico
            self.historico.adicionar_desenho(tipo_desenho, parametros or {}, pixels)

    def limpar_pixels(self):
        """Limpa todos os pixels e o histórico."""
        self.pixels_a_desenhar.clear()
        self.historico.limpar_historico()

    def desfazer_ultimo_desenho(self):
        """Desfaz o último desenho feito."""
        self.pixels_a_desenhar = self.historico.desfazer_ultimo_desenho()

    def obter_historico(self):
        """Retorna o histórico de desenhos."""
        return self.historico.obter_desenhos()

    def remover_desenho_indice(self, indice: int):
        """Remove um desenho específico pelo índice no histórico (0 = mais antigo)."""
        self.pixels_a_desenhar = self.historico.remover_por_indice(indice)

    def desenhar(self, tela):
        self.surface.fill(COR_FUNDO)
        self.desenhar_grade()
        if self.pixels_a_desenhar:
            for pixel in self.pixels_a_desenhar:
                self.desenhar_pixel(pixel[0], pixel[1])
        tela.blit(self.surface, (0, 0))