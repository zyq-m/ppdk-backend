class ScoreCalculator:
    def __init__(self, total=0, data={}):
        self.totalScore = total
        self.data = data

    def score_category(self, obtained):
        percentage = self.score_percentage(obtained)

        if percentage >= 90:
            category = 3
        elif percentage >= 75:
            category = 2
        elif percentage >= 50:
            category = 1
        else:
            category = 0

        return category

    def score_percentage(self, obtained):
        percentage = (obtained / self.totalScore) * 100
        return percentage

    def calc_score(self):
        score = 0
        for key, value in self.data.items():
            score += int(value)
        return score

    def calc_sdq_score(self, ranges, obtained):
        for i, (start, end) in enumerate(ranges):
            if start <= obtained <= end:
                return i
        return -1
