"""
Janela flutuante (UIWindow) dedicada à configuração de projeções 3D.

O objetivo desta classe é isolar todos os controles relacionados a:
- a) Escolha do sólido 3D (Cubo padrão ou Poliedro definido manualmente);
- b) Tipo de projeção (Ortogonal, Perspectiva, Cavalier, Cabinet);
- c) Parâmetros auxiliares por tipo (ângulo para projeções oblíquas e
         ponto do observador para perspectiva);
- d) Campos específicos para um poliedro personalizado (lista de vértices e
         lista de arestas por índices), visíveis somente quando aplicável.

Integração esperada com a aplicação:
- A Aplicação lê as opções selecionadas/valores de texto aqui, chama os
    algoritmos de projeção e, por fim, constrói UMA ÚNICA polilinha que passa
    por todas as arestas projetadas (decisão arquitetural já adotada).
- Esta janela apenas coleta parâmetros e não desenha por conta própria; o botão
    "Desenhar Projeção" serve como gatilho para a Aplicação executar a lógica.

Notas de UX e implementação:
- Campos condicionalmente exibidos: oblíquo (ângulo) e perspectiva (observador),
    além dos campos do poliedro personalizado. O método atualizar_visibilidade_controles
    centraliza esse toggle e chama rebuild() para reajustar o layout quando algo muda.
- Formatos de entrada dos campos de poliedro:
    • Vértices: "x,y,z; x,y,z; ..." (separação por ponto e vírgula entre vértices)
    • Arestas: "i,j; k,l; ..." onde i e j são índices inteiros em 0..n-1 dos vértices
        declarados acima. A validação e parsing são feitos pela Aplicação.
"""

import pygame
import pygame_gui

class PainelProjecoes(pygame_gui.elements.UIWindow):
    def __init__(self, ui_manager, largura_canvas):
        """Constrói a janela e todos os controles.

        Parâmetros
        - ui_manager: pygame_gui.UIManager que gerencia os elementos de UI.
        - largura_canvas: usado para posicionar a janela à direita da área de desenho.

        Layout
        - Usamos um cursor vertical (y_cursor) simples para espaçar os grupos.
        - Labels explicam a função do próximo campo/dropdown.
        """
        super().__init__(
            rect=pygame.Rect((largura_canvas, 50), (400, 600)), # Aumentar altura da janela
            manager=ui_manager,
            window_display_title='Painel de Projeções 3D',
            object_id='#painel_projecoes'
        )

        self.ui_manager = ui_manager

        # --- Controles ---
        # Cursor Y controla a posição vertical acumulada dos widgets.
        y_cursor = 20
        
        # Seleção de Sólido 3D (fonte da geometria):
        # - "Cubo": sólido padrão (coordenadas conhecidas)
        # - "Poliedro (Vértices)": usuário fornece listas de vértices e arestas
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

        # Seleção de Projeção:
        # - Ortogonal: projeção paralela nos planos XY
        # - Perspectiva: depende do ponto do observador (campos X/Y/Z abaixo)
        # - Cavalier/Cabinet: projeções oblíquas; dependem de um ângulo
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
        # Visível apenas em Cavalier/Cabinet; padrão "45" graus.
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
        # Apenas para projeção "Perspectiva"; define o centro de projeção (CoP).
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
        
        # Valores padrão: observador em Z negativo olhando para a origem.
        self.entrada_obs_x.set_text('0')
        self.entrada_obs_y.set_text('0')
        self.entrada_obs_z.set_text('-100')

        # --- Entradas para Poliedro Personalizado (escondidas por padrão) ---
        # Formatos esperados:
        # - Vértices: "x,y,z; x,y,z; ..." (floats/ints). Ex.: "-20,-20,-20; 20,-20,-20; ..."
        # - Arestas: "i,j; k,l; ..." (índices inteiros referenciando os vértices acima).
        # A conversão de string -> estrutura (lista de tuplas/lista de pares) é feita na Aplicação.
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
        # Exemplos iniciais para orientar o usuário (um quadrado no plano Z=-20):
        self.entrada_vertices.set_text('-20,-20,-20; 20,-20,-20; 20,20,-20; -20,20,-20')
        self.entrada_arestas.set_text('0,1; 1,2; 2,3; 3,0')

        # Esconder campos personalizados por padrão (apenas aparece quando "Poliedro" estiver selecionado)
        self.label_vertices.hide()
        self.entrada_vertices.hide()
        self.label_arestas.hide()
        self.entrada_arestas.hide()

        # Botão de Desenho: dispara o processamento de projeção na Aplicação.
        self.botao_desenhar = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, self.get_container().get_size()[1] - 60), (150, 40)),
            text='Desenhar Projeção',
            manager=self.ui_manager,
            container=self,
            object_id='#desenhar_projecao'
        )

        self.atualizar_visibilidade_controles()

    def atualizar_visibilidade_controles(self):
        """Mostra/esconde campos com base nas seleções de dropdown.

        Regra geral:
        - Sólido "Poliedro (Vértices)" → mostrar campos de vértices e arestas.
        - Projeção "Perspectiva" → mostrar grupo do observador (X, Y, Z).
        - Projeções "Cavalier"/"Cabinet" → mostrar campo de ângulo.

        Importante: usamos a propriedade .visible para cada elemento e depois
        chamamos rebuild() para o pygame_gui recalcular o layout.
        """
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

        # Recalcular e reposicionar os elementos após qualquer mudança de visibilidade.
        self.rebuild()
