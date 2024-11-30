import datetime
import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from zoneinfo import ZoneInfo


from config import PRACTICE_GROUP, LECTURE_GROUPS, RANEPA_SCHEDULE_URL_PAGE

# Часовой пояс Москвы
moscow_tz = ZoneInfo("Europe/Moscow")
current_year = datetime.date.today().year

# Константы для имен классов столбцов
COLUMN_DAY = 'column-2'
COLUMN_MONTH = 'column-3'
COLUMN_TIME = 'column-4'
COLUMN_GROUP = 'column-5'
COLUMN_LESSON_TYPE = 'column-6'
COLUMN_SUBJECT = 'column-7'
COLUMN_TEACHER = 'column-9'
COLUMN_LOCATION = 'column-10'


def parse_event(group_name, day) -> Event:
    try:
        # Разбор времени начала и конца занятия
        time_text = day.find(class_=COLUMN_TIME).text.strip()
        try:
            time_begin_str, time_end_str = time_text.split('-')
        except Exception:
            time_begin_str = time_text
            time_end_str = None
        time_format = "%H.%M"
        time_begin = datetime.datetime.strptime(time_begin_str, time_format)
        time_end = datetime.datetime.strptime(time_end_str, time_format) if time_end_str else None

        # Разбор даты
        day_num = int(day.find(class_=COLUMN_DAY).text.strip())
        month_num = int(day.find(class_=COLUMN_MONTH).text.strip())

        # Создание объектов datetime с учетом часового пояса
        event_start = datetime.datetime(
            year=current_year,
            month=month_num,
            day=day_num,
            hour=time_begin.hour,
            minute=time_begin.minute,
            tzinfo=moscow_tz
        )
        event_end = datetime.datetime(
            year=current_year,
            month=month_num,
            day=day_num,
            hour=time_end.hour,
            minute=time_end.minute,
            tzinfo=moscow_tz
        ) if time_end else None

        # Формирование названия и описания события
        subject = day.find(class_=COLUMN_SUBJECT).text.strip()
        lesson_type = day.find(class_=COLUMN_LESSON_TYPE).text.strip()
        teacher = day.find(class_=COLUMN_TEACHER).text.strip()
        location = day.find(class_=COLUMN_LOCATION).text.strip()

        event_name = f"{subject} {group_name} {lesson_type}"
        event_description = f"Преподаватель: {teacher}. Занятие проходит: {location}"

        return Event(
            name=event_name,
            begin=event_start,
            end=event_end,
            description=event_description
        )
    except Exception as e:
        print(f"Ошибка при обработке события: {e}")
        return None


def generate_calendar(days, group_name, output_file):
    calendar = Calendar()
    for day in days:
        group = day.find(class_=COLUMN_GROUP).text.strip()
        if group == group_name:
            event = parse_event(group_name, day)
            if event:
                calendar.events.add(event)
    with open(output_file, 'w', encoding='utf8') as file:
        file.writelines(calendar.serialize_iter())


def main():
    # Получение данных с веб-страницы
    response = requests.get(RANEPA_SCHEDULE_URL_PAGE, verify=False)
    soup = BeautifulSoup(response.text, 'lxml')

    # Поиск таблицы расписания
    schedule_table = soup.find(class_='row-hover')
    days = schedule_table.find_all('tr')

    # Генерация календарей
    generate_calendar(days, PRACTICE_GROUP, 'ranepa_schedules_practice.ics')
    generate_calendar(days, LECTURE_GROUPS, 'ranepa_schedules_lecture.ics')


if __name__ == "__main__":
    main()
