from dataclasses import dataclass
from typing import List, Tuple, Dict
from datetime import datetime

@dataclass
class DesenhoHistorico:
    tipo: str  # Tipo do desenho (Linha, Círculo, etc)
    parametros: Dict  # Parâmetros usados (coordenadas, raio, etc)
    pixels: List[Tuple[int, int]]  # Lista de pixels do desenho
    timestamp: datetime  # Momento em que foi desenhado

class Historico:
    def __init__(self):
        self.desenhos: List[DesenhoHistorico] = []
    
    def adicionar_desenho(self, tipo: str, parametros: Dict, pixels: List[Tuple[int, int]]):
        desenho = DesenhoHistorico(
            tipo=tipo,
            parametros=parametros,
            pixels=pixels,
            timestamp=datetime.now()
        )
        self.desenhos.append(desenho)
    
    def limpar_historico(self):
        self.desenhos.clear()
    
    def obter_desenhos(self) -> List[DesenhoHistorico]:
        return self.desenhos
    
    def desfazer_ultimo_desenho(self) -> List[Tuple[int, int]]:
        """Remove o último desenho do histórico e retorna todos os pixels que devem permanecer visíveis."""
        if not self.desenhos:
            return []
        
        self.desenhos.pop()  # Remove o último desenho
        
        # Retorna todos os pixels dos desenhos restantes
        pixels = []
        for desenho in self.desenhos:
            pixels.extend(desenho.pixels)
        return pixels
