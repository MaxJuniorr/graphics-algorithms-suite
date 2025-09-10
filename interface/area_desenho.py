import pygame
from utils.historico import Historico
from algoritmos.bresenham import calcular_linha_bresenham
from algoritmos.circulo_elipse import calcular_circulo, calcular_elipse
from algoritmos.curvas_bezier import rasterizar_curva_bezier
from algoritmos.polilinha import rasterizar_polilinha

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
        meia_largura_grid = self.largura_grid // 2
        meia_altura_grid = self.altura_grid // 2

        for x_grid in range(-meia_largura_grid, meia_largura_grid + 1):
            pos_x = centro_x + x_grid * self.tamanho_celula_x
            cor = COR_EIXO if x_grid == 0 else COR_GRADE
            pygame.draw.line(self.surface, cor, (pos_x, 0), (pos_x, self.altura))

        for y_grid in range(-meia_altura_grid, meia_altura_grid + 1):
            pos_y = centro_y - y_grid * self.tamanho_celula_y
            cor = COR_EIXO if y_grid == 0 else COR_GRADE
            pygame.draw.line(self.surface, cor, (0, pos_y), (self.largura, pos_y))

    def desenhar_pixel(self, x_grid, y_grid, cor=COR_PIXEL):
        if self.tamanho_celula_x <= 0 or self.tamanho_celula_y <= 0: return
        centro_x_tela, centro_y_tela = self.largura / 2, self.altura / 2
        x_tela = centro_x_tela + x_grid * self.tamanho_celula_x
        y_tela = centro_y_tela - (y_grid + 1) * self.tamanho_celula_y
        retangulo_pixel = pygame.Rect(x_tela, y_tela, self.tamanho_celula_x, self.tamanho_celula_y)
        pygame.draw.rect(self.surface, cor, retangulo_pixel)

    def adicionar_forma(self, tipo_desenho, parametros):
        self.historico.adicionar_desenho(tipo_desenho, parametros or {})
        self.indice_selecionado = None

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
            pixels = self.rasterizar_desenho(desenho)
            for pixel in pixels:
                self.desenhar_pixel(pixel[0], pixel[1], cor)
                
        tela.blit(self.surface, (0, 0))

    def rasterizar_desenho(self, desenho):
        """Chama o algoritmo de rasterização apropriado para um desenho."""
        tipo = desenho.tipo
        params = desenho.parametros

        if tipo == "Linha (Bresenham)":
            return calcular_linha_bresenham(params['p1'], params['p2'])
        elif tipo == "Círculo":
            return calcular_circulo(params['centro'], params['raio'])
        elif tipo == "Elipse":
            return calcular_elipse(params['centro'], params['rx'], params['ry'])
        elif tipo == "Curva de Bézier":
            pontos = [params[f'p{i}'] for i in range(4)]
            return rasterizar_curva_bezier(*pontos)
        elif tipo == "Polilinha":
            return rasterizar_polilinha(params['pontos'])
        
        return []

    def tela_para_grade(self, x_tela, y_tela):
        """Converte coordenadas da tela (pygame) para coordenadas da grade (cartesianas)."""
        if self.tamanho_celula_x <= 0 or self.tamanho_celula_y <= 0:
            return 0, 0
        centro_x_tela, centro_y_tela = self.largura / 2, self.altura / 2
        offset_x = x_tela - centro_x_tela
        offset_y = centro_y_tela - y_tela
        x_grid = int(offset_x // self.tamanho_celula_x)
        y_grid = int(offset_y // self.tamanho_celula_y)
        return x_grid, y_grid
