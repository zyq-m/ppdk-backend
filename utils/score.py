class ScoreCalculator:
    def __init__(self, total):
        self.totalScore = total

    def score_category(self, obtained):
        percentage = self.score_percentage(obtained)

        if percentage >= 90:
            category = "Sangat Tinggi"
        elif percentage >= 75:
            category = "Tinggi"
        elif percentage >= 50:
            category = "Sederhana"
        else:
            category = "Rendah"

        return category

    def score_percentage(self, obtained):
        percentage = (obtained / self.totalScore) * 100
        return percentage
