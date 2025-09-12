# Visão Geral do Projeto

Este é um aplicativo de desktop em Python, desenvolvido como uma suíte para aprendizado e visualização de algoritmos clássicos de computação gráfica. A interface, construída com **Pygame** e **Pygame_GUI**, permite que os usuários selecionem algoritmos, ajustem parâmetros geométricos e vejam os resultados renderizados em tempo real em uma tela baseada em grade.

O projeto foi estruturado com foco em **modularidade**, separando claramente a lógica dos algoritmos, o gerenciamento da interface e as utilidades de suporte.

# Arquitetura e Componentes

A aplicação é dividida em três pacotes principais: `interface`, `algoritmos` e `utils`.

### 1. Interface (`interface/`)

Responsável por toda a experiência do usuário. A lógica da UI é distribuída em componentes especializados:

- **`app.py` (`Aplicacao`)**: É o coração da aplicação. Orquestra os outros componentes, gerencia o loop de eventos principal do Pygame, processa eventos da UI e coordena as atualizações entre o painel de controle e a área de desenho.

- **`area_desenho.py` (`AreaDesenho`)**: Gerencia a "tela" onde os algoritmos são visualizados. Suas responsabilidades são:
    - Desenhar a grade de fundo.
    - Mapear as coordenadas da grade (ex: 1, 2) para as coordenadas da tela em pixels.
    - Renderizar os pixels retornados pelos algoritmos.
    - Gerenciar o estado dos desenhos através da classe `Historico`, permitindo que formas sejam destacadas, removidas ou que ações sejam desfeitas.
    - Desenhar uma janela de recorte retangular na tela quando um algoritmo de recorte é ativado.

- **`painel_controle.py` (`PainelControle`)**: Constrói e gerencia todos os widgets do painel lateral. A interface é dividida em seções lógicas:
    - **Configuração da Grade**: Entradas para a resolução da grade (`Largura`, `Altura`).
    - **Seleção de Figura**: Um menu dropdown para alternar entre os algoritmos disponíveis (`Linha`, `Círculo`, `Elipse`, `Curva de Bézier`, `Polilinha`, `Projeções 3D`). A seleção aqui controla quais campos de entrada são exibidos abaixo.
    - **Parâmetros de Algoritmos**: Campos de texto que aparecem dinamicamente para inserir os parâmetros necessários para o algoritmo selecionado (coordenadas de pontos, raios, etc.).
    - **Histórico de Desenhos**: Uma lista que exibe cada forma desenhada. Clicar em um item o seleciona e o destaca na área de desenho.
    - **Ações Gerais**: Botões para `Limpar Tela`, `Desfazer` a última ação e `Excluir` a forma selecionada no histórico.
    - **Transformações 2D**: Controles para aplicar translação, escala e rotação ao objeto selecionado.
    - **Preenchimento**: Botões para aplicar algoritmos de preenchimento como `Scanline` e `Flood Fill`.
    - **Recorte**: Uma nova seção que aparece dinamicamente quando uma **Linha** ou **Polilinha** é selecionada no histórico. Permite ao usuário definir uma janela de recorte (xmin, ymin, xmax, ymax) e aplicar o algoritmo de recorte correspondente.

- **`painel_projecoes.py` (`PainelProjecoes`)**: Uma janela flutuante que permite ao usuário:
    - Selecionar um sólido 3D (Cubo padrão ou Poliedro customizado).
    - Definir vértices e arestas para um poliedro customizado.
    - Escolher um tipo de projeção (Ortogonal, Perspectiva, Cavalier, Cabinet).
    - Desenhar a projeção 2D resultante no canvas principal.

### 2. Algoritmos (`algoritmos/`)

Contém a lógica pura e matemática de cada algoritmo. As funções neste pacote são independentes da interface e do Pygame. Elas recebem parâmetros numéricos e retornam uma lista de tuplas de coordenadas `(x, y)` que representam os pixels a serem desenhados.

**Algoritmos Implementados:**
- **`bresenham.py`**: `calcular_linha_bresenham(p1, p2)`
    - Implementa o algoritmo de Bresenham para rasterizar uma linha entre dois pontos com coordenadas inteiras.
- **`circulo_elipse.py`**: 
    - `calcular_circulo(centro, raio)`: Implementa o algoritmo do Ponto Médio para desenhar um círculo.
    - `calcular_elipse(centro, rx, ry)`: Implementa o algoritmo do Ponto Médio para desenhar uma elipse a partir de um centro e dois raios (rx e ry).
- **`curvas_bezier.py`**: `rasterizar_curva_bezier(p0, p1, p2, p3)`
    - Calcula os pontos de uma curva de Bézier cúbica usando a definição paramétrica e, em seguida, utiliza o algoritmo de Bresenham para conectar esses pontos, efetivamente rasterizando a curva.
- **`polilinha.py`**: `rasterizar_polilinha(pontos)`
    - Conecta uma sequência de pontos para formar uma polilinha.
- **`preenchimento.py`**:
    - `preencher_scanline(vertices)`: Preenche um polígono usando o algoritmo de varredura (Scanline).
    - `preencher_recursao(vertices, seed)`: Preenche uma área usando um algoritmo de preenchimento recursivo (Flood Fill).
    - `preencher_flood_canvas(ocupados, seed, bounds)`: Preenche uma área vazia no canvas.
- **`transformacoes.py`**:
    - `transladar(pontos, tx, ty)`: Translada um conjunto de pontos.
    - `escalar(pontos, sx, sy, ponto_fixo)`: Escala um conjunto de pontos em relação a um ponto fixo.
    - `rotacionar(pontos, angulo, pivo)`: Rotaciona um conjunto de pontos em torno de um pivô.
- **`recorte.py`**:
    - `cohen_sutherland_clip(p1, p2, xmin, ymin, xmax, ymax)`: Implementa o algoritmo de Cohen-Sutherland para recorte de linhas.
    - `sutherland_hodgman_clip(subject_polygon, clip_window)`: Implementa o algoritmo de Sutherland-Hodgman para recorte de polígonos.
- **`projecoes.py`**:
    - `obter_cubo_padrao()`: Retorna os vértices e arestas de um cubo padrão.
    - `projecao_ortogonal(vertices_3d, plano)`: Projeta vértices 3D em um plano 2D.
    - `projecao_cavalier(vertices_3d, angulo_graus)`: Projeção Cavalier.
    - `projecao_cabinet(vertices_3d, angulo_graus)`: Projeção Cabinet.
    - `projecao_perspectiva(vertices_3d, d)`: Projeção em perspectiva.

### 3. Utilitários (`utils/`)

- **`historico.py`**: Fornece a espinha dorsal para o gerenciamento de estado.
    - `DesenhoHistorico` (dataclass): Estrutura que armazena os dados de uma única forma desenhada: seu tipo (ex: "Círculo"), os parâmetros usados e um timestamp.
    - `Historico` (classe): Gerencia uma lista de objetos `DesenhoHistorico`. Expõe métodos para adicionar, remover, limpar e desfazer desenhos, que são consumidos pela `AreaDesenho`.
- **`geometria.py`**: Funções auxiliares de geometria, como `eh_convexo` para validar polígonos.

# Fluxo de Interação (Exemplo com Recorte)

1.  O usuário desenha uma **Linha** ou **Polilinha**.
2.  O usuário clica no item correspondente na lista de **Histórico de Desenhos**. O item é selecionado.
3.  O `PainelControle` detecta a seleção e, como o item é uma Linha/Polilinha, exibe a seção de **Recorte** com os campos `xmin`, `ymin`, `xmax`, `ymax` e o botão "Aplicar".
4.  O usuário preenche os valores da janela de recorte e clica em "Aplicar Recorte".
5.  O `Aplicacao` detecta o evento `UI_BUTTON_PRESSED`.
6.  Ele lê os valores da janela de recorte e os parâmetros da forma selecionada no histórico.
7.  Chama a função apropriada do pacote `algoritmos/recorte.py` (`cohen_sutherland_clip` ou `sutherland_hodgman_clip`).
8.  A função de recorte processa os dados e retorna os novos vértices da forma recortada (ou `None`/lista vazia se foi totalmente descartada).
9.  O `Aplicacao` atualiza os parâmetros do `DesenhoHistorico` original com os novos vértices. Se a forma foi descartada, ela é removida do histórico.
10. Ao mesmo tempo, `Aplicacao` informa à `AreaDesenho` as dimensões da janela de recorte, que passa a desenhar um retângulo vermelho na tela para visualização.
11. No próximo ciclo de desenho, a `AreaDesenho` renderiza a forma com suas novas coordenadas, já recortada.

# Como Adicionar um Novo Algoritmo

1.  **Criar a Lógica**: Crie um novo arquivo em `algoritmos/` (ex: `meu_algoritmo.py`). Nele, defina uma função que receba os parâmetros necessários e retorne uma lista de pixels `[(x1, y1), (x2, y2), ...]`. Inclua uma docstring explicando seu funcionamento.
2.  **Integrar na Interface (`painel_controle.py`)**:
    - Adicione o nome do seu algoritmo à lista de opções do `UIDropDownMenu`.
    - Crie os widgets (labels, campos de texto, botão) para os parâmetros do seu algoritmo, agrupando-os em um dicionário (ex: `self.elementos_meu_algoritmo`).
    - Adicione seu novo dicionário de elementos ao mapeamento no método `mostrar_elementos_figura` para que a UI possa exibi-los.
3.  **Adicionar o Gatilho do Evento (`app.py`)**:
    - Importe sua nova função: `from algoritmos.meu_algoritmo import minha_funcao`.
    - No método `manipular_eventos_ui`, adicione um novo bloco `elif` para o evento de clique do seu novo botão.
    - Neste bloco, leia os valores das suas entradas de UI, chame sua função de algoritmo e passe o resultado para `self.area_desenho.adicionar_forma()`.
