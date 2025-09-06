import pygame
import pygame_gui
from interface.painel_controle import PainelControle
from interface.area_desenho import AreaDesenho
from algoritmos.bresenham import calcular_linha_bresenham
from algoritmos.circulo_elipse import calcular_circulo
from algoritmos.curvas_bezier import rasterizar_curva_bezier

# --- Constantes de Layout ---
LARGURA_TOTAL = 1200
ALTURA_TOTAL = 800
LARGURA_PAINEL = 400
LARGURA_CANVAS = LARGURA_TOTAL - LARGURA_PAINEL
ALTURA_CANVAS = ALTURA_TOTAL
COR_PAINEL = (60, 60, 60)

class Aplicacao:
    def __init__(self, largura_grid_inicial, altura_grid_inicial):
        pygame.init()

        self.tela = pygame.display.set_mode((LARGURA_TOTAL, ALTURA_TOTAL))
        pygame.display.set_caption("Trabalho de Computação Gráfica")
        self.ui_manager = pygame_gui.UIManager((LARGURA_TOTAL, ALTURA_TOTAL))
        
        self.area_desenho = AreaDesenho(LARGURA_CANVAS, ALTURA_CANVAS, largura_grid_inicial, altura_grid_inicial)
        self.painel_controle = PainelControle(self.ui_manager, LARGURA_PAINEL, ALTURA_TOTAL, LARGURA_CANVAS)

        self.rodando = True
        self.clock = pygame.time.Clock()

    def executar(self):
        while self.rodando:
            delta_time = self.clock.tick(60) / 1000.0

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.rodando = False
                
                if evento.type == pygame_gui.UI_BUTTON_PRESSED:
                    self.manipular_eventos_ui(evento)

                self.ui_manager.process_events(evento)
            
            self.ui_manager.update(delta_time)
            
            self.area_desenho.desenhar(self.tela)
            pygame.draw.rect(self.tela, COR_PAINEL, (LARGURA_CANVAS, 0, LARGURA_PAINEL, ALTURA_TOTAL))
            self.ui_manager.draw_ui(self.tela)
            
            pygame.display.flip()

        pygame.quit()

    def manipular_eventos_ui(self, evento):
        painel = self.painel_controle
        if evento.ui_element == painel.botao_aplicar_res:
            try:
                nova_largura = int(painel.entrada_largura.get_text())
                nova_altura = int(painel.entrada_altura.get_text())
                self.area_desenho.atualizar_resolucao_grid(nova_largura, nova_altura)
            except ValueError:
                print("Erro: A resolução deve ser um número inteiro.")
        
        elif evento.ui_element == painel.botao_bresenham:
            try:
                p1 = (int(painel.entrada_p1_x.get_text()), int(painel.entrada_p1_y.get_text()))
                p2 = (int(painel.entrada_p2_x.get_text()), int(painel.entrada_p2_y.get_text()))
                pixels = calcular_linha_bresenham(p1, p2)
                self.area_desenho.adicionar_pixels(pixels)
            except ValueError:
                print("Erro: As coordenadas da linha devem ser números inteiros.")

        elif evento.ui_element == painel.botao_circulo:
            try:
                centro = (int(painel.entrada_centro_x.get_text()), int(painel.entrada_centro_y.get_text()))
                raio = int(painel.entrada_raio.get_text())
                pixels = calcular_circulo(centro, raio)
                self.area_desenho.adicionar_pixels(pixels)
            except ValueError:
                 print("Erro: As coordenadas do centro e o raio devem ser números inteiros.")

        elif evento.ui_element == painel.botao_bezier:
            try:
                p0 = (int(painel.entrada_b_p0_x.get_text()), int(painel.entrada_b_p0_y.get_text()))
                p1 = (int(painel.entrada_b_p1_x.get_text()), int(painel.entrada_b_p1_y.get_text()))
                p2 = (int(painel.entrada_b_p2_x.get_text()), int(painel.entrada_b_p2_y.get_text()))
                p3 = (int(painel.entrada_b_p3_x.get_text()), int(painel.entrada_b_p3_y.get_text()))
                pixels = rasterizar_curva_bezier(p0, p1, p2, p3)
                self.area_desenho.adicionar_pixels(pixels)
            except ValueError:
                print("Erro: As coordenadas dos pontos de controle devem ser números inteiros.")
                        
        elif evento.ui_element == painel.botao_limpar:
            self.area_desenho.limpar_pixels()