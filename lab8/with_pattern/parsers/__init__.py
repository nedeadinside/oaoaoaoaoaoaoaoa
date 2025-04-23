from abc import ABCMeta, abstractmethod

class BookIterator(metaclass=ABCMeta):
    """Абстрактный базовый класс для итераторов"""

    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def __next__(self):
        pass
    
    
class AbstractFormatter(metaclass=ABCMeta):
    @abstractmethod
    def parse(self, path):
        pass

    @abstractmethod
    def get_icon_from_cover(self, cover_image):
        pass