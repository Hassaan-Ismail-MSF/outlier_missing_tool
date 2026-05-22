from datetime import datetime, timedelta

def generate_week_range(start_week, end_week):
    def week_to_date(week_str):
        year = int(week_str[:4])
        week = int(week_str[5:])
        return datetime.fromisocalendar(year, week, 1)

    start_date = week_to_date(start_week)
    end_date = week_to_date(end_week)

    weeks = []
    current = start_date

    while current <= end_date:
        year, week, _ = current.isocalendar()
        weeks.append(f"{year}W{week:02d}")
        current += timedelta(days=7)

    return weeks

def date_to_week(date_obj):
    year, week, _ = date_obj.isocalendar()
    return f"{year}W{week:02d}"
