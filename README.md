# Graphics Algorithms Suite

Trabalho final da disciplina de Computação Gráfica com o professor Bianchi Serique Meiguins. 

Aplicação didática (Python + pygame-ce + pygame_gui) para estudar e demonstrar algoritmos clássicos de Computação Gráfica em uma grade cartesiana interativa. O foco é visualizar passo a passo desenho de linhas e curvas, preenchimentos, recorte de linhas/polígonos, transformações geométricas e projeções 3D — com interface amigável e comentários no código que servem como roteiro de apresentação/estudo.

## Explicação no youtube: 
![Playlist Trabalho final de computação gráfica](https://www.youtube.com/playlist?list=PLeUnahGUNxlTmsYc6Vz_gTyLftrJT5kj8) 

## 🎯 Objetivo central
- Fornecer um ambiente visual para praticar algoritmos de rasterização, preenchimento, recorte, transformações 2D e projeções 3D;
- Ajudar no entendimento por meio de uma grade (grid) e histórico de desenhos, permitindo refazer/inspecionar resultados;
- Servir de material de apoio para aulas, trabalhos e apresentações (código extensivamente comentado).

## ✨ Principais recursos
- Linhas (Bresenham) e polilinhas (por pontos ou pré-definidas);
- Círculo e elipse (ponto médio);
- Curvas de Bézier;
- Preenchimentos: Flood Fill, Scanline (simples e múltiplo);
- Recorte: Cohen–Sutherland (linhas retangulares) e Sutherland–Hodgman (polígonos/convexos);
- Transformações: translação, escala (com ponto fixo), rotação;
- Projeções 3D: Ortogonal, Perspectiva, Cavalier e Cabinet (com painel dedicado);
- Histórico de ações/desenhos com rótulos e reexibição na grade.

## 🔧 Requisitos
- Python 3.11+ (recomendado)
- Dependências Python (listadas em `requirements.txt`):
  - `pygame-ce`
  - `pygame_gui`

## 🚀 Instalação
No Linux (shell padrão zsh):

```sh
# Dentro da pasta do projeto
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> Dica: para sair do ambiente virtual depois: `deactivate`.

## ▶️ Como executar

```sh
# Com o ambiente virtual ativo
python main.py
```

Ao iniciar, a janela principal exibirá a grade de desenho e o painel de controles. Use o dropdown de figura para escolher o que desenhar e preencha os parâmetros conforme necessário.

### Projeções 3D
- No dropdown principal, selecione “Projeções 3D”.
- Clique no botão “Coordenadas 3D” para abrir o painel dedicado.
- Escolha o sólido (Cubo ou Poliedro personalizado) e o tipo de projeção.
- Para Cavalier/Cabinet, informe o ângulo; para Perspectiva, informe o ponto do observador (X, Y, Z).
- Em “Poliedro (Vértices)”, informe:
  - Vértices: `x,y,z; x,y,z; ...`
  - Arestas: `i,j; k,l; ...` (índices dos vértices começando em 0)
- Pressione “Desenhar Projeção”. A saída é um único objeto polilinha que percorre todas as arestas projetadas.

## 🗂️ Estrutura do projeto (resumo)
- `main.py`: ponto de entrada; inicia a aplicação e o loop principal.
- `interface/`: UI e renderização da grade
  - `app.py`: loop de eventos, roteamento de ações e integração com algoritmos
  - `area_desenho.py`: desenho da grade, histórico e rasterização para pixels
  - `painel_controle.py`: controles principais (figuras, transformações, preenchimento, recorte)
  - `painel_projecoes.py`: painel para projeções 3D (parâmetros e acionamento)
- `algoritmos/`: implementações de desenho, preenchimento, recorte, transformações e projeções (código comentado)
- `utils/`: utilidades e geometria de apoio
- `theme.json`: tema visual do pygame_gui

## ❓Dúvidas e problemas comuns
- Caso o pygame não abra a janela, verifique se o ambiente virtual está ativo e as dependências foram instaladas corretamente.
- Em ambientes minimalistas, pode ser necessário instalar bibliotecas de sistema do SDL/OpenGL (varia por distro). Mantenha seu sistema atualizado e consulte a documentação do pygame-ce se necessário.

---

