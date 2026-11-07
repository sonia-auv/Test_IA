import csv
import os
from collections.abc import Generator

IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
CSV_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
EXTENSIONS = ['.png', '.jpg', '.jpeg']


class LabeledImage:
    
    def __init__(self, filename:str):
        self.filename = filename
        self.image_path = os.path.join(IMAGES_DIR, filename)
        self.results_path = os.path.join(CSV_DIR, os.path.splitext(filename)[0] + ".csv")


    def load_expected_results(self) -> list[dict[str, str]]:
        with open(self.results_path, newline='', encoding='utf-8-sig') as expected_file:
            return list(csv.DictReader(expected_file))


    @staticmethod
    def load_images() -> Generator['LabeledImage', None, None]:
        for name in os.listdir(IMAGES_DIR):
            if name.lower().endswith(tuple(EXTENSIONS)):
                yield LabeledImage(name)