from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any
from datetime import datetime

@dataclass
class DesenhoHistorico:
    """Representa um único objeto desenhado, definido por seus parâmetros."""
    tipo: str
    parametros: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    # O campo 'pixels' foi removido. A rasterização agora é feita sob demanda.

class Historico:
    def __init__(self):
        self.desenhos: List[DesenhoHistorico] = []
    
    def adicionar_desenho(self, tipo: str, parametros: Dict[str, Any]):
        """Adiciona um novo desenho ao histórico, baseado em seus parâmetros."""
        desenho = DesenhoHistorico(
            tipo=tipo,
            parametros=parametros
        )
        self.desenhos.append(desenho)
    
    def limpar_historico(self):
        self.desenhos.clear()
    
    def obter_desenhos(self) -> List[DesenhoHistorico]:
        return self.desenhos
    
    def desfazer_ultimo_desenho(self):
        """Remove o último desenho do histórico."""
        if not self.desenhos:
            return
        self.desenhos.pop()

    def remover_por_indice(self, indice: int):
        """Remove o desenho pelo índice (0 = mais antigo)."""
        if 0 <= indice < len(self.desenhos):
            self.desenhos.pop(indice)
