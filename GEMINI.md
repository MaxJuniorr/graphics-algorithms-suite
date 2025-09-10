# Visão Geral do Projeto

Este é um aplicativo de desktop em Python, desenvolvido como uma suíte para aprendizado e visualização de algoritmos clássicos de computação gráfica. A interface, construída com **Pygame** e **Pygame_GUI**, permite que os usuários selecionem algoritmos, ajustem parâmetros geométricos, apliquem transformações 2D e vejam os resultados renderizados em tempo real em uma tela baseada em grade.

O projeto foi estruturado com foco em **modularidade** e um fluxo de dados reativo, separando claramente a lógica dos algoritmos, o gerenciamento da interface e as utilidades de suporte. Uma característica central da arquitetura é que os objetos não são armazenados como pixels, mas como **representações paramétricas**, sendo rasterizados sob demanda a cada quadro.

---

# Arquitetura e Componentes

A aplicação é dividida em três pacotes principais: `interface`, `algoritmos` e `utils`.

### 1. Interface (`interface/`)

Responsável por toda a experiência do usuário.

- **`app.py` (`Aplicacao`)**: É o coração da aplicação. Orquestra os outros componentes, gerencia o loop de eventos principal do Pygame, processa eventos da UI e coordena as atualizações entre o painel de controle e a área de desenho. É aqui que a lógica de manipulação de eventos para desenho e transformações é implementada.

- **`area_desenho.py` (`AreaDesenho`)**: Gerencia a "tela" onde os algoritmos são visualizados. Suas responsabilidades são:
    - Desenhar a grade de fundo e os eixos.
    - Mapear as coordenadas da grade (ex: 1, 2) para as coordenadas da tela em pixels.
    - **Rasterização sob Demanda**: A cada quadro, itera sobre os objetos no histórico e chama a função de algoritmo apropriada para obter os pixels.
    - Renderizar os pixels na tela, destacando o objeto selecionado.
    - Gerenciar o estado dos desenhos através da classe `Historico`.

- **`painel_controle.py` (`PainelControle`)**: Constrói e gerencia todos os widgets do painel lateral. A interface é dividida em seções lógicas:
    - **Configuração da Grade**: Entradas para a resolução da grade.
    - **Seleção de Figura**: Um menu dropdown para alternar entre os algoritmos disponíveis.
    - **Parâmetros de Algoritmos**: Campos de texto dinâmicos para os parâmetros do algoritmo selecionado. Inclui botões "Def" para definir coordenadas clicando na tela.
    - **Transformações 2D**: Seção para aplicar translação, escala e rotação no objeto selecionado no histórico.
    - **Histórico de Desenhos**: Uma lista que exibe cada forma desenhada. Clicar em um item o seleciona e o destaca na área de desenho.
    - **Ações Gerais**: Botões para `Limpar Tela`, `Desfazer` e `Excluir` a forma selecionada.

### 2. Algoritmos (`algoritmos/`)

Contém a lógica pura e matemática de cada algoritmo. As funções recebem parâmetros numéricos e retornam uma lista de coordenadas `(x, y)`.

**Algoritmos Implementados:**
- **`bresenham.py`**: `calcular_linha_bresenham(p1, p2)` - Rasteriza uma linha.
- **`circulo_elipse.py`**:
    - `calcular_circulo(centro, raio)`: Rasteriza um círculo (Ponto Médio).
    - `calcular_elipse(centro, rx, ry)`: Rasteriza uma elipse (Ponto Médio).
- **`curvas_bezier.py`**: `rasterizar_curva_bezier(p0, p1, p2, p3)` - Gera uma curva de Bézier cúbica conectando pontos amostrados com Bresenham.
- **`polilinha.py`**: `rasterizar_polilinha(pontos)` - Conecta uma sequência de pontos com o algoritmo de Bresenham.
- **`transformacoes.py`**:
    - `transladar(pontos, tx, ty)`: Aplica translação a uma lista de vértices.
    - `escalar(pontos, sx, sy, ponto_fixo)`: Aplica escala em relação a um ponto fixo.
    - `rotacionar(pontos, angulo, pivo)`: Aplica rotação em torno de um pivô.

**Algoritmos Planejados (Arquivos Vazios):**
- `preenchimento.py`
- `projecoes.py`
- `recorte.py`

### 3. Utilitários (`utils/`)

- **`historico.py`**: Fornece a espinha dorsal para o gerenciamento de estado.
    - `DesenhoHistorico` (dataclass): Estrutura que armazena os dados de uma forma: seu `tipo` (ex: "Círculo") e seus `parametros` (ex: `{'centro': (0,0), 'raio': 20}`). **Não armazena pixels**.
    - `Historico` (classe): Gerencia uma lista de objetos `DesenhoHistorico`.

---

# Fluxos de Interação

## Fluxo de Desenho

1.  O usuário insere valores no `PainelControle` (ex: raio do círculo) e clica em "Desenhar".
2.  O `Aplicacao` detecta o evento, lê os parâmetros da UI.
3.  Chama `area_desenho.adicionar_forma()`, passando o tipo de forma e seus parâmetros (ex: "Círculo", `{'centro':(0,0), 'raio':20}`).
4.  A `AreaDesenho` cria um `DesenhoHistorico` e o adiciona à sua instância de `Historico`.
5.  No próximo ciclo de desenho, `AreaDesenho.desenhar()` itera pelo histórico. Para cada `DesenhoHistorico`, ele chama o método `rasterizar_desenho`.
6.  `rasterizar_desenho` atua como um despachante: com base no `tipo` do desenho, ele chama a função de algoritmo correspondente (ex: `calcular_circulo`), passando os `parametros`.
7.  O algoritmo retorna a lista de pixels, que é finalmente renderizada na tela.

## Fluxo de Transformação

1.  O usuário seleciona um objeto na lista de **Histórico de Desenhos**.
2.  O `Aplicacao` registra o índice do objeto selecionado. `AreaDesenho` usa esse índice para destacar o objeto correto.
3.  O usuário insere os parâmetros de transformação (ex: ângulo de rotação) e clica em "Aplicar".
4.  O `Aplicacao` identifica o `DesenhoHistorico` selecionado.
5.  **Lógica de Aplicação**:
    - Se o objeto é definido por vértices (`Linha`, `Polilinha`, `Curva de Bézier`), o `Aplicacao` extrai seus pontos, chama a função de transformação apropriada (`transladar`, `rotacionar`, etc.) e atualiza os parâmetros do `DesenhoHistorico` com os novos pontos.
    - Se o objeto é paramétrico (`Círculo`, `Elipse`) e a transformação não pode ser aplicada diretamente aos parâmetros (como rotação ou escala não uniforme), o `Aplicacao` primeiro **converte o objeto para uma Polilinha** (`_converter_para_polilinha`), substituindo o objeto original no histórico. Em seguida, aplica a transformação aos vértices da nova polilinha.
6.  Como a tela é redesenhada a cada quadro, as mudanças são refletidas instantaneamente.

---

# Como Adicionar um Novo Algoritmo

1.  **Criar a Lógica**: Crie um novo arquivo em `algoritmos/` (ex: `meu_algoritmo.py`). Nele, defina uma função que receba os parâmetros necessários e retorne uma lista de pixels `[(x1, y1), ...]`.
2.  **Integrar na Interface (`painel_controle.py`)**:
    - Adicione o nome do seu algoritmo à lista de opções do `UIDropDownMenu`.
    - Crie os widgets para os parâmetros do seu algoritmo e agrupe-os em um dicionário.
    - Adicione o dicionário ao mapeamento no método `mostrar_elementos_figura`.
3.  **Adicionar o Gatilho do Evento (`app.py`)**:
    - No método `manipular_eventos_ui`, adicione um novo bloco `elif` para o evento de clique do seu novo botão.
    - Neste bloco, leia os valores da UI e chame `self.area_desenho.adicionar_forma("Meu Algoritmo", {'param1': valor1, ...})`.
4.  **Adicionar o Ramo de Rasterização (`area_desenho.py`)**:
    - Importe sua nova função: `from algoritmos.meu_algoritmo import minha_funcao`.
    - No método `rasterizar_desenho`, adicione um novo bloco `elif tipo == "Meu Algoritmo":` que chama sua função com os parâmetros do desenho.