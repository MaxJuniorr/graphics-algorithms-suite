import pygame
import pygame_gui
from interface.painel_controle import PainelControle
from interface.area_desenho import AreaDesenho
from algoritmos.bresenham import calcular_linha_bresenham
from algoritmos.circulo_elipse import calcular_circulo, calcular_elipse
from algoritmos.curvas_bezier import rasterizar_curva_bezier
from algoritmos.polilinha import rasterizar_polilinha

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
        self.proximo_clique_define = None # Estado para o modo de definição de ponto
        
    def executar(self):
        while self.rodando:
            delta_time = self.clock.tick(60) / 1000.0

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.rodando = False

                # Manipulador de clique do mouse para definir pontos
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    if self.proximo_clique_define and evento.pos[0] < LARGURA_CANVAS:
                        coords = self.area_desenho.tela_para_grade(*evento.pos)
                        self.definir_coordenadas_por_clique(coords)
                        self.proximo_clique_define = None # Reseta o modo

                self.ui_manager.process_events(evento)
                
                if evento.type == pygame_gui.UI_BUTTON_PRESSED:
                    self.manipular_eventos_ui(evento)
                elif evento.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    if evento.ui_element == self.painel_controle.seletor_figura:
                        self.painel_controle.mostrar_elementos_figura(evento.text)
                elif evento.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
                    if evento.ui_element == self.painel_controle.lista_historico:
                        self.manipular_selecao_historico(evento)

            # Atualiza o painel de controle com os dados mais recentes
            self.painel_controle.atualizar_historico(
                self.area_desenho.obter_historico(), 
                self.area_desenho.obter_indice_selecionado()
            )
            
            self.ui_manager.update(delta_time)
            
            # Desenha tudo
            self.area_desenho.desenhar(self.tela)
            pygame.draw.rect(self.tela, COR_PAINEL, (LARGURA_CANVAS, 0, LARGURA_PAINEL, ALTURA_TOTAL))
            self.ui_manager.draw_ui(self.tela)
            
            pygame.display.flip()

        pygame.quit()

    def definir_coordenadas_por_clique(self, coords):
        """Atualiza os campos de texto da UI com base no estado de self.proximo_clique_define."""
        tipo_figura, ponto = self.proximo_clique_define
        x_str, y_str = str(coords[0]), str(coords[1])

        if tipo_figura == 'linha':
            self.painel_controle.elementos_linha[f'{ponto}_x'].set_text(x_str)
            self.painel_controle.elementos_linha[f'{ponto}_y'].set_text(y_str)
        elif tipo_figura == 'circulo':
            self.painel_controle.elementos_circulo['centro_x'].set_text(x_str)
            self.painel_controle.elementos_circulo['centro_y'].set_text(y_str)
        elif tipo_figura == 'elipse':
            self.painel_controle.elementos_elipse['centro_x'].set_text(x_str)
            self.painel_controle.elementos_elipse['centro_y'].set_text(y_str)
        elif tipo_figura == 'bezier':
            self.painel_controle.elementos_bezier[f'{ponto}_x'].set_text(x_str)
            self.painel_controle.elementos_bezier[f'{ponto}_y'].set_text(y_str)

    def manipular_selecao_historico(self, evento):
        """Lida com a seleção de um item na lista de histórico."""
        item_selecionado = evento.text
        if not item_selecionado:
            self.area_desenho.selecionar_desenho(None)
            return

        try:
            if item_selecionado.startswith('* '):
                item_selecionado = item_selecionado[2:]
            
            indice_str = item_selecionado.split('.')[0]
            indice = int(indice_str) - 1
            self.area_desenho.selecionar_desenho(indice)
        except (ValueError, IndexError):
            print(f"Erro ao parsear o índice do histórico: {item_selecionado}")
            self.area_desenho.selecionar_desenho(None)

    def manipular_eventos_ui(self, evento):
        painel = self.painel_controle
        
        if evento.ui_element == painel.botao_aplicar_res:
            try:
                nova_largura = int(painel.entrada_largura.get_text())
                nova_altura = int(painel.entrada_altura.get_text())
                self.area_desenho.atualizar_resolucao_grid(nova_largura, nova_altura)
            except ValueError:
                print("Erro: A resolução deve ser um número inteiro.")
        
        # --- Botões de Desenho ---
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
                centro = (int(painel.elementos_circulo['centro_x'].get_text()), int(painel.elementos_circulo['centro_y'].get_text()))
                raio = int(painel.elementos_circulo['raio'].get_text())
                pixels = calcular_circulo(centro, raio)
                parametros = {'centro': centro, 'raio': raio}
                self.area_desenho.adicionar_pixels(pixels, "Círculo", parametros)
            except ValueError:
                print("Erro: As coordenadas do centro e o raio devem ser números inteiros.")

        elif evento.ui_element == painel.elementos_bezier.get('botao'):
            try:
                pontos = [ (int(painel.elementos_bezier[f'p{i}_x'].get_text()), int(painel.elementos_bezier[f'p{i}_y'].get_text())) for i in range(4) ]
                pixels = rasterizar_curva_bezier(*pontos)
                parametros = {f'p{i}': p for i, p in enumerate(pontos)}
                self.area_desenho.adicionar_pixels(pixels, "Curva de Bézier", parametros)
            except ValueError:
                print("Erro: As coordenadas dos pontos de controle devem ser números inteiros.")
        
        elif evento.ui_element == painel.elementos_elipse.get('botao'):
            try:
                centro = (int(painel.elementos_elipse['centro_x'].get_text()), int(painel.elementos_elipse['centro_y'].get_text()))
                rx = int(painel.elementos_elipse['rx'].get_text())
                ry = int(painel.elementos_elipse['ry'].get_text())
                pixels = calcular_elipse(centro, rx, ry)
                parametros = {'centro': centro, 'rx': rx, 'ry': ry}
                self.area_desenho.adicionar_pixels(pixels, "Elipse", parametros)
            except ValueError:
                print("Erro: As coordenadas do centro e os raios devem ser números inteiros.")

        elif evento.ui_element == painel.elementos_polilinha.get('botao'):
            try:
                texto_pontos = painel.elementos_polilinha['entrada_pontos'].get_text()
                # Parse "x1,y1; x2,y2; ..."
                pontos_str = [p.strip() for p in texto_pontos.split(';')]
                pontos = []
                for ponto_str in pontos_str:
                    if not ponto_str: continue
                    x_str, y_str = ponto_str.split(',')
                    pontos.append((int(x_str), int(y_str)))
                
                if len(pontos) < 2:
                    print("Erro: A polilinha precisa de pelo menos 2 pontos.")
                    return

                pixels = rasterizar_polilinha(pontos)
                parametros = {'pontos': pontos}
                self.area_desenho.adicionar_pixels(pixels, "Polilinha", parametros)
            except ValueError:
                print("Erro: Formato dos pontos inválido. Use 'x1,y1; x2,y2; ...'")
        
        # --- Botões de Definição de Ponto ---
        elif evento.ui_element == painel.elementos_linha.get('btn_p1'): self.proximo_clique_define = ('linha', 'p1')
        elif evento.ui_element == painel.elementos_linha.get('btn_p2'): self.proximo_clique_define = ('linha', 'p2')
        elif evento.ui_element == painel.elementos_circulo.get('btn_centro'): self.proximo_clique_define = ('circulo', 'centro')
        elif evento.ui_element == painel.elementos_elipse.get('btn_centro'): self.proximo_clique_define = ('elipse', 'centro')
        elif evento.ui_element == painel.elementos_bezier.get('btn_p0'): self.proximo_clique_define = ('bezier', 'p0')
        elif evento.ui_element == painel.elementos_bezier.get('btn_p1'): self.proximo_clique_define = ('bezier', 'p1')
        elif evento.ui_element == painel.elementos_bezier.get('btn_p2'): self.proximo_clique_define = ('bezier', 'p2')
        elif evento.ui_element == painel.elementos_bezier.get('btn_p3'): self.proximo_clique_define = ('bezier', 'p3')

        # --- Ações Gerais ---
        elif evento.ui_element == painel.botao_limpar: self.area_desenho.limpar_pixels()
        elif evento.ui_element == painel.botao_desfazer: self.area_desenho.desfazer_ultimo_desenho()
        elif evento.ui_element == painel.botao_excluir_selecao:
            indice = self.area_desenho.obter_indice_selecionado()
            if indice is not None: self.area_desenho.remover_desenho_indice(indice)
