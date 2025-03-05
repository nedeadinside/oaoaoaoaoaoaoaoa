from dataclasses import dataclass
import os
import pysrt


@dataclass
class Movie:
    name: str
    language: str
    video_path: str
    subtitle_path: str


class MovieManager:
    def __init__(self, base_dir):
        self._base_dir = base_dir
        self._movies: list[Movie] = self._scan_movies()

    def _scan_movies(self) -> list[Movie]: 
        movies = []
        for lang in os.listdir(self._base_dir):
            lang_path = os.path.join(self._base_dir, lang)
            if not os.path.isdir(lang_path):
                continue
            for movie_folder in os.listdir(lang_path):
                movie_path = os.path.join(lang_path, movie_folder)
                if not os.path.isdir(movie_path):
                    continue
                
                video_file = f"{movie_folder}.mp4"
                sub_file = f"{movie_folder}.srt"
                video_path = os.path.join(movie_path, video_file)
                sub_path = os.path.join(movie_path, sub_file)
                
                movie = Movie(movie_folder, lang, video_path, sub_path)
                movies.append(movie)
        
        return movies

    def get_movie_list(self):
        movie_names = set()
        for movie in self._movies:
            movie_names.add(movie.name)
        return list(movie_names)

    def get_languages(self, movie_name):
        languages = []
        for movie in self._movies:
            if movie.name == movie_name:
                languages.append(movie.language)
        return languages

    def get_video_path(self, movie_name, language):
        for movie in self._movies:
            if movie.name == movie_name and movie.language == language:
                return movie.video_path
        return None

    def load_subtitles(self, movie_name, language):
        for movie in self._movies:
            if movie.name == movie_name and movie.language == language:
                try:
                    return pysrt.open(movie.subtitle_path, encoding="utf-8")
                except:
                    return None
        return None