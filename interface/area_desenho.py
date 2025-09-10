import pygame
from utils.historico import Historico

COR_FUNDO = (20, 20, 20)
COR_GRADE = (40, 40, 40)
COR_EIXO = (80, 80, 80)
COR_PIXEL = (255, 255, 255)
COR_SELECIONADO = (255, 255, 0)  # Amarelo para destaque

class AreaDesenho:
    def __init__(self, largura, altura, largura_grid, altura_grid):
        self.largura = largura
        self.altura = altura
        self.surface = pygame.Surface((largura, altura))
        self.historico = Historico()
        self.indice_selecionado = None
        self.atualizar_resolucao_grid(largura_grid, altura_grid)

    def atualizar_resolucao_grid(self, nova_largura, nova_altura):
        self.largura_grid = nova_largura
        self.altura_grid = nova_altura
        if self.largura_grid > 0:
            self.tamanho_celula_x = self.largura / self.largura_grid
        if self.altura_grid > 0:
            self.tamanho_celula_y = self.altura / self.altura_grid
        self.limpar_pixels()

    def desenhar_grade(self):
        centro_x, centro_y = self.largura / 2, self.altura / 2
        
        # Limites da grade em coordenadas de grade
        meia_largura_grid = self.largura_grid // 2
        meia_altura_grid = self.altura_grid // 2

        # Linhas verticais
        for x_grid in range(-meia_largura_grid, meia_largura_grid + 1):
            pos_x = centro_x + x_grid * self.tamanho_celula_x
            cor = COR_EIXO if x_grid == 0 else COR_GRADE
            pygame.draw.line(self.surface, cor, (pos_x, 0), (pos_x, self.altura))

        # Linhas horizontais
        for y_grid in range(-meia_altura_grid, meia_altura_grid + 1):
            pos_y = centro_y - y_grid * self.tamanho_celula_y
            cor = COR_EIXO if y_grid == 0 else COR_GRADE
            pygame.draw.line(self.surface, cor, (0, pos_y), (self.largura, pos_y))

    def desenhar_pixel(self, x_grid, y_grid, cor=COR_PIXEL):
        if self.tamanho_celula_x <= 0 or self.tamanho_celula_y <= 0: return

        # Converte coordenadas da grade (centro (0,0)) para coordenadas da tela (canto sup. esq. (0,0))
        centro_x_tela, centro_y_tela = self.largura / 2, self.altura / 2
        
        # Calcula a posição do canto superior esquerdo da célula da grade na tela
        x_tela = centro_x_tela + x_grid * self.tamanho_celula_x
        y_tela = centro_y_tela - (y_grid + 1) * self.tamanho_celula_y

        # Pygame lida com o clipping de retângulos fora da superfície, então a verificação de limites não é necessária aqui.
        retangulo_pixel = pygame.Rect(x_tela, y_tela, self.tamanho_celula_x, self.tamanho_celula_y)
        pygame.draw.rect(self.surface, cor, retangulo_pixel)

    def adicionar_pixels(self, pixels, tipo_desenho=None, parametros=None):
        if tipo_desenho:
            self.historico.adicionar_desenho(tipo_desenho, parametros or {}, pixels)
        self.indice_selecionado = None # Desseleciona ao adicionar novo

    def limpar_pixels(self):
        self.historico.limpar_historico()
        self.indice_selecionado = None

    def desfazer_ultimo_desenho(self):
        self.historico.desfazer_ultimo_desenho()
        self.indice_selecionado = None

    def obter_historico(self):
        return self.historico.obter_desenhos()

    def remover_desenho_indice(self, indice: int):
        self.historico.remover_por_indice(indice)
        self.indice_selecionado = None

    def selecionar_desenho(self, indice: int):
        historico = self.obter_historico()
        if 0 <= indice < len(historico):
            self.indice_selecionado = indice
        else:
            self.indice_selecionado = None

    def obter_indice_selecionado(self):
        return self.indice_selecionado

    def desenhar(self, tela):
        self.surface.fill(COR_FUNDO)
        self.desenhar_grade()
        
        for i, desenho in enumerate(self.obter_historico()):
            cor = COR_SELECIONADO if i == self.indice_selecionado else COR_PIXEL
            for pixel in desenho.pixels:
                self.desenhar_pixel(pixel[0], pixel[1], cor)
                
        tela.blit(self.surface, (0, 0))

    def tela_para_grade(self, x_tela, y_tela):
        """Converte coordenadas da tela (pygame) para coordenadas da grade (cartesianas)."""
        if self.tamanho_celula_x <= 0 or self.tamanho_celula_y <= 0:
            return 0, 0

        centro_x_tela, centro_y_tela = self.largura / 2, self.altura / 2

        # Calcula o deslocamento a partir do centro da tela
        offset_x = x_tela - centro_x_tela
        offset_y = centro_y_tela - y_tela  # Inverte o eixo Y

        # Converte o deslocamento em pixels para coordenadas de grade
        x_grid = int(offset_x // self.tamanho_celula_x)
        y_grid = int(offset_y // self.tamanho_celula_y)

        return x_grid, y_grid