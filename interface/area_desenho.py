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
COR_SELECIONADO = (255, 255, 0)


class AreaDesenho:
    """
    Canvas baseado em grade cartesiana, com gerenciamento de histórico e
    rasterização de formas para pixels do grid.

    Principais responsabilidades:
    - Manter resolução da grade (largura x altura) e calcular o tamanho das
        células em pixels (tamanho_celula_x/y) de acordo com o tamanho da janela;
    - Desenhar a grade e eixos (x=0, y=0) para referência visual;
    - Gerenciar o histórico (adicionar, remover, desfazer, seleção atual);
    - Rasterizar e desenhar cada item do histórico por tipo (linha, círculo,
        elipse, Bézier, polilinha, pontos);
    - Exibir pré-visualizações (polilinha em construção e janela convexa);
    - Converter coordenadas de tela (pixels) para coordenadas de grade (inteiros).
    """
    def __init__(self, largura, altura, largura_grid, altura_grid):
        self.largura = largura
        self.altura = altura
        self.surface = pygame.Surface((largura, altura))
        self.historico = Historico()
        self.indice_selecionado = None
        self.janela_recorte = None
        self.preview_polilinha = None  # lista de pontos (x, y) para pré-visualização
        self.preview_clip_poligono = None  # janela de recorte poligonal (convexa)
        # valores padrão até atualizar a resolução
        self.tamanho_celula_x = 0
        self.tamanho_celula_y = 0
        self.atualizar_resolucao_grid(largura_grid, altura_grid)

    def definir_janela_recorte(self, rect):
        self.janela_recorte = rect

    def limpar_janela_recorte(self):
        self.janela_recorte = None

    def definir_preview_polilinha(self, pontos):
        self.preview_polilinha = list(pontos) if pontos else None

    def limpar_preview_polilinha(self):
        self.preview_polilinha = None

    def definir_preview_clip_poligono(self, pontos):
        self.preview_clip_poligono = list(pontos) if pontos else None

    def limpar_preview_clip_poligono(self):
        self.preview_clip_poligono = None

    def atualizar_resolucao_grid(self, nova_largura, nova_altura):
        """
        Define uma nova resolução de grade (quantidade de células horizontais e
        verticais) e recalcula o tamanho de cada célula em pixels. Limpa a tela
        para refletir a nova resolução.
        """
        self.largura_grid = nova_largura
        self.altura_grid = nova_altura
        self.tamanho_celula_x = (self.largura / self.largura_grid) if self.largura_grid > 0 else 0
        self.tamanho_celula_y = (self.altura / self.altura_grid) if self.altura_grid > 0 else 0
        self.limpar_pixels()

    def desenhar_grade(self):
        """
        Desenha linhas verticais e horizontais igualmente espaçadas conforme a
        resolução de grade atual. Os eixos x=0 e y=0 são destacados.
        """
        centro_x, centro_y = self.largura / 2, self.altura / 2
        half_w = self.largura_grid // 2
        half_h = self.altura_grid // 2

        for xg in range(-half_w, half_w + 1):
            pos_x = centro_x + xg * self.tamanho_celula_x
            cor = COR_EIXO if xg == 0 else COR_GRADE
            pygame.draw.line(self.surface, cor, (pos_x, 0), (pos_x, self.altura))

        for yg in range(-half_h, half_h + 1):
            pos_y = centro_y - yg * self.tamanho_celula_y
            cor = COR_EIXO if yg == 0 else COR_GRADE
            pygame.draw.line(self.surface, cor, (0, pos_y), (self.largura, pos_y))

    def desenhar_pixel(self, x_grid, y_grid, cor=COR_PIXEL):
        """
        Pinta a célula correspondente às coordenadas de grade (x_grid, y_grid).

        Conversão grade→tela:
        - Origem no centro da superfície (cx, cy);
        - Eixo x positivo para a direita; y positivo para cima (logo, ao ir para
          cima no grid, a coordenada de tela diminui);
        - O retângulo desenhado tem o tamanho de uma célula (tamanho_celula_x/y).
        """
        if self.tamanho_celula_x <= 0 or self.tamanho_celula_y <= 0:
            return
        cx, cy = self.largura / 2, self.altura / 2
        x_tela = cx + x_grid * self.tamanho_celula_x
        y_tela = cy - (y_grid + 1) * self.tamanho_celula_y
        rect = pygame.Rect(x_tela, y_tela, self.tamanho_celula_x, self.tamanho_celula_y)
        pygame.draw.rect(self.surface, cor, rect)

    def adicionar_forma(self, tipo_desenho, parametros):
        self.historico.adicionar_desenho(tipo_desenho, parametros or {})
        self.indice_selecionado = None

    def limpar_pixels(self):
        self.historico.limpar_historico()
        self.indice_selecionado = None
        self.limpar_janela_recorte()
        self.limpar_preview_polilinha()
        self.limpar_preview_clip_poligono()

    def desfazer_ultimo_desenho(self):
        self.historico.desfazer_ultimo_desenho()
        self.indice_selecionado = None

    def obter_historico(self):
        return self.historico.obter_desenhos()

    def remover_desenho_indice(self, indice: int):
        self.historico.remover_por_indice(indice)
        self.indice_selecionado = None

    def selecionar_desenho(self, indice):
        # Permite desselecionar quando indice=None
        if indice is None:
            self.indice_selecionado = None
            return
        historico = self.obter_historico()
        if 0 <= indice < len(historico):
            self.indice_selecionado = indice
        else:
            self.indice_selecionado = None

    def obter_indice_selecionado(self):
        return self.indice_selecionado

    def desenhar(self, tela):
        """
        Redesenha completamente a área de desenho:
        1) Fundo + grade + eixos
        2) Janela retangular de recorte (se houver)
        3) Formas do histórico rasterizadas (com destaque para a seleção)
        4) Pré-visualizações (polilinha e janela convexa)
        """
        self.surface.fill(COR_FUNDO)
        self.desenhar_grade()

        # Janela retangular (margens) em vermelho
        if self.janela_recorte:
            xmin, ymin, xmax, ymax = self.janela_recorte
            x0 = self.largura / 2 + xmin * self.tamanho_celula_x
            y0 = self.altura / 2 - (ymax + 1) * self.tamanho_celula_y
            w = (xmax - xmin + 1) * self.tamanho_celula_x
            h = (ymax - ymin + 1) * self.tamanho_celula_y
            rect = pygame.Rect(x0, y0, w, h)
            pygame.draw.rect(self.surface, (255, 0, 0), rect, 1)

        # Desenha histórico
        for i, desenho in enumerate(self.obter_historico()):
            cor = COR_SELECIONADO if i == self.indice_selecionado else COR_PIXEL
            pixels = self.rasterizar_desenho(desenho)
            for p in pixels:
                self.desenhar_pixel(p[0], p[1], cor)

        # Pré-visualização da polilinha (em vermelho)
        if self.preview_polilinha and len(self.preview_polilinha) >= 2:
            preview_pixels = rasterizar_polilinha(self.preview_polilinha)
            for p in preview_pixels:
                self.desenhar_pixel(p[0], p[1], (255, 0, 0))

        # Pré-visualização da janela de recorte poligonal (em vermelho)
        if self.preview_clip_poligono and len(self.preview_clip_poligono) >= 2:
            pts = self.preview_clip_poligono
            chain = pts if pts[0] == pts[-1] else (pts + [pts[0]] if len(pts) >= 3 else pts)
            clip_pixels = rasterizar_polilinha(chain)
            for p in clip_pixels:
                self.desenhar_pixel(p[0], p[1], (255, 0, 0))

        tela.blit(self.surface, (0, 0))

    def rasterizar_desenho(self, desenho):
        """
        Converte um item do histórico (tipo + parâmetros) na lista de pixels de
        grade que devem ser pintados. Para curvas/linhas, delega para os módulos
        de algoritmos correspondentes; para "Pontos" retorna diretamente.
        """
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
        elif tipo.startswith("Projeção") or tipo == "Pontos":
            return params.get('pontos', [])
        return []

    def tela_para_grade(self, x_tela, y_tela):
        """
        Converte coordenadas de tela (em pixels, origem no canto superior
        esquerdo) para coordenadas de grade inteiras.

        Fórmulas:
        - x_grid = floor((x_tela - cx) / tamanho_celula_x)
        - y_grid = floor((cy - y_tela) / tamanho_celula_y)
        """
        if self.tamanho_celula_x <= 0 or self.tamanho_celula_y <= 0:
            return 0, 0
        cx, cy = self.largura / 2, self.altura / 2
        dx = x_tela - cx
        dy = cy - y_tela
        x_grid = int(dx // self.tamanho_celula_x)
        y_grid = int(dy // self.tamanho_celula_y)
        return x_grid, y_grid
