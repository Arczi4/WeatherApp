from os import name
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
import requests
import hashlib

# Słownik zawierający dodatkowe informacje do wyskakującego okienka
Pollution = {'Good': '  Air quality is considered satisfactory\n  air pollution poses little or no risk',
            'Moderate': '  Air quality is acceptable:\n  for some pollutants there may be a moderate health\n  concern for a very small number of people\n  who are unusually sensitive to air pollution.',
            'Unhealthy for \n             Sensitive Groups': 'Members of sensitive groups may experience\nhealth effects. The general public is not likely\nto be affected.',
            'Unhealthy': '  Everyone may begin to experience\n  health effects: members of sensitive groups\n  may experience more serious health effects',
            'Very Unhealthy': 'Health warnings of emergency conditions.\nThe entire population is more likely to be affected.',
            'Hazardous': 'Health alert: everyone may experience\nmore serious health effects'}


BASE = 'http://127.0.0.1:5000/'
WHEATHER_API = 'http://api.openweathermap.org/data/2.5/weather?id=524901&appid=6e931473ff3e014d501365f6cdbfa0fc&q='

# Okno logowania
class MainWindow(Screen):
    username = ObjectProperty(None) 
    password = ObjectProperty(None)

    # Funkcjonalność przycisku Log in
    def log_in_Btn(self):
        usr = self.username.text
        passwd = self.password.text
        response = requests.get(BASE + f'user/{usr}') # wysłanie get request do podanego url BASE/user/usr
        hashed = hashlib.sha1(passwd.encode('utf-8')) # Szyfrowanie hasła wpisanego w aplikacji w celu porównania go z hasłem zapisanym w bazie 
        try: # Kontrola błędu
            if  usr != '' and passwd != '': # Sprawdzanie poprawności danych
                if response.json()['username'] == usr and response.json()['password']==hashed.hexdigest():
                        self.reset()
                        sm.current = "AppWin" # Dane się zgadzają -> przejście do okna aplikacji
                        login() # Wywołanie wyskakującego okienka - Popup window
                else:
                    wrongdata()
            else:
                wrongdata()
        except:
            self.reset() # Czyszczenie pól login password
            wrongdata() # Wywołanie wyskakującego okienka - Popup window

    # Funkcjonalnośc przyciusku Create account 
    def createBtn(self): 
        self.reset() # Czyszczenie pól login password
        sm.current = 'Create' # Zmiana okna na okno rejestrowania

    # Funkcja czyszcząca pola login password
    def reset(self):
        self.username.text = ""
        self.password.text = ""

# Okno aplikacji
class AppWindow(Screen):
    # Tworzenie zmiennych do których będą przypisywane dane pobrane z api oraz użytkownika
    city = ObjectProperty(None) 
    # Weather
    country = StringProperty(None)
    weather = StringProperty(None)
    temp = StringProperty(None)
    pressure = StringProperty(None)
    wind = StringProperty(None)
    
    # Air quality
    status = StringProperty(None)
    co = StringProperty(None)
    pm10 = StringProperty(None)
    pm25 = StringProperty(None)
    so2 = StringProperty(None)
    
    # Funkcjonalnośc przyciusku Log out 
    def go_main(self):
        self.reset() # Funkcja czyszcząca pola 
        log_out() # Wywołanie wyskakującego okienka - Popup window
        sm.current = "Main" # Zmiana okna na okno logowania

    # Czyszczenie pola city
    def reset_city(self):
        self.city.text = '' 

    # API
    def check_weather(self):
        city = self.city.text # zmienna wpisana w pole tekstowe w aplikacji
        if len(city) != 0: # Sprawdzanie czy w pole zostało cokolwiek wpisane
            self.reset() # czyszczenie pola

            # Pobieranie danych pogodowych i jakośic powietrze z serwera
            url = WHEATHER_API + city
            data_w = requests.get(url).json()
            AIR_WAQI = f'https://api.waqi.info/feed/{city}/?token=eb242489ce9c640a89dc254411c54390bda04aee'
            data_a = requests.get(AIR_WAQI).json()

            # Przypisywanie wcześniej zainicjalizowanych zmiennych do tych pobranych z serwera, try-expect->kontrola błędów
            try: 
                country = data_w['sys']['country']
            except:
                country = 'Lack of data'    
            try:
                weather = data_w['weather'][0]['description']
            except:
                weather = 'Lack of data'
            try:
                temp = str(round((data_w['main']['temp'] - 273), 2))
            except:
                temp = 'Lack of data'
            try:
                pressure = str(round(data_w['main']['pressure'],2))
            except:
                pressure = 'Lack of data'
            try:    
                wind = str(round(data_w['wind']['speed'],2))
            except:
                wind = 'Lack of data'
            self.country = country
            self.weather = weather
            self.temp = temp
            self.pressure = pressure
            self.wind = wind
            
            # Air
            try:
                aqi = data_a['data']['aqi']
                if aqi < 50:
                    status = 'Good'

                if aqi > 51 and aqi<100:
                    status = 'Moderate'

                if aqi > 101 and aqi<150:
                    status = 'Unhealthy for \n             Sensitive Groups'

                if aqi > 151 and aqi<200:
                    status = 'Unhealthy'

                if aqi > 201 and aqi<300:
                    status = 'Very Unhealthy'

                if aqi > 300:
                    status = 'Hazardous'
                    
            except:
                status = 'Lack of data'
            try:
                co = str(data_a['data']['iaqi']['co']['v'])
            except:
                co='Lack of data'
            try:
                pm10 = str(data_a['data']['iaqi']['pm10']['v'])
            except:
                pm10='Lack of data'
            try:
                pm25 = str(data_a['data']['iaqi']['pm25']['v'])
            except:
                pm25 = 'Lack of data'
            try:
                so2 = str(data_a['data']['iaqi']['so2']['v'])
            except:
                so2='Lack of data'
            self.status = status
            self.co = co
            self.pm10 = pm10
            self.pm25 = pm25
            self.so2 = so2
        
        else:
            city_none() # Wywołanie wyskakującego okienka - Popup window
    
    # Czyszczenie zawartości zmiennych
    def reset(self):
        self.country = ''
        self.weather = ''
        self.temp = ''
        self.pressure = ''
        self.wind = ''

        self.status = ''
        self.co = ''
        self.pm10 = ''
        self.pm25 = ''
        self.so2 = ''

    # Funkcjonalność przycisku More Info
    def more(self, st):
        more_info(st)

# Okno rejestracji
class CreateWindow(Screen):
    username = ObjectProperty(None)
    password = ObjectProperty(None)

     # Funkcjonalnośc przyciusku Already have an account 
    def go_main(self):
        self.reset() # Czyszczenie pola username i password
        sm.current = "Main" # Zmiana okna na okno logowania

    # Funkcjonalność przyciusku Create account
    def create(self): 
        # Przypisanie zmiennych wpisanych w pola tekstowe w aplikacji
        username = self.username.text 
        password = self.password.text
        
        response = requests.put(BASE + f'user/{username}', data={'password': f'{password}'}) # wywołanie metody put request w celu zapisania go do bazy danych
        # Sprawdzenie Status Code
        output = str(response).split(' ')[1] 
        out = output[1:4]

        if out == '409': # Konflikt danych
            self.reset()
            indata() # Wywołanie wyskakującego okienka - Popup window
        else: # Jeśli brak konfilktu dodanie nowego użytkownika
            self.reset()
            created_account() # Wywołanie wyskakującego okienka - Popup window

    # Funkcja czyszcząca pola tekstowe
    def reset(self):
        self.username.text = ""
        self.password.text = ""

# Klasa umożliwiająca przechodzenie między oknami Main, AppWin, Create
class WindowManager(ScreenManager):
    pass

# Funkcje wyskakujących okienek (Popup Winow), zawierające dodatkowe informacje o działaniu aplikacji
def indata():
    pop = Popup(title='Error',
                  content=Label(text='Username is already taken'),
                  size_hint=(None, None), size=(400, 400))
    pop.open()

def login():
    pop = Popup(title='Login succesful',
                  content=Label(text='Login succesful!'),
                  size_hint=(None, None), size=(400, 400))
    pop.open()

def invaliddata():
    pop = Popup(title='Error',
                content=Label(text='Invalid email or data!'),
                size_hint=(None, None), size=(400, 400))
    pop.open()


def wrongdata():
    pop=Popup(title="ERROR",
              content=Label(text="Wrong username or password"),
              size_hint=(None, None), size=(400, 400))
    pop.open()

def created_account():
    pop=Popup(title="Created",
              content=Label(text="Created"),
              size_hint=(None, None), size=(400, 400))
    pop.open()

def log_out():
    pop=Popup(title="Log out",
              content=Label(text="Log out succesful"),
              size_hint=(None, None), size=(400, 400))
    pop.open() 

def city_none():
    pop=Popup(title="City error",
              content=Label(text="No city name provided!"),
              size_hint=(None, None), size=(400, 400))
    pop.open() 

def more_info(stat):
    try:
        pop=Popup(title="More info",
                content=Label(text=Pollution[stat]),
                size_hint=(None, None), size=(400, 400))
    except:
        pop=Popup(title="More info",
                content=Label(text='Check weather first!'),
                size_hint=(None, None), size=(400, 400))

    pop.open() 


kv = Builder.load_file("my2.kv")
sm = WindowManager()

# Funkcjonalność przechodzenia między oknami aplikacji
screens = [MainWindow(name='Main'), CreateWindow(name='Create'), AppWindow(name='AppWin')]
for screen in screens:
    sm.add_widget(screen)

class MyMainApp(App):
    def build(self):
        return sm


if __name__ == '__main__':
    MyMainApp().run()

