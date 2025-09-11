import pygame
import pygame_gui

class PainelProjecoes(pygame_gui.elements.UIWindow):
    def __init__(self, ui_manager, largura_canvas):
        super().__init__(
            rect=pygame.Rect((largura_canvas, 50), (400, 500)),
            manager=ui_manager,
            window_display_title='Painel de Projeções 3D',
            object_id='#painel_projecoes'
        )

        self.ui_manager = ui_manager

        # --- Controles ---
        y_inicial = 20
        
        # Seleção de Sólido
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, y_inicial), (150, 20)),
            text='Sólido 3D:',
            manager=self.ui_manager,
            container=self
        )
        self.seletor_solido = pygame_gui.elements.UIDropDownMenu(
            options_list=['Cubo', 'Poliedro (Vértices)'],
            starting_option='Cubo',
            relative_rect=pygame.Rect((10, y_inicial + 25), (150, 30)),
            manager=self.ui_manager,
            container=self
        )

        # Seleção de Projeção
        y_proj = y_inicial + 70
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, y_proj), (150, 20)),
            text='Tipo de Projeção:',
            manager=self.ui_manager,
            container=self
        )
        self.seletor_projecao = pygame_gui.elements.UIDropDownMenu(
            options_list=['Ortogonal', 'Perspectiva', 'Cavalier', 'Cabinet'],
            starting_option='Ortogonal',
            relative_rect=pygame.Rect((10, y_proj + 25), (150, 30)),
            manager=self.ui_manager,
            container=self
        )

        # --- Entradas para Poliedro Personalizado (escondidas por padrão) ---
        y_custom = y_proj + 70
        self.label_vertices = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, y_custom), (360, 20)),
            text='Vértices (x,y,z; ...)',
            manager=self.ui_manager,
            container=self
        )
        self.entrada_vertices = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((10, y_custom + 25), (360, 30)),
            manager=self.ui_manager,
            container=self
        )
        self.label_arestas = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, y_custom + 65), (360, 20)),
            text='Arestas (índice1,índice2; ...)',
            manager=self.ui_manager,
            container=self
        )
        self.entrada_arestas = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((10, y_custom + 90), (360, 30)),
            manager=self.ui_manager,
            container=self
        )
        # Exemplos
        self.entrada_vertices.set_text('-20,-20,-20; 20,-20,-20; 20,20,-20; -20,20,-20')
        self.entrada_arestas.set_text('0,1; 1,2; 2,3; 3,0')

        # Esconder campos personalizados
        self.label_vertices.hide()
        self.entrada_vertices.hide()
        self.label_arestas.hide()
        self.entrada_arestas.hide()

        # Botão de Desenho
        self.botao_desenhar = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, self.get_container().get_size()[1] - 80), (150, 40)),
            text='Desenhar Projeção',
            manager=self.ui_manager,
            container=self,
            object_id='#desenhar_projecao'
        )
