import pygame
import pygame_gui
from interface.painel_controle import PainelControle
from interface.area_desenho import AreaDesenho
from algoritmos.bresenham import calcular_linha_bresenham
from algoritmos.circulo_elipse import calcular_circulo, calcular_elipse
from algoritmos.curvas_bezier import rasterizar_curva_bezier

# --- Constantes de Layout ---
LARGURA_TOTAL = 1200
ALTURA_TOTAL = 950
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
        # Preload de fontes usadas em tags <b> e <i> do histórico para evitar avisos
        self.ui_manager.preload_fonts([
            {'name': 'noto_sans', 'point_size': 14, 'style': 'bold', 'antialiased': True},
            {'name': 'noto_sans', 'point_size': 14, 'style': 'italic', 'antialiased': True},
        ])
        
        self.area_desenho = AreaDesenho(LARGURA_CANVAS, ALTURA_CANVAS, largura_grid_inicial, altura_grid_inicial)
        self.painel_controle = PainelControle(self.ui_manager, LARGURA_PAINEL, ALTURA_TOTAL, LARGURA_CANVAS)

        self.rodando = True
        self.clock = pygame.time.Clock()
        
    def mostrar_historico(self):
        """Mostra o histórico de desenhos na tela."""
        historico = self.area_desenho.obter_historico()
        print("\n=== Histórico de Desenhos ===")
        if not historico:
            print("Nenhum desenho no histórico.")
        else:
            for i, desenho in enumerate(historico, 1):
                print(f"\nDesenho {i}:")
                print(f"Tipo: {desenho.tipo}")
                print(f"Parâmetros: {desenho.parametros}")
                print(f"Timestamp: {desenho.timestamp.strftime('%H:%M:%S')}")
                print(f"Total de pixels: {len(desenho.pixels)}")

    def executar(self):
        while self.rodando:
            delta_time = self.clock.tick(60) / 1000.0

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.rodando = False
                
                # Processar eventos do pygame_gui
                self.ui_manager.process_events(evento)
                
                # Processar eventos específicos da aplicação
                if evento.type == pygame_gui.UI_BUTTON_PRESSED:
                    self.manipular_eventos_ui(evento)
                elif evento.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    if evento.ui_element == self.painel_controle.seletor_figura:
                        self.painel_controle.mostrar_elementos_figura(evento.text)
                
            # Atualiza o histórico a cada frame
            self.painel_controle.atualizar_historico(self.area_desenho.obter_historico())
            
            self.ui_manager.update(delta_time)
            
            self.area_desenho.desenhar(self.tela)
            pygame.draw.rect(self.tela, COR_PAINEL, (LARGURA_CANVAS, 0, LARGURA_PAINEL, ALTURA_TOTAL))
            self.ui_manager.draw_ui(self.tela)
            
            pygame.display.flip()

        pygame.quit()

    def manipular_eventos_ui(self, evento):
        painel = self.painel_controle
        
        # Botão de Resolução
        if evento.ui_element == painel.botao_aplicar_res:
            try:
                nova_largura = int(painel.entrada_largura.get_text())
                nova_altura = int(painel.entrada_altura.get_text())
                self.area_desenho.atualizar_resolucao_grid(nova_largura, nova_altura)
            except ValueError:
                print("Erro: A resolução deve ser um número inteiro.")
        
        # Botões de Desenho
        
        elif evento.ui_element == painel.elementos_linha.get('botao'):
            try:
                p1 = (int(painel.elementos_linha['p1_x'].get_text()), int(painel.elementos_linha['p1_y'].get_text()))
                p2 = (int(painel.elementos_linha['p2_x'].get_text()), int(painel.elementos_linha['p2_y'].get_text()))
                pixels = calcular_linha_bresenham(p1, p2)
                parametros = {'p1': p1, 'p2': p2}
                self.area_desenho.adicionar_pixels(pixels, "Linha (Bresenham)", parametros)
            except ValueError:
                print("Erro: As coordenadas da linha devem ser números inteiros.")

        elif evento.ui_element == painel.elementos_circulo.get('botao'):
            try:
                centro = (int(painel.elementos_circulo['centro_x'].get_text()),
                         int(painel.elementos_circulo['centro_y'].get_text()))
                raio = int(painel.elementos_circulo['raio'].get_text())
                pixels = calcular_circulo(centro, raio)
                parametros = {'centro': centro, 'raio': raio}
                self.area_desenho.adicionar_pixels(pixels, "Círculo", parametros)
            except ValueError:
                print("Erro: As coordenadas do centro e o raio devem ser números inteiros.")

        elif evento.ui_element == painel.elementos_bezier.get('botao'):
            try:
                p0 = (int(painel.elementos_bezier['p0_x'].get_text()),
                      int(painel.elementos_bezier['p0_y'].get_text()))
                p1 = (int(painel.elementos_bezier['p1_x'].get_text()),
                      int(painel.elementos_bezier['p1_y'].get_text()))
                p2 = (int(painel.elementos_bezier['p2_x'].get_text()),
                      int(painel.elementos_bezier['p2_y'].get_text()))
                p3 = (int(painel.elementos_bezier['p3_x'].get_text()),
                      int(painel.elementos_bezier['p3_y'].get_text()))
                pixels = rasterizar_curva_bezier(p0, p1, p2, p3)
                parametros = {'p0': p0, 'p1': p1, 'p2': p2, 'p3': p3}
                self.area_desenho.adicionar_pixels(pixels, "Curva de Bézier", parametros)
            except ValueError:
                print("Erro: As coordenadas dos pontos de controle devem ser números inteiros.")
        
        elif evento.ui_element == painel.elementos_elipse.get('botao'):
            try:
                centro = (int(painel.elementos_elipse['centro_x'].get_text()),
                         int(painel.elementos_elipse['centro_y'].get_text()))
                rx = int(painel.elementos_elipse['rx'].get_text())
                ry = int(painel.elementos_elipse['ry'].get_text())
                pixels = calcular_elipse(centro, rx, ry)
                parametros = {'centro': centro, 'rx': rx, 'ry': ry}
                self.area_desenho.adicionar_pixels(pixels, "Elipse", parametros)
            except ValueError:
                print("Erro: As coordenadas do centro e os raios devem ser números inteiros.")
                        
        elif evento.ui_element == painel.botao_limpar:
            self.area_desenho.limpar_pixels()
            
        elif evento.ui_element == painel.botao_desfazer:
            self.area_desenho.desfazer_ultimo_desenho()
                        
        elif evento.ui_element == painel.botao_limpar:
            self.area_desenho.limpar_pixels()
        else:
            # Verifica se é um botão de exclusão do histórico
            if hasattr(painel, '_historico_itens'):
                for item in painel._historico_itens:
                    for w in item.get('widgets', []):
                        if isinstance(w, pygame_gui.elements.UIButton) and evento.ui_element == w:
                            indice_real = getattr(w, 'indice_historico_real', None)
                            if indice_real is not None:
                                self.area_desenho.remover_desenho_indice(indice_real)
                            return