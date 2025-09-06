# Visão Geral do Projeto

Este é um aplicativo de desktop em Python projetado como uma suíte para aprender e visualizar algoritmos clássicos de computação gráfica. A interface permite que os usuários ajustem parâmetros, executem algoritmos e vejam os resultados renderizados em tempo real em uma tela baseada em grade.

A aplicação usa **Pygame** para a janela principal e o desenho, e **Pygame_GUI** para o painel de controle interativo.

---

# Arquitetura e Componentes

A aplicação é dividida em três componentes principais: a **Interface**, os **Algoritmos** e as **Utilitários**.

### 1. Interface (`interface/`)

Este pacote gerencia toda a experiência do usuário.

- **`app.py`**: Contém a classe principal `Aplicacao`, que inicializa o Pygame, gerencia o loop de eventos principal, processa a entrada do usuário e coordena o desenho na tela.
- **Painel de Controle**: Construído dentro de `app.py`, o painel é dividido em seções:
    - **Configuração da Grade**: Entradas para `Largura` e `Altura` da grade de pixels, com um botão "Aplicar Resolução".
    - **Bresenham (Linha)**: Entradas para as coordenadas (x, y) de dois pontos (P1 e P2) e um botão "Desenhar Linha".
    - **Ponto Médio (Círculo)**: Entradas para as coordenadas do `Centro` (x, y) e o `Raio`, com um botão "Desenhar Círculo".
    - **Ações Gerais**: Um botão "Limpar Tela" para limpar os pixels desenhados.
- **Área de Desenho**: Uma superfície do Pygame onde uma grade é desenhada. Os algoritmos não desenham pixels diretamente; em vez disso, eles retornam uma lista de coordenadas `(x, y)` que a classe `Aplicacao` então renderiza na grade.

### 2. Algoritmos (`algoritmos/`)

Este pacote contém a lógica pura para cada algoritmo gráfico. Cada arquivo implementa uma função que recebe parâmetros geométricos (pontos, raio, etc.) e retorna uma lista de tuplas de coordenadas `(x, y)` para desenhar.

**Algoritmos Implementados:**
- **`bresenham.py`**:
    - `calcular_linha_bresenham(ponto_inicial, ponto_final)`: Retorna os pixels para uma linha entre dois pontos.
- **`circulo_elipse.py`**:
    - `calcular_circulo(centro, raio)`: Retorna os pixels para um círculo usando o algoritmo do ponto médio.
- **`curvas_bezier.py`**:
    - `rasterizar_curva_bezier(p0, p1, p2, p3, num_segmentos)`: Calcula os pontos de uma curva de Bézier cúbica e os conecta usando o algoritmo de Bresenham para rasterização.

**Algoritmos Planejados (Arquivos Vazios):**
- `preenchimento.py`
- `projecoes.py`
- `recorte.py`
- `transformacoes.py`

### 3. Utilitários (`utils/`)

- **`geometria.py`**: (Atualmente vazio) Destinado a conter funções auxiliares de geometria, como cálculos de distância, manipulação de vetores, etc.

---

# Como Usar

### 1. Instalar Dependências

Certifique-se de ter Python instalado. Em seguida, instale as bibliotecas necessárias:
```bash
pip install -r requirements.txt
```

### 2. Executar a Aplicação

Para iniciar o programa, execute o script `main.py` na raiz do projeto:
```bash
python main.py
```

---

# Convenções de Desenvolvimento

- **Modularidade**: A lógica do algoritmo é estritamente separada da lógica da interface. Funções de algoritmo nunca devem interagir diretamente com o Pygame.
- **Coordenadas**: Os algoritmos operam em um sistema de coordenadas de grade. A classe `Aplicacao` é responsável por traduzir essas coordenadas de grade para as posições de pixel na tela.
- **Idioma**: Comentários de código, nomes de variáveis e texto da interface estão em português.
- **Docstrings**: As funções dos algoritmos incluem docstrings explicando seu propósito, argumentos e o que retornam.

### Como Adicionar um Novo Algoritmo

1.  **Criar a Lógica**: Crie um novo arquivo em `algoritmos/` (ex: `meu_algoritmo.py`). Nele, defina uma função que receba os parâmetros necessários e retorne uma lista de pixels `[(x1, y1), (x2, y2), ...]`.
2.  **Integrar na Interface**:
    - Em `interface/app.py`, importe sua nova função: `from algoritmos.meu_algoritmo import minha_funcao`.
    - Na função `construir_interface`, adicione os elementos de UI necessários (entradas de texto, botões) para o seu algoritmo.
3.  **Adicionar o Gatilho do Evento**:
    - Na função `executar`, adicione um `elif` ao bloco de manipulação de eventos `pygame_gui.UI_BUTTON_PRESSED`.
    - Neste bloco, leia os valores das suas novas entradas de UI, chame sua função de algoritmo com esses valores e adicione os pixels retornados à lista `self.pixels_a_desenhar`.