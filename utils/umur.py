from datetime import datetime


class UmurCalculator:
    def __init__(self, ic_number):
        self.ic = ic_number

    def get_age(self):
        today = datetime.today()
        dob = self.get_dob()
        age = today.year - dob.year - \
            ((today.month, today.day) < (dob.month, dob.day))

        return age

    def get_dob(self):
        """
        Calculate age based on IC number.

        Parameters:
        ic_number (str): The IC number in the format '010929090900'.

        Returns:
        int: The date of birth of the person.
        """

        # Extract year, month, and day from IC number
        today = datetime.today()
        year_code = int(self.ic[0:2])

        # if we total up year code with 2000 it not greater or equal than current year, it is 20's
        if (year_code + 2000) <= today.year:
            year = 2000 + year_code
        else:
            year = 1900 + year_code

        month = int(self.ic[2:4])
        day = int(self.ic[4:6])

        # Validate date
        try:
            return datetime(year, month, day)
        except ValueError:
            raise ValueError("Invalid date in IC number")
