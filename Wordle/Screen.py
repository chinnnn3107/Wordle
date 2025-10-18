from abc import ABC, abstractmethod

class Screen(ABC):
    @abstractmethod
    def handle(self, event): pass
    
    @abstractmethod
    def update(self): pass
    
    @abstractmethod
    def render(self): pass




