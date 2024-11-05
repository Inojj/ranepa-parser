import arrow
import requests
import datetime

from bs4 import BeautifulSoup
from ics import Calendar, Event

url = 'https://spb.ranepa.ru/raspisanie/mn-3-23-01-02-noyabr/'
year = int(datetime.date.today().year)

calendar = Calendar()

response = requests.get(url, verify=False)
soup = BeautifulSoup(response.text, 'lxml')

rasp_table = soup.find(class_='row-hover')
days = rasp_table.find_all('tr')
for day in days:
    time = day.find(class_='column-4').text.split('-')
    time_begin = time[0].split('.')
    hour_begin = time_begin[0]
    minutes_begin = time_begin[-1]
    time_end = time[-1].split('.')
    hour_end = time_end[0]
    minutes_end = time_end[-1]
    event = Event()
    event.name = f"{day.find(class_='column-7').text.strip()} {day.find(class_='column-5').text} {day.find(class_='column-6').text}"
    # arrow.Arrow(year, 5, 5, 12, 30, 45)
    event.begin = datetime.datetime(year=year,
                                    month=int(day.find(class_='column-3').text),
                                    day=int(day.find(class_='column-2').text),
                                    hour=int(hour_begin),
                                    minute=int(minutes_begin),
                                    )
    event.end = datetime.datetime(year=year,
                                  month=int(day.find(class_='column-3').text),
                                  day=int(day.find(class_='column-2').text),
                                  hour=int(hour_end),
                                  minute=int(minutes_end),
                                  )
    event.description = f"Преподаватель: {day.find(class_='column-9').text}. Занятие проходит: {day.find(class_='column-10').text}"
    calendar.events.add(event)


with open('my.ics', 'w', encoding='utf') as my_file:
    my_file.writelines(calendar.serialize_iter())
