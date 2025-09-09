# main.py
from interface.app import Aplicacao

if __name__ == "__main__":
    print("Iniciando a aplicação de Computação Gráfica...")
    # Define a resolução inicial da grade
    app = Aplicacao(largura_grid_inicial=80, altura_grid_inicial=80)
    app.executar()

