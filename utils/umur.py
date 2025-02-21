from datetime import datetime


class UmurCalculator:
    def __init__(self, dob):
        # year of birth
        # self.yob = datetime.strptime(dob, "%Y-%m-%d").year
        self.yob = dob.year

    def get_age(self):
        current_year = datetime.now().year
        age = current_year - self.yob
        return age
