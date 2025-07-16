from abc import ABC, abstractmethod


class Writable(ABC):
    @abstractmethod
    def write(self):
        pass


class Readable(ABC):
    @abstractmethod
    def read(self):
        pass
