import datetime
import things

class Things3:
    def count_of_completed_tasks_for_date(self, date=None):
        # Default to today
        if not date:
             date = date.today()

        iso_date = date.isoformat()
        completed_tasks = things.tasks(status='completed', stop_date=iso_date)
        return len(completed_tasks)


