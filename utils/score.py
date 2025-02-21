from CONSTANT import SCORING


class ScoreCalculator:
    def __init__(self, data):
        self.data = data

    def calc_score(self):
        score = 0
        for key, value in self.data.items():
            print()
            score += int(value)
        return score

    def range_score(self):
        num_questions = len(self.data)
        low_score = round(num_questions * 1 / 3, 1)
        mid_score = round(num_questions * 2 / 3, 1)
        max_score = round(num_questions * 2, 1)

        return {
            "low": {"min": 0, "max": low_score},
            "mid": {"min": low_score + 0.1, "max": mid_score},
            "high": {"min": mid_score + 0.1, "max": max_score},
        }

    def classify_score(self):
        ranges = self.range_score()
        score = self.calc_score()

        if ranges["low"]["min"] <= score <= ranges["low"]["max"]:
            return "Rendah"
        elif ranges["mid"]["min"] <= score <= ranges["mid"]["max"]:
            return "Sederhana"
        elif ranges["high"]["min"] <= score <= ranges["high"]["max"]:
            return "Tinggi"
