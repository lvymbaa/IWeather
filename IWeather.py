import pyowm
from pyowm.utils.config import get_default_config
import geocoder
import speech_recognition as sr
import pyttsx3
import datetime
from fuzzywuzzy import fuzz
# для ответов
tts = pyttsx3.init()
rate = tts.getProperty('rate')
tts.setProperty('rate', rate-40)
volume = tts.getProperty('volume')
tts.setProperty('volume', volume+0.9)

# настройка координат и менеджера погоды
g = geocoder.ip('me')
token = '3115bbd4f082056bdbee0d8b561877f3'
owm = pyowm.OWM(token)
mgr = owm.weather_manager()

opts = {
    "alias": ('сима', 'сим'),

    "tbr": ('скажи','расскажи','мне','слушай','послушай','а','произнести','покажи',
    'какая','какой','какое','какие','интересно','же', 'насколько', 'как','большая', 'большие',
    'много','большое','большой','сегодня'), # ненужные слова в команде
                                    
    "cmds": {
        "temp": ('температура','температуру','сколько градусов',),

        "press": ('давление','сейчас давление'),

        "hum": ('влажность','влажность','влажно'),

        "cloud": ('облачно','облака','облачность'),

        "time": ('который час','сколько времени','сколько сейчас времени'),

    } # команды
}

#('давление','температура','время','влажность','видимость','облачность','статус') # команды

def how_to_say(number, word):
    if number % 10 == 1 and number % 100 != 11:
        if word == 'град':
            return 'градус'
        elif word == 'дав':
            return 'миллиметр'
        elif word == 'час':
            return 'час'
        elif word == 'мин':
            return 'минута'
    elif number % 10 >= 2 and number % 10 <= 4 and (number % 100 < 10 or number % 100 > 20):
        if word == 'град':
            return 'градуса'
        elif word == 'дав':
            return 'миллиметра'
        elif word == 'час':
            return 'часа'
        elif word == 'мин':
            return 'минуты'
    else:
        if word == 'град':
            return 'градусов'
        elif word == 'дав':
            return 'миллиметров'
        elif word == 'час':
            return 'часов'
        elif word == 'мин':
            return 'минут'

# говорит температуру
def say_temperature(flag):
    observation = mgr.weather_at_coords(*g.latlng)
    w = observation.weather
    config_dict = get_default_config()
    config_dict['language'] = 'ru'

    t = w.temperature("celsius")
    t_now = round(t['temp']) # температура сейчас
    t_feels = round(t['feels_like']) # как ощущается
    t_max = round(t['temp_max']) # максимальная температура
    t_min = round(t['temp_min']) # минимальная

    if flag is True:
        say_message(f'Сейчас температура воздуха {t_now} {how_to_say(t_now, "град")}, ощущается как {t_feels} {how_to_say(t_feels, "град")}.')

    elif flag is False:
        say_message(f'Сегодня максимальная температура воздуха составит {t_max} {how_to_say(t_max, "град")},'
        + f'минимальная - {t_min} {how_to_say(t_min, "град")}. На данный момент температура воздуха составляет {t_now} {how_to_say(t_now, "град")},'
        + f'ощущается как {t_feels} {how_to_say(t_feels, "град")}')

# говорит атмосферное давление
def say_pressure():
    observation = mgr.weather_at_coords(*g.latlng)
    w = observation.weather
    config_dict = get_default_config()
    config_dict['language'] = 'ru'

    pr = round(w.pressure['press'] * 0.75)
    say_message(f'Атмосферное давление составляет {pr} {how_to_say(pr, "дав")} ртутного столба.')

# говорит влажность
def say_humidity():
    observation = mgr.weather_at_coords(*g.latlng)
    w = observation.weather
    config_dict = get_default_config()
    config_dict['language'] = 'ru'

    hum = w.humidity

    say_message(f'Влажность сегодня составляет {hum} %.')

# говорит облачность
def say_clouds():
    observation = mgr.weather_at_coords(*g.latlng)
    w = observation.weather
    config_dict = get_default_config()
    config_dict['language'] = 'ru'

    cl = w.clouds

    say_message(f'Сегодня облачность {cl} %.')

# говорит текущее время
def say_time():
    time = datetime.datetime.now()
    say_message(f"Сейчас {time.hour} {how_to_say(time.hour, 'час')} {time.minute} {how_to_say(time.minute, 'мин')}")
    
# слушает команду
def listen_command():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone(device_index=1)
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.1) 
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio, language='ru-RU').lower()

        if 'прощай' in command:
            say_message('Было приятно с вами общаться.')
            exit()
        
        for x in opts['alias']:
            command = command.replace(x, "").strip()

        for x in opts['tbr']:
            command = command.replace(x, "").strip()


        command = recognize_command(command)
        return command


    except sr.UnknownValueError:
        return "error"

    except sr.RequestError:
        return "error"

#нечеткое сравнение команды cmd с элементами словаря возможных команд
#c - элемент словаря opts(список возможных произношений)
#v - возможные произношения команды
def recognize_command(command):
    RC = {'cmd': '', 'percent': 0}
    for c,v in opts['cmds'].items():
        for x in v:
            vrt = fuzz.ratio(command, x)#степень похожести
            if vrt > RC['percent']:
                RC['cmd'] = c
                RC['percent'] = vrt
    
    return RC

# выполнение комманды
def do_command(command):
    if command == "temp":
        if "сейчас" in command:
            say_temperature(True)
        else:
            say_temperature(False)

    elif command == "press":
        say_pressure()

    elif command == "hum":
        say_humidity()

    elif command == "cloud":
        say_clouds()
        

    elif command == "time":
        say_time()
    else:
        pass

#проговаривание аудиосообщения
def say_message(message):
    tts.say(message)
    tts.runAndWait()
    tts.stop()



""" while greeting is not True:
    recognizer = sr.Recognizer()
    microphone = sr.Microphone(device_index=1)
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.1) 
        audio = recognizer.listen(source)
    try:
        speech = recognizer.recognize_google(audio, language='ru-RU').lower()
        if 'привет' and 'сима' in speech:
            greeting = True
            say_message("Здравствуйте. Чем я могу вам помочь?")
    except:
        pass
 """

def main_func():
    say_message("Здравствуйте. Чем я могу вам помочь?")
    try:
        command = listen_command()
        do_command(command['cmd'])
    except:
        pass