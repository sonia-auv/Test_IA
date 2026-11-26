import yaml
from pathlib import Path

with open(Path(__file__).parent / "config.yaml", "r") as f:
    config = yaml.safe_load(f)

GREEN = config['comparator']['color']['green']
YELLOW = config['comparator']['color']['yellow']
RED = config['comparator']['color']['red']
RESET = config['comparator']['color']['reset']
TOLERANCE = config['comparator']['tolerance']
FIELDS = config['comparator']['fields']
Detection = dict[str, str]


class Comparator:

    def __init__(self, expected: list[Detection], result: list[Detection]):
        self.expected: list[Detection] = expected
        self.result: list[Detection] = result


    def compare(self, image_name: str):
        print(f"\n===== IMG: {image_name} =====")
        matched, missing, extra = self.__match_all()
        success = len(matched)
        for m in matched:
            print(f"{GREEN}[MATCHED]{RESET} {self.__format_result(m)}")
        for exp in missing:
            print(f"{RED}[MISSING]{RESET} {self.__format_result(exp)}")
        for r in extra:
            print(f"{RED}[EXTRA]{RESET} {self.__format_result(r)}")
        success_rate = success * 100 / len(self.expected)
        success_color = self.__set_color(success_rate)
        print(f"==={success_color} {success_rate:.2f}% ({success} / {len(self.expected)}){RESET} ===\n")


    def __format_result(self, d: Detection) -> str:
        return ", ".join(f"{abbr}={d.get(field)}" for field, abbr in FIELDS.items())


    def __is_match(self, exp: Detection, got: Detection) -> bool:
        if exp['class_name'] != got.get('class_name'):
            return False
        for field in list(FIELDS.keys())[1:]:
            expected_value, got_value = float(exp[field]), float(got[field])
            if abs(got_value - expected_value) > TOLERANCE:
                return False
        return True
    

    def __match_all(self) -> tuple[list[Detection], list[Detection], list[Detection]]:
        matched, missing, extra = [], [], list(self.result)
        for exp in self.expected:
            got: Detection | None = next((r for r in extra if self.__is_match(exp, r)), None)
            if got is not None:
                matched.append(got)
                extra.remove(got)
            else:
                missing.append(exp)
        return matched, missing, extra


    @staticmethod
    def __set_color(success_rate: float) -> str:
        if success_rate >= 90:
            color = GREEN
        elif success_rate >= 60:
            color = YELLOW
        else:
            color = RED
        return color