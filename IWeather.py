import pyowm
from pyowm.utils.config import get_default_config
import geocoder
import speech_recognition as sr
import pyttsx3
import datetime
from fuzzywuzzy import fuzz
from pathlib import Path
from tkinter import Tk, Canvas, Text, Button, PhotoImage
from tkinter.constants import DISABLED, END, NORMAL
from ctypes import *
import goslate



OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./assets")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

# для ответов
tts = pyttsx3.init() 
""" rate = tts.getProperty('rate')
tts.setProperty('rate', rate-50) """
volume = tts.getProperty('volume')
tts.setProperty('volume', volume+0.9)



nowFlag = False
commandText = ''


# настройка координат и менеджера погоды
g = geocoder.ip('me')
token = '3115bbd4f082056bdbee0d8b561877f3'
owm = pyowm.OWM(token)
mgr = owm.weather_manager()

opts = {
    "alias": ('сима', 'сим'),

    "tbr": ('скажи','расскажи','мне','слушай','послушай','а','произнести','покажи',
    'какая','какой','какое','какие','интересно','же', 'насколько', 'как','большая', 'большие',
    'много','большое','большой','сегодня', 'есть'), # ненужные слова в команде
                                    
    "cmds": {
        "temp": ('температура','температуру','сколько градусов',),

        "press": ('давление','сейчас давление'),

        "hum": ('влажность','влажность','влажно'),

        "cloud": ('облачно','облака','облачность'),

        "wind": ('скорость', 'ветер', 'ветра', 'скорость ветра'),

        "fl": ('осадки', 'погода'),

        "time": ('который час','сколько времени','сколько сейчас времени'),

    } # команды
}



def how_to_say(number, word):
    number = abs(number)
    if number % 10 == 1 and number % 100 != 11:
        if word == 'град':
            return 'градус'
        elif word == 'дав':
            return 'миллиметр'
        elif word == 'метр':
            return 'метр'
        elif word == 'час':
            return 'час'
        elif word == 'мин':
            return 'минута'
    elif number % 10 >= 2 and number % 10 <= 4 and (number % 100 < 10 or number % 100 > 20):
        if word == 'град':
            return 'градуса'
        elif word == 'дав':
            return 'миллиметра'
        elif word == 'метр':
            return 'метра'
        elif word == 'час':
            return 'часа'
        elif word == 'мин':
            return 'минуты'
    else:
        if word == 'град':
            return 'градусов'
        elif word == 'дав':
            return 'миллиметров'
        elif word == 'метр':
            return 'метров'
        elif word == 'час':
            return 'часов'
        elif word == 'мин':
            return 'минут'

# говорит температуру
def say_temperature():
    observation = mgr.weather_at_coords(*g.latlng)
    w = observation.weather
    config_dict = get_default_config()
    config_dict['language'] = 'ru'

    t = w.temperature("celsius")
    t_now = round(t['temp']) # температура сейчас
    t_feels = round(t['feels_like']) # как ощущается
    t_max = round(t['temp_max']) # максимальная температура
    t_min = round(t['temp_min']) # минимальная

    if nowFlag is True:
        commandText = f'Сейчас температура воздуха {t_now} {how_to_say(t_now, "град")}, ощущается как {t_feels} {how_to_say(t_feels, "град")}.'
        if turnFlag:
            entry_1.delete('0.0', 'end')
            entry_1.insert('0.0', commandText)
            entry_1.update()
            withdraw_message(commandText)
        else:
            entry_1.delete('0.0', 'end')
            entry_1.insert('0.0', commandText)

            entry_1.update()
        
    elif nowFlag is False:
        commandText = f'Сегодня максимальная температура воздуха составит {t_max} {how_to_say(t_max, "град")},'
        + f'минимальная - {t_min} {how_to_say(t_min, "град")}. На данный момент температура воздуха составляет {t_now} {how_to_say(t_now, "град")},'
        + f'ощущается как {t_feels} {how_to_say(t_feels, "град")}'
        if turnFlag:
            entry_1.delete('0.0', 'end')
            entry_1.insert('0.0', commandText)

            entry_1.update()
            withdraw_message(commandText)
        else:
            entry_1.delete('0.0', 'end')
            entry_1.insert('0.0', commandText)

            entry_1.update()
      

# говорит атмосферное давление
def say_pressure():
    observation = mgr.weather_at_coords(*g.latlng)
    w = observation.weather
    config_dict = get_default_config()
    config_dict['language'] = 'ru'

    pr = round(w.pressure['press'] * 0.75)
    commandText = f'Атмосферное давление составляет {pr} {how_to_say(pr, "дав")} ртутного столба.'
    if turnFlag:
        entry_1.delete('0.0', 'end')
        entry_1.insert('0.0', commandText)

        entry_1.update()
        withdraw_message(commandText)
    else:
        entry_1.delete('0.0', 'end')
        entry_1.insert('0.0', commandText)

        entry_1.update()
    

# говорит влажность
def say_humidity():
    observation = mgr.weather_at_coords(*g.latlng)
    w = observation.weather
    config_dict = get_default_config()
    config_dict['language'] = 'ru'

    hum = w.humidity
    commandText = f'Влажность сегодня составляет {hum} %.'
    if turnFlag:
        entry_1.delete('0.0', 'end')
        entry_1.insert('0.0', commandText)

        entry_1.update()
        withdraw_message(commandText)
    else:
        entry_1.delete('0.0', 'end')
        entry_1.insert('0.0', commandText)

        entry_1.update()
    

# говорит облачность
def say_clouds():
    observation = mgr.weather_at_coords(*g.latlng)
    w = observation.weather
    config_dict = get_default_config()
    config_dict['language'] = 'ru'

    cl = w.clouds
    commandText = f'Сегодня облачность {cl} %.'
    if turnFlag:
        entry_1.delete('0.0', 'end')
        entry_1.insert('0.0', commandText)

        entry_1.update()
        withdraw_message(commandText)
    else:
        entry_1.delete('0.0', 'end')
        entry_1.insert('0.0', commandText)

        entry_1.update()
    

# говорит текущее время
def say_time():
    time = (datetime.datetime.now()).strftime('%H:%M')

    commandText = f"Сейчас {time}"
    if turnFlag:
        entry_1.delete('0.0', 'end')
        entry_1.insert('0.0', commandText)

        entry_1.update()
        withdraw_message(commandText)
    else:
        entry_1.delete('0.0', 'end')
        entry_1.insert('0.0', commandText)

        entry_1.update()

def say_wind():
    observation = mgr.weather_at_coords(*g.latlng)
    w = observation.weather
    config_dict = get_default_config()
    config_dict['language'] = 'ru'

    wind = w.wind()['speed']
    commandText = f'Сегодня скорость ветра {wind} ' + how_to_say(wind, 'метр') + ' в секунду.'
    if turnFlag:
        entry_1.delete('0.0', 'end')
        entry_1.insert('0.0', commandText)
        entry_1.update()
        withdraw_message(commandText)
    else:
        entry_1.delete('0.0', 'end')
        entry_1.insert('0.0', commandText)
        entry_1.update()

def say_fallout():
    observation = mgr.weather_at_coords(*g.latlng)
    w = observation.weather
    config_dict = get_default_config()
    config_dict['language'] = 'ru'

    gs = goslate.Goslate()

    fl = gs.translate(w.detailed_status, 'ru').capitalize()
    commandText = f'{fl}.'
    if turnFlag:
        entry_1.delete('0.0', 'end')
        entry_1.insert('0.0', commandText)
        entry_1.update()
        withdraw_message(commandText)
    else:
        entry_1.delete('0.0', 'end')
        entry_1.insert('0.0', commandText)
        entry_1.update()



# слушает команду
def listen_command():
    global nowFlag
    recognizer = sr.Recognizer()
    microphone = sr.Microphone(device_index=1)
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.1) 
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio, language='ru-RU').lower()

        if 'сейчас' in command:
            nowFlag = True

        elif 'сейчас' not in command:
            nowFlag = False
        
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
    exitFlag = False
    for c,v in opts['cmds'].items():
        for x in v:
            vrt = fuzz.ratio(command, x)#степень похожести
            if (vrt > RC['percent']) and (vrt >= 50):
                RC['cmd'] = c
                RC['percent'] = vrt
    

    return RC

# выполнение комманды
def do_command(command):
    if command == "temp":
        #if "сейчас" in command:
            #say_temperature(True)
        #else:
            #say_temperature(False)
        say_temperature()

    elif command == "press":
        say_pressure()

    elif command == "hum":
        say_humidity()

    elif command == "cloud":
        say_clouds()
        
    elif command == "fl":
        say_fallout() 
    elif command == "time":
        say_time()
    
    elif command == "wind":
        say_wind()

    else:
        if turnFlag:
            entry_1.delete('0.0', 'end')
            entry_1.insert('0.0', 'Простите, я Вас не поняла.')
            entry_1.update()
            withdraw_message('Простите, я Вас не поняла.')
        else:
            entry_1.delete('0.0', 'end')
            entry_1.insert('0.0', 'Простите, я Вас не поняла.')
            entry_1.update()

#проговаривание аудиосообщения
def withdraw_message(message):
    tts.say(message)
    tts.runAndWait()
    tts.stop()

def main_func():
    withdraw_message("Здравствуйте, чем я могу помочь?")
    try:
        command = listen_command()
        do_command(command['cmd'])
    except:
        pass

turnFlag = True

def butt_press(event):
    global turnFlag 
    if turnFlag:
        earphones_indicator.config(image=earphonesOff_image)
        turnFlag = False
    else:
        earphones_indicator.config(image=earphonesOn_image)
        turnFlag = True


def talk_button_pressed(event):
    talk_button.configure(state=DISABLED)
    main_func()

    talk_button.configure(state=NORMAL)
    talk_button.update()

window = Tk()

window.geometry("711x426")
window.configure(bg = "#3B6C9B")


canvas = Canvas(
    window,
    bg = "#3B6C9B",
    height = 426,
    width = 711,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x = 0, y = 0)
background_image = PhotoImage(
    file=relative_to_assets("background.png"))
background = canvas.create_image(
    355.0,
    213.0,
    image=background_image

)

cat_image = PhotoImage(
    file=relative_to_assets("cat.png"))
cat = canvas.create_image(
    558.0,
    279.0,
    image=cat_image
)

talk_button_image = PhotoImage(
    file=relative_to_assets("talk_button.png"))
talk_button = Button(
    image=talk_button_image,
    bg="#3B6C9B",
    activebackground="#3B6C9B",
    borderwidth=0,
    highlightthickness=0,
    relief="flat"
)
talk_button.place(
    x=177.0,
    y=283.0,
    width=217.0,
    height=56.0
)


textfield_image = PhotoImage(
    file=relative_to_assets("textfield.png"))
textfield = canvas.create_image(
    286.0,
    153.5,
    image=textfield_image
)
entry_1 = Text(
    bd=0,
    bg="#FFFFFF",
    highlightthickness=0,
    #state=DISABLED
)
entry_1.place(
    x=142.0,
    y=67.0,
    width=288.0,
    height=173.0
)


microphone_image = PhotoImage(
    file=relative_to_assets("microOn.png"))
microphone_indicator = canvas.create_image(
    31.0,
    392.0,
    image=microphone_image
)

winmm= windll.winmm
if(winmm.waveInGetNumDevs() >= 1):
    microphone_image = PhotoImage(file=relative_to_assets("microOn.png"))
    microphone_indicator = canvas.create_image(
    31.0,
    392.0,
    image=microphone_image
)
elif(winmm.waveInGetNumDevs() == 0):
    microphone_image = PhotoImage(file=relative_to_assets("microOff.png"))
    microphone_indicator = canvas.create_image(
    31.0,
    392.0,
    image=microphone_image
)

earphonesOff_image = PhotoImage(
    file=relative_to_assets("earphonesOff.png"))

earphonesOn_image = PhotoImage(
    file=relative_to_assets("earphonesOn.png"))

earphones_indicator = Button(
    image=earphonesOn_image,
    bg="#3B6C9B",
    activebackground="#3B6C9B",
    borderwidth=0,
    highlightthickness=0,
    relief="flat"
)
earphones_indicator.place(
    x=69.0,
    y=377.0,
    width=30.0,
    height=30.0
)


window.resizable(False, False)
window.title("IWeather")
window.iconphoto(False, PhotoImage(file=relative_to_assets("cloud.ico")))
earphones_indicator.bind('<Button-1>', butt_press)
talk_button.bind('<Button-1>', talk_button_pressed)
window.mainloop()