import csv
import os
import yaml
from pathlib import Path
from collections.abc import Generator

with open(Path(__file__).parent / "config.yaml", "r") as f:
    config = yaml.safe_load(f)

IMAGES_DIR = os.environ["SONIA_WS"] + "/src/Test_IA/" + config['labeled_image']['images_dir']
CSV_DIR = os.environ["SONIA_WS"] + "/src/Test_IA/" + config['labeled_image']['csv_dir']
EXTENSIONS = config['labeled_image']['extensions']


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