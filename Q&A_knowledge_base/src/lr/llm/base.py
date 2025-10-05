from abc import ABC, abstractmethod
from typing import List, Dict

class Embeddings(ABC):
    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]: ...

class Chat(ABC):
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]]) -> str: ...
