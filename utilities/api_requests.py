import re
import json

import aiohttp
from bs4 import BeautifulSoup
from discord.ext import commands

import utilities as util

async def fetch_student(session, query):
    params = {
        'query' : query,
        'search_inactive' : 'false',
        'show_external_id' : 'false'
    }

    resp = await session.request('get', 'https://web1.normanhurb-h.schools.nsw.edu.au/timetables/ajax/searchStudents', params = params)
    return await resp.text()

async def fetch_timetable(session, student_id):
    resp = await session.request('get', 
                                 'https://web1.normanhurb-h.schools.nsw.edu.au/timetables/timetable', 
                                  params = {'student' : str(student_id)})

    return await resp.text()

def find_period_classes(html):
    soup = BeautifulSoup(html, 'html.parser')

    periods = [period for period in 
               soup.findAll('th', {'class' : 'timetable-period'})
               if re.match(r'P\d{1}', period.text)]

    return periods

def parse_period_classes(html):
    periods = find_period_classes(html)

    weekA, weekB = periods[:len(periods)//2], periods[len(periods)//2:]

    period_classes = {**util.parse_timetable('a',weekA), **util.parse_timetable('b',weekB)}

    return period_classes

def find_today_classes(html):
    periods = parse_period_classes(html)

    today_classes_html = []
    for period, classes in periods.items():
        for _class in classes:
            try:
                if 'today' in _class['class']:
                    today_classes_html.append((period, _class.find('div', {'class' : 'timetable-class'})))
            except TypeError:
                pass

    today_classes = [{'period' : today_class[0],
                      'info' : {'title' : today_class[1].find('strong').text,
                                'description' : today_class[1].find('br').text}} for today_class in today_classes_html 
                                if today_class[1]]

    return today_classes

def find_current_class(html):
    periods = find_period_classes(html)

    current_class_html = None
    for period in periods:
        now_row = period.find_parent('tr', {'class' : 'now'})
        if now_row:
            current_class = now_row.find('td', {'class' : 'timetable-dayperiod today'})
            if current_class:
                current_class_html = (period, current_class)

    if current_class_html:    
        current_class = {'period' : current_class_html[0],
                         'info' : {'title' : current_class_html[1].find('strong').text,
                                   'description' : current_class_html[1].find('br').text}}
    else:
        current_class = None

    return current_class

def find_next_class(html):
    periods = find_period_classes(html)

    for period in periods:
        now_row = period.find_parent('tr', {'class' : 'now'})
        if now_row:
            next_class = now_row.next_sibling.next_sibling.find('td', {'class' : 'timetable-dayperiod today'})
            if next_class:
                next_class_html = (period, next_class)

    if next_class_html:    
        next_class = {'period' : str(int(next_class_html[0].text[1:]) + 1),
                         'info' : {'title' : next_class_html[1].find('strong').text,
                                   'description' : next_class_html[1].find('br').text}}
    else:
        next_class = None

    return next_class

def find_day_classes(week, day_index, html):
    periods = parse_period_classes(html)

    day_classes_html = []
    for period, _class in periods.items():
        if period.startswith(week):
            try:
                day_classes_html.append((period, _class[day_index].find('div', {'class' : 'timetable-class'})))
            except TypeError:
                pass

    day_classes = [{'period' : day_class[0],
                      'info' : {'title' : day_class[1].find('strong').text,
                                'description' : day_class[1].find('br').text}} for day_class in day_classes_html 
                                if day_class[1]]

    return day_classes

def find_date(html):
    soup = BeautifulSoup(html, 'html.parser')

    day_overview = soup.find('th', {'class' : 'timetable-day today'})
    weekday = soup.find('th', {'class' : 'timetable-date today'})

    return util.week_from_tag(day_overview), util.SchoolDays[weekday.text.upper()]

async def query_student_info(session, query):
    try: 
        query_resp = await fetch_student(session, query)
        student_info = json.loads(query_resp)['results'][0]
    except (IndexError, TypeError) as e:
        raise commands.BadArgument
        return

    return student_info

async def find_student_info(ctx, session, query):
    if query is not None:
        student_info = await query_student_info(session, query)
    else:
        try:
            identity = util.get_identity(ctx)[0]
            student_info = await query_student_info(session, identity.split('|')[0])

        except Exception as e:
            print(e)
            raise commands.BadArgument

    return student_info
