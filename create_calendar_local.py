import requests
from ics import Calendar, Event
from datetime import datetime, timezone, timedelta
import pytz

def get_sun_events(current_date_str):
    # Generazione pulita dell'URL
    sun_times_url = f"https://api.sunrise-sunset.org/json?lat=40.945&lng=14.296&date={current_date_str}"

    response = requests.get(sun_times_url)
    if response.status_code != 200:
        print(f"Fallimento API. Status code: {response.status_code}")
        return []

    data = response.json()
    time_format = "%I:%M:%S %p"
    year, month, day = map(int, current_date_str.split('-'))

    # Parsing degli orari e assegnazione rigorosa del fuso orario UTC
    datetime_objects = {
        key: datetime.strptime(value, time_format).replace(tzinfo=pytz.utc)
        for key, value in data['results'].items()
        if key != 'day_length'
    }

    # Sostituzione della data mantenendo il fuso orario intatto
    for key, dt_obj in datetime_objects.items():
        datetime_objects[key] = dt_obj.replace(year=year, month=month, day=day)

    events = []

    # Creazione evento Alba
    e_sunrise = Event()
    e_sunrise.name = "🌅 Sunrise"
    # L'uso di isoformat() preserva l'offset UTC (+00:00) per gli standard ICS
    e_sunrise.begin = datetime_objects['sunrise'].isoformat()
    e_sunrise.duration = {'seconds': 15*60}
    events.append(e_sunrise)

    # Creazione evento Tramonto
    e_sunset = Event()
    e_sunset.name = "🌇 Sunset"
    e_sunset.begin = datetime_objects['sunset'].isoformat()
    e_sunset.duration = {'seconds': 15*60}
    events.append(e_sunset)

    return events

# Inizializzazione Calendario
c = Calendar()
current_dt = datetime.now(timezone.utc)

# Calcolo per oggi e i successivi 6 giorni (7 giorni totali)
for i in range(7):
    date_str = (current_dt + timedelta(days=i)).strftime('%Y-%m-%d')
    for event in get_sun_events(date_str):
        c.events.add(event)

# Serializzazione sicura su file
with open('sun.ics', 'w') as f:
    f.writelines(c.serialize_iter())
