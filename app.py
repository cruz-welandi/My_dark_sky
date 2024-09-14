import requests
from flask import Flask, render_template, request
import datetime
from flask_caching import Cache
import json
import socket
import time

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

API_KEY = "892ec09e650614bee278f3854735b995"


def current_wather(url):
    current_date = datetime.datetime.today()
    current_date = current_date.strftime("%A %d %B")
    try: 
        response = requests.get(url).json()

        if response['cod'] == 200:
            id_icon = response["weather"][0]["icon"]
            temps = int(response['main']['temp']-273.15)
            lows = int(response['main']['temp_min']-273.15)
            highs = int(response['main']['temp_max']-273.15)

            data = {
                'id_icon': id_icon,
                'current_date': current_date,
                'temps': temps,
                'lows': lows,
                'highs': highs,
                'response': response
            }
            return data
        else:
            return {"error": "API request failed with status code: {}".format(response['cod'])}
    except requests.exceptions.RequestException as e:
        return {"error": "Request failed: {}".format(e)}   
        

def forcast_7days(url):
    data=[]
    try:
        response_forecast_7days = requests.get(url).json()

        if response_forecast_7days['cod'] == '200':
            print('correct')
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

                    data.append({
                        'date': formatted_date,
                        'day': day_name,
                        'low': low,
                        'high': high,
                        'temp': temp,
                        'humidity': humidity,
                        'pressure': pressure,
                        'url_icon_forecast_7days': " https://openweathermap.org/img/wn/"+item['weather'][0]['icon']+"@2x.png"
                    })
            return data
        else:
            return {"error": "API request failed with status code: {}".format(response_forecast_7days['cod'])}
    except requests.exceptions.RequestException as e:
        return {"error": "Request failed: {}".format(e)} 

def forcast(url):
    data=[]
    try: 
        response_forecast = requests.get(url).json()
        
        if response_forecast['cod'] == '200':
            print('correct')
            for item in response_forecast['list']:
                dt = datetime.datetime.strptime(item['dt_txt'], '%Y-%m-%d %H:%M:%S')
                day_abbr = dt.strftime("%H %p").lower()
                data.append({
                    'day': day_abbr,
                    'temp': item['main']['temp'],
                    'url_icon_forecast': " https://openweathermap.org/img/wn/"+item['weather'][0]['icon']+"@2x.png"
                })
            
            return data
        else:
            return {"error": "API request failed with status code: {}".format(response_forecast['cod'])}
    except requests.exceptions.RequestException as e:
        return {"error": "Request failed: {}".format(e)} 


@app.route("/")
def home():
    global API_KEY
    name_city = "LEKONI"
    url_current ="https://api.openweathermap.org/data/2.5/weather?q={}&APPID={}".format(name_city, API_KEY )
    data_current = current_wather(url_current)
    
    url_icon=" https://openweathermap.org/img/wn/{}@2x.png".format(data_current['id_icon'])

    sunrises = time.strftime("%I:%M", time.gmtime(data_current['response']['sys']['sunrise']-21600))
    sunsets = time.strftime("%I:%M", time.gmtime(data_current['response']['sys']['sunset']-21600))

    city = data_current['response']['name']
    url_forecast = "https://api.openweathermap.org/data/2.5/forecast?q={}&units=metric&cnt=7&appid={}".format(city, API_KEY)
    forecast_data = forcast(url_forecast)

    if data_current or forecast_data:
        return render_template("index.html", url_i=url_icon, data=data_current['response'], date=data_current['current_date'], temp = data_current['temps'], low = data_current['lows'], high = data_current['highs'], sunrise= sunrises, sunset = sunsets, forecast = forecast_data )
    elif data_current['error']:
        return data_current['error']
    elif forecast_data['error']:
        return forecast_data['error']



@app.route("/traitement", methods=["POST"])
def traitement():
    global API_KEY
    data = request.form
    name_city = data.get('search_value')
    url_current ="https://api.openweathermap.org/data/2.5/weather?q={}&APPID={}".format(name_city, API_KEY )
    data_current = current_wather(url_current)
    
    url_icon=" https://openweathermap.org/img/wn/{}@2x.png".format(data_current['id_icon'])

    sunrises = time.strftime("%I:%M", time.gmtime(data_current['response']['sys']['sunrise']-21600))
    sunsets = time.strftime("%I:%M", time.gmtime(data_current['response']['sys']['sunset']-21600))

    city = data_current['response']['name']
    url_forecast = "https://api.openweathermap.org/data/2.5/forecast?q={}&units=metric&cnt=7&appid={}".format(city, API_KEY)
    forecast_data = forcast(url_forecast)

    url_forecast_7days = "https://api.openweathermap.org/data/2.5/forecast?q={}&units=metric&cnt=56&appid={}".format(city, API_KEY)
    days_data = forcast_7days(url_forecast_7days)

    if data_current or forecast_data or days_data:
        return render_template("result.html", url_i=url_icon, data=data_current['response'], date=data_current['current_date'], temp = data_current['temps'], low = data_current['lows'], high = data_current['highs'], sunrise= sunrises, sunset = sunsets, forecast = forecast_data, forecast_days = days_data)
    elif data_current['error']:
        return data_current['error']
    elif forecast_data['error']:
        return forecast_data['error']
    elif days_data['error']:
        return days_data['error']


if __name__ == "__main__":
    app.run(debug=True)