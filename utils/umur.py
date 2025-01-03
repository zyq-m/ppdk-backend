from datetime import datetime


class UmurCalculator:
    def __init__(self, no_ic):
        # year of birth
        self.yob = 2000 + int(no_ic[:2])

    def get_age(self):
        current_year = datetime.now().year
        age = current_year - self.yob
        return age
