import pygame
import pygame_gui

class PainelProjecoes(pygame_gui.elements.UIWindow):
    def __init__(self, ui_manager, largura_canvas):
        super().__init__(
            rect=pygame.Rect((largura_canvas, 50), (400, 600)), # Aumentar altura da janela
            manager=ui_manager,
            window_display_title='Painel de Projeções 3D',
            object_id='#painel_projecoes'
        )

        self.ui_manager = ui_manager

        # --- Controles ---
        y_cursor = 20
        
        # Seleção de Sólido
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, y_cursor), (150, 20)),
            text='Sólido 3D:',
            manager=self.ui_manager,
            container=self
        )
        y_cursor += 25
        self.seletor_solido = pygame_gui.elements.UIDropDownMenu(
            options_list=['Cubo', 'Poliedro (Vértices)'],
            starting_option='Cubo',
            relative_rect=pygame.Rect((10, y_cursor), (150, 30)),
            manager=self.ui_manager,
            container=self
        )

        # Seleção de Projeção
        y_cursor += 45
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, y_cursor), (150, 20)),
            text='Tipo de Projeção:',
            manager=self.ui_manager,
            container=self
        )
        y_cursor += 25
        self.seletor_projecao = pygame_gui.elements.UIDropDownMenu(
            options_list=['Ortogonal', 'Perspectiva', 'Cavalier', 'Cabinet'],
            starting_option='Ortogonal',
            relative_rect=pygame.Rect((10, y_cursor), (150, 30)),
            manager=self.ui_manager,
            container=self
        )

        # --- Ângulo para Projeções Oblíquas ---
        y_cursor += 45
        self.label_angulo_obliquo = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, y_cursor), (280, 20)),
            text='Ângulo (para Cavalier/Cabinet):',
            manager=self.ui_manager,
            container=self
        )
        y_cursor += 25
        self.entrada_angulo_obliquo = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((10, y_cursor), (100, 30)),
            manager=self.ui_manager,
            container=self
        )
        self.entrada_angulo_obliquo.set_text('45')

        # --- Ponto de Observação para Perspectiva ---
        y_cursor += 45
        self.label_observador = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, y_cursor), (360, 20)),
            text='Ponto de Observação (para Perspectiva):',
            manager=self.ui_manager,
            container=self
        )
        y_cursor += 25
        # Coordenada X
        self.label_obs_x = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((10, y_cursor), (20, 30)), text='X:', manager=ui_manager, container=self)
        self.entrada_obs_x = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((35, y_cursor), (80, 30)), manager=ui_manager, container=self)
        # Coordenada Y
        self.label_obs_y = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((125, y_cursor), (20, 30)), text='Y:', manager=ui_manager, container=self)
        self.entrada_obs_y = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((150, y_cursor), (80, 30)), manager=ui_manager, container=self)
        # Coordenada Z
        self.label_obs_z = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((240, y_cursor), (20, 30)), text='Z:', manager=ui_manager, container=self)
        self.entrada_obs_z = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((265, y_cursor), (80, 30)), manager=ui_manager, container=self)
        
        self.entrada_obs_x.set_text('0')
        self.entrada_obs_y.set_text('0')
        self.entrada_obs_z.set_text('-100')

        # --- Entradas para Poliedro Personalizado (escondidas por padrão) ---
        y_cursor += 45
        self.label_vertices = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, y_cursor), (360, 20)),
            text='Vértices (x,y,z; ...)',
            manager=self.ui_manager,
            container=self
        )
        y_cursor += 25
        self.entrada_vertices = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((10, y_cursor), (360, 30)),
            manager=self.ui_manager,
            container=self
        )
        y_cursor += 40
        self.label_arestas = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, y_cursor), (360, 20)),
            text='Arestas (índice1,índice2; ...)',
            manager=self.ui_manager,
            container=self
        )
        y_cursor += 25
        self.entrada_arestas = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((10, y_cursor), (360, 30)),
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
            relative_rect=pygame.Rect((10, self.get_container().get_size()[1] - 60), (150, 40)),
            text='Desenhar Projeção',
            manager=self.ui_manager,
            container=self,
            object_id='#desenhar_projecao'
        )

        self.atualizar_visibilidade_controles()

    def atualizar_visibilidade_controles(self):
        """ Mostra/esconde campos com base nas seleções de dropdown. """
        if not self.alive():
            return
            
        tipo_solido = self.seletor_solido.selected_option[0]
        tipo_projecao = self.seletor_projecao.selected_option[0]

        # Controles do poliedro personalizado
        visivel_poliedro = (tipo_solido == 'Poliedro (Vértices)')
        self.label_vertices.visible = visivel_poliedro
        self.entrada_vertices.visible = visivel_poliedro
        self.label_arestas.visible = visivel_poliedro
        self.entrada_arestas.visible = visivel_poliedro

        # Controles de perspectiva
        visivel_perspectiva = (tipo_projecao == 'Perspectiva')
        self.label_observador.visible = visivel_perspectiva
        self.label_obs_x.visible = visivel_perspectiva
        self.entrada_obs_x.visible = visivel_perspectiva
        self.label_obs_y.visible = visivel_perspectiva
        self.entrada_obs_y.visible = visivel_perspectiva
        self.label_obs_z.visible = visivel_perspectiva
        self.entrada_obs_z.visible = visivel_perspectiva

        # Controles de projeção oblíqua
        visivel_obliquo = tipo_projecao in ['Cavalier', 'Cabinet']
        self.label_angulo_obliquo.visible = visivel_obliquo
        self.entrada_angulo_obliquo.visible = visivel_obliquo

        self.rebuild()
