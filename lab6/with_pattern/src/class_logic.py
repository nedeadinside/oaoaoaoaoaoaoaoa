from abc import abstractmethod, ABCMeta
from typing import List, Dict
import pysrt
import os

from dotenv import load_dotenv, find_dotenv
find_dotenv('.env')
load_dotenv()

MOVIES_TYPE = os.getenv("MOVIES_TYPE")
SUBTITLES_TYPE = os.getenv("SUBTITLES_TYPE")

# Абстрактные классы
class AbstractMovie(metaclass=ABCMeta):
    @abstractmethod
    def get_video_path(self) -> str:
        raise NotImplementedError


class AbstractSubtitles(metaclass=ABCMeta):
    @abstractmethod
    def get_subtitles(self) -> object:
        raise NotImplementedError


class AbstractFactory(metaclass=ABCMeta):
    @abstractmethod
    def create_movie(self, movie_name: str) -> AbstractMovie:
        raise NotImplementedError

    @abstractmethod
    def create_subtitles(self, movie_name: str) -> AbstractSubtitles:
        raise NotImplementedError


class EnglishMovie(AbstractMovie):
    _lang = 'en'
    def __init__(self, movie_name: str, movies_path: str):
        self.movie_name = movie_name
        self.path = os.path.join(movies_path, self._lang, f"{movie_name}.{MOVIES_TYPE}")
        
    def get_video_path(self) -> str:
        return self.path


class EnglishSubtitles(AbstractSubtitles):
    _lang = 'en'
    def __init__(self, movie_name: str, movies_path: str):
        self.movie_name = movie_name
        self.path = os.path.join(movies_path, self._lang, f"{movie_name}.{SUBTITLES_TYPE}")
        self._subs = None

    def get_subtitles(self) -> object:
        if self._subs is None:
            try:
                self._subs = pysrt.open(self.path, encoding='utf-8')
            except Exception:
                return None
        return self._subs


class EnglishFactory(AbstractFactory):
    def __init__(self, movies_path: str):
        self.movies_path = movies_path
        
    def create_movie(self, movie_name: str) -> AbstractMovie:
        return EnglishMovie(movie_name, self.movies_path)

    def create_subtitles(self, movie_name: str) -> AbstractSubtitles:
        return EnglishSubtitles(movie_name, self.movies_path)


class RussianMovie(AbstractMovie):
    _lang = 'ru'
    def __init__(self, movie_name: str, movies_path: str):
        self.movie_name = movie_name
        self.path = os.path.join(movies_path, self._lang, f"{movie_name}.{MOVIES_TYPE}")

    def get_video_path(self) -> str:
        return self.path


class RussianSubtitles(AbstractSubtitles):
    _lang = 'ru'
    def __init__(self, movie_name: str, movies_path: str):
        self.movie_name = movie_name
        self.path = os.path.join(movies_path, self._lang, f"{movie_name}.{SUBTITLES_TYPE}")
        self._subs = None

    def get_subtitles(self) -> object:
        if self._subs is None:
            try:
                with open(self.path, 'r', encoding='cp1251') as file:
                    content = file.read()
                self._subs = pysrt.from_string(content)
            except Exception as e:
                return None
        return self._subs


class RussianFactory(AbstractFactory):
    def __init__(self, movies_path: str):
        self.movies_path = movies_path
        
    def create_movie(self, movie_name: str) -> RussianMovie:
        return RussianMovie(movie_name, self.movies_path)

    def create_subtitles(self, movie_name: str) -> RussianSubtitles:
        return RussianSubtitles(movie_name, self.movies_path)
    
    
class MovieManager:
    def __init__(self, path: str):
        self._movies_dir = path
        self.factories: Dict[str, AbstractFactory] = {
            "en": EnglishFactory(path),
            "ru": RussianFactory(path)
        }

    def get_available_movies(self) -> List[str]:
        movie_names = set()
        for lang in self.factories.keys():
            movie_dir = os.path.join(self._movies_dir, lang)
            if os.path.exists(movie_dir):
                for filename in os.listdir(movie_dir):
                    if filename.endswith(f".{MOVIES_TYPE}"):
                        movie_name = filename.split('.')[0]
                        movie_names.add(movie_name)
        return list(movie_names)


    def get_available_languages(self, movie_name: str) -> List[str]:
        languages = []
        for lang, _ in self.factories.items():
            movie_path = os.path.join(self._movies_dir, lang, f"{movie_name}.{MOVIES_TYPE}")
            if os.path.exists(movie_path):
                languages.append(lang)
        return languages


    def get_factory(self, language: str) -> AbstractFactory:
        return self.factories.get(language, None)


    def create_movie(self, movie_name: str, language: str) -> AbstractMovie:
        factory = self.get_factory(language)
        return factory.create_movie(movie_name)


    def create_subtitles(self, movie_name: str, language: str) -> AbstractSubtitles:
        factory = self.get_factory(language)
        return factory.create_subtitles(movie_name)