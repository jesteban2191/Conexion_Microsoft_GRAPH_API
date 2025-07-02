from abc import ABC, abstractmethod

class InitializerInterface(ABC):

    @abstractmethod
    def InitializeSharepoint(self):
        pass