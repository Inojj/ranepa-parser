import requests
import datetime

from bs4 import BeautifulSoup
from ics import Calendar, Event
import zoneinfo

from config import EXPECTED_GROUPS, RANEPA_SCHEDULE_URL_PAGE

moscow_tz = zoneinfo.ZoneInfo("Europe/Moscow")
year = int(datetime.date.today().year)

calendar = Calendar()

response = requests.get(RANEPA_SCHEDULE_URL_PAGE, verify=False)
soup = BeautifulSoup(response.text, 'lxml')

rasp_table = soup.find(class_='row-hover')
days = rasp_table.find_all('tr')
for day in days:
    group = day.find(class_='column-5').text
    if group in EXPECTED_GROUPS:
        time = day.find(class_='column-4').text.split('-')
        time_begin = time[0].split('.')
        hour_begin = int(time_begin[0])
        minutes_begin = int(time_begin[-1])
        time_end = time[-1].split('.')
        hour_end = int(time_end[0])
        minutes_end = int(time_end[-1])
        event = Event(name=f"{day.find(class_='column-7').text.strip()} {group} {day.find(class_='column-6').text}",
                      begin=datetime.datetime(year=year,
                                              month=int(day.find(class_='column-3').text),
                                              day=int(day.find(class_='column-2').text),
                                              hour=hour_begin,
                                              minute=minutes_begin,
                                              tzinfo=moscow_tz,
                                              ),
                      end=datetime.datetime(year=year,
                                            month=int(day.find(class_='column-3').text),
                                            day=int(day.find(class_='column-2').text),
                                            hour=hour_end,
                                            minute=minutes_end,
                                            tzinfo=moscow_tz,
                                            ),
                      description=f"Преподаватель: {day.find(class_='column-9').text}. "
                                  f"Занятие проходит: {day.find(class_='column-10').text}"
                      )
        calendar.events.add(event)

with open('ranepa_schedules.ics', 'w', encoding='utf') as my_file:
    my_file.writelines(calendar.serialize_iter())
