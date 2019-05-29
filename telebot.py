import telebot
import requests
from time import time
import datetime
from datetime import *
from datetime import datetime
from datetime import timedelta, datetime, time

access_token = ''
# Создание бота с указанным токеном доступа
bot = telebot.TeleBot(access_token)





def get_page(group, week=''):
    if week:
        week = str(week) + '/'
    url = 'http://www.ifmo.ru/ru/schedule/0/{group}/{week}raspisanie_zanyatiy_{group}.htm'.format(

        week=week, 
        group=group)
    response = requests.get(url)
    web_page = response.text
    return web_page
    

web_page=get_page('M3110')
from bs4 import BeautifulSoup


def get_schedule(web_page, day='monday'):
    soup = BeautifulSoup(web_page,"html5lib")
    if type(day) != int:
        days = ['0', 'monday', 'tuesday','wednesday', 'thursday', 'friday', 'saturday']
        for i in range(0,len(days)):
            if day.replace('/','') == days[i]:
                day = str(i)+'day'
        #print(day)
    else:
        day = str(day)+'day'
    # Получаем таблицу с расписанием на понедельник
    schedule_table = soup.find("table", attrs={"id": day})
    # Время проведения занятий
    times_list = schedule_table.find_all("td", attrs={"class": "time"})
    times_list = [time.span.text for time in times_list]

    # Место проведения занятий
    locations_list = schedule_table.find_all("td", attrs={"class": "room"})
    locations_list = [room.span.text for room in locations_list]


    # Название дисциплин и имена преподавателей
    lessons_list = schedule_table.find_all("td", attrs={"class": "lesson"})
    lessons_list = [lesson.text.split('\n\n') for lesson in lessons_list]
    lessons_list = [', '.join([info for info in lesson_info if info]) for lesson_info in lessons_list]
    lessons_list2=[]
    lessons_list3=[]
    for i in range(0,len(lessons_list)):
        lessons_list2.append(lessons_list[i].replace('\t',''))
        lessons_list3.append(lessons_list2[i].replace('\n',''))


    # Номер кабинета
    rooms_list = schedule_table.find_all("td", attrs={"class": "room"})
    rooms_list = [room.dd.text for room in rooms_list]
    #print(rooms_list)
    return times_list, locations_list, lessons_list3, rooms_list
#print(get_schedule(web_page,day))

@bot.message_handler(commands=['monday', 'tuesday','wednesday', 'thursday', 'friday', 'saturday'])
def get_timetable(message):
    ch_nech=0
    day='monday'
    group = 'M3110'
    try:
        day, ch_nech, group = message.text.split()
    except:
        pass
    #print(day)
    web_page = get_page(group,ch_nech)
    times_lst, locations_lst, lessons_lst, rooms_lst = get_schedule(web_page,day)

    resp = ''
    for time, location, lession, room in zip(times_lst, locations_lst, lessons_lst, rooms_lst):
        resp += '<b>{}</b>, {}, {}, {}\n'.format(time, location, lession, room)

    bot.send_message(message.chat.id, resp, parse_mode='HTML')

@bot.message_handler(commands=['tommorow'])
def get_tommorow(message):
    my_date = date.today()
    today = my_date.isoweekday()+1
    if today == 8:
        today = 1
    elif today == 7:
        today = 1
    group = 'M3110'
    try:
        a, group = message.text.split()
    except:
        pass
    web_page = get_page(group)
    times_lst, locations_lst, lessons_lst, rooms_lst = get_schedule(web_page,today)

    resp = ''
    for time, location, lession, room in zip(times_lst, locations_lst, lessons_lst, rooms_lst):
        resp += '<b>{}</b>, {}, {}, {}\n'.format(time, location, lession, room)

    bot.send_message(message.chat.id, resp, parse_mode='HTML')
@bot.message_handler(commands=['all'])
def get_all(message):
    ch_nech=0
    group='M3110'
    try:
        a, ch_nech, group = message.text.split()
    except:
        pass
    resp = ''
    web_page = get_page(group,ch_nech)
    j=0
    list_d=['ПОНЕДЕЛЬНИК', 'ВТОРНИК','СРЕДА', 'ЧЕТВЕРГ', 'ПЯТНИЦА', 'СУББОТА']
    list_s=['monday', 'tuesday','wednesday', 'thursday', 'friday', 'saturday']
    for i in list_s:
        times_lst, locations_lst, lessons_lst, rooms_lst = get_schedule(web_page,i)
        resp += '\n\n<b>{}</b>\n'.format(list_d[j])
        for time, location, lession, room in zip(times_lst, locations_lst, lessons_lst, rooms_lst):
            resp += '<b>{}</b>, {}, {}, {}\n'.format(time, location, lession, room)
        j+=1
    resp += '\n\n<b>{}</b>\n'.format('ВОСКРЕСЕНЬЕ - ВЫХОДНОЙ!!!!')   
    bot.send_message(message.chat.id, resp, parse_mode='HTML')

@bot.message_handler(commands=['near_lesson'])
def get_near(message):
    sunday = False
    a = 0
    my_date=datetime.today()
    my_time=my_date.time()
    my_time = str(my_time)
    today = my_date.isoweekday()
    if int(today) == 7:
    	sunday = True
    	today = 1
    group = 'M3110'
    try:
        a, group = message.text.split()
    except:
        pass
    web_page = get_page(group)
    times_lst, locations_lst, lessons_lst, rooms_lst = get_schedule(web_page,today)
    hour=my_time[0:2]
    if hour[0]=='0':
        hour = int(hour[1])
    minn=my_time[3:5]
    if minn[0]=='0':
        minn = int(minn[1])
    for i in range(0,len(times_lst)):
        print(int(str(times_lst[i])[0:2]),int(hour))
        try:
            if int(str(times_lst[i])[0:2]) > int(hour):
                break
            if int(str(times_lst[i])[0:2]) == int(hour):
                if int(str(times_lst[i])[3:5]) > int(minn):
                    break
        except:
            if i == (len(times_lst)+1):
                if sunday:
                    a = 0
                    print('true')
                else:
                    a = 1
                    print('false')
                i = 0
                times_lst, locations_lst, lessons_lst, rooms_lst = get_schedule(web_page,int(today)+a)
                break
    resp = '<b>{}</b>, {}, {}, {}\n'.format(times_lst[i], locations_lst[i],  lessons_lst[i], rooms_lst[i])

    bot.send_message(message.chat.id, resp, parse_mode='HTML')

@bot.message_handler(commands=['help','info'])
def get_near(message):
    m = '<b>Привет!</b>\nЯ могу предсказать расписание любой группы:\n\n'
    m += 'полностью:\n<b>/all</b> НЕДЕЛЯ (1-ч. 2-неч.) ГРУППА\n\n'
    m += 'на следующий день:\n<b>/tommorow</b> ГРУППА\n\n'
    m += 'на определенный день:\n<b>/monday</b> НЕДЕЛЯ ГРУППА\n\n'
    m += 'ближайшее занятие:\n<b>/near_lesson</b> ГРУППА'
    bot.send_message(message.chat.id, m, parse_mode='HTML')

if __name__ == '__main__':
    bot.polling(none_stop=True)
