import requests
from flask import Flask, render_template, request
import datetime
from flask_caching import Cache
import json
import time

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

API_KEY = "892ec09e650614bee278f3854735b995"


def current_wather(url):
    current_date = datetime.datetime.today()
    current_date = current_date.strftime("%A %d %B")
    response = requests.get(url).json()
    id_icon = response["weather"][0]["icon"]
    temps = int(response['main']['temp']-273.15)
    lows = int(response['main']['temp_min']-273.15)
    highs = int(response['main']['temp_max']-273.15)
    return response, id_icon, temps, current_date, lows, highs


@app.route("/")
@cache.cached(timeout=300)
def home():
    global API_KEY
    ip = request.headers.request.headers.get('X-Real-IP')
    url_ip="https://ipinfo.io/{}?token=4bdb60e14a4fcc".format(ip)
    response_ip = requests.get(url_ip).json()
    name_city = response_ip.get("city")

    url_current ="https://api.openweathermap.org/data/2.5/weather?q={}&APPID={}".format(name_city, API_KEY )
    response, id_icon, temps, current_date, lows, highs = current_wather(url_current)

    url_icon=" https://openweathermap.org/img/wn/{}@2x.png".format(id_icon)

    sunrises = time.strftime("%I:%M", time.gmtime(response['sys']['sunrise']-21600))
    sunsets = time.strftime("%I:%M", time.gmtime(response['sys']['sunset']-21600))

    city = response['name']
    url_forecast = "https://api.openweathermap.org/data/2.5/forecast?q={}&units=metric&cnt=7&appid={}".format(city, API_KEY)
    response_forecast = requests.get(url_forecast).json()
    forecast_data=[]
    for item in response_forecast['list']:
        dt = datetime.datetime.strptime(item['dt_txt'], '%Y-%m-%d %H:%M:%S')
        day_abbr = dt.strftime("%H %p").lower()
        forecast_data.append({
            'day': day_abbr,
            'temp': item['main']['temp'],
            'url_icon_forecast': " https://openweathermap.org/img/wn/"+item['weather'][0]['icon']+"@2x.png"
        })


    return json.dumps(ip)


@app.route("/traitement", methods=["POST"])
@cache.cached(timeout=300)
def traitement():
    global API_KEY
    data = request.form
    name_city = data.get('search_value')
    url_current ="https://api.openweathermap.org/data/2.5/weather?q={}&APPID={}".format(name_city, API_KEY )
    response, id_icon, temps, current_date, lows, highs = current_wather(url_current)

    url_icon=" https://openweathermap.org/img/wn/{}@2x.png".format(id_icon)

    sunrises = time.strftime("%I:%M", time.gmtime(response['sys']['sunrise']-21600))
    sunsets = time.strftime("%I:%M", time.gmtime(response['sys']['sunset']-21600))

    city = response['name']
    url_forecast = "https://api.openweathermap.org/data/2.5/forecast?q={}&units=metric&cnt=7&appid={}".format(city, API_KEY)
    response_forecast = requests.get(url_forecast).json()
    forecast_data=[]
    for item in response_forecast['list']:
        dt = datetime.datetime.strptime(item['dt_txt'], '%Y-%m-%d %H:%M:%S')
        day_abbr = dt.strftime("%H %p").lower()
        forecast_data.append({
            'day': day_abbr,
            'temp': item['main']['temp'],
            'url_icon_forecast': " https://openweathermap.org/img/wn/"+item['weather'][0]['icon']+"@2x.png"
        })

    days_data = []
    url_forecast_7days = "https://api.openweathermap.org/data/2.5/forecast?q={}&units=metric&cnt=56&appid={}".format(city, API_KEY)
    response_forecast_7days = requests.get(url_forecast_7days).json()
    for item in response_forecast_7days['list']:
        dt_txt = item['dt_txt']
        date, times = dt_txt.split(' ')
        year, month, day= date.split('-')
        if times == '12:00:00':
            dt = datetime.datetime.strptime(date, "%Y-%m-%d")
            day_name = dt.strftime('%a').capitalize()
            formatted_date = f"{day}/{month}"
            temp = item['main']['temp']
            humidity = item['main']['humidity']
            pressure = item['main']['pressure']
            low = item['main']['temp_min']
            high = item['main']['temp_max']

            days_data.append({
                'date': formatted_date,
                'day': day_name,
                'low': low,
                'high': high,
                'temp': temp,
                'humidity': humidity,
                'pressure': pressure,
                'url_icon_forecast_7days': " https://openweathermap.org/img/wn/"+item['weather'][0]['icon']+"@2x.png"
            })

    return render_template("result.html", url_i=url_icon, data=response, date=current_date, temp = temps, low = lows, high = highs, sunrise= sunrises, sunset = sunsets, forecast = forecast_data, forecast_days = days_data)


@app.route("/search", methods=["POST"])
@cache.cached(timeout=300)
def search():
    global API_KEY
    data = request.form
    name_city = data.get('search_value')
    url_current ="https://api.openweathermap.org/data/2.5/weather?q={}&APPID={}".format(name_city, API_KEY )
    response, id_icon, temps, current_date, lows, highs = current_wather(url_current)

    url_icon=" https://openweathermap.org/img/wn/{}@2x.png".format(id_icon)

    sunrises = time.strftime("%I:%M", time.gmtime(response['sys']['sunrise']-21600))
    sunsets = time.strftime("%I:%M", time.gmtime(response['sys']['sunset']-21600))

    city = response['name']
    url_forecast = "https://api.openweathermap.org/data/2.5/forecast?q={}&units=metric&cnt=7&appid={}".format(city, API_KEY)
    response_forecast = requests.get(url_forecast).json()
    forecast_data=[]
    for item in response_forecast['list']:
        dt = datetime.datetime.strptime(item['dt_txt'], '%Y-%m-%d %H:%M:%S')
        day_abbr = dt.strftime("%H %p").lower()
        forecast_data.append({
            'day': day_abbr,
            'temp': item['main']['temp'],
            'url_icon_forecast': " https://openweathermap.org/img/wn/"+item['weather'][0]['icon']+"@2x.png"
        })

    days_data = []
    url_forecast_7days = "https://api.openweathermap.org/data/2.5/forecast?q={}&units=metric&cnt=56&appid={}".format(city, API_KEY)
    response_forecast_7days = requests.get(url_forecast_7days).json()
    for item in response_forecast_7days['list']:
        dt_txt = item['dt_txt']
        date, times = dt_txt.split(' ')
        year, month, day= date.split('-')
        if times == '12:00:00':
            dt = datetime.datetime.strptime(date, "%Y-%m-%d")
            day_name = dt.strftime('%a').capitalize()
            formatted_date = f"{day}/{month}"
            temp = item['main']['temp']
            humidity = item['main']['humidity']
            pressure = item['main']['pressure']
            low = item['main']['temp_min']
            high = item['main']['temp_max']

            days_data.append({
                'date': formatted_date,
                'day': day_name,
                'low': low,
                'high': high,
                'temp': temp,
                'humidity': humidity,
                'pressure': pressure,
                'url_icon_forecast_7days': " https://openweathermap.org/img/wn/"+item['weather'][0]['icon']+"@2x.png"
            })

    return render_template("result.html", url_i=url_icon, data=response, date=current_date, temp = temps, low = lows, high = highs, sunrise= sunrises, sunset = sunsets, forecast = forecast_data, forecast_days = days_data)


if __name__ == "__main__":
    app.run(debug=True)