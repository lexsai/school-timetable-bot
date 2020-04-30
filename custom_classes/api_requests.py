import re
import json

import aiohttp
from bs4 import BeautifulSoup
from discord.ext import commands

import custom_classes as cc

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

async def parse_today_classes(html):
    soup = BeautifulSoup(html, 'html.parser')

    today_classes_html = soup.findAll('td', {'class' : 'timetable-dayperiod today'})
    today_classes = [{'title' : today_class.find('strong').text,
                      'info' : today_class.find('br').text} for today_class in today_classes_html]

    return today_classes

async def parse_current_class(html):
    soup = BeautifulSoup(html, 'html.parser')

    current_classes_html = soup.findAll('tr', {'class' : 'now'})

    try:
        current_class_html = [current.find('td', {'class' : 'timetable-dayperiod today'}) 
                              for current in current_classes_html 
                              if current.find('td', {'class' : 'timetable-dayperiod today'}) != None][0]
    except IndexError:
        return None

    current_class = {'title' : current_class_html.find('strong').text, 
                     'info' :  current_class_html.find('br').text}    

    return current_class

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
            identity = cc.get_identity(ctx)[0]
            student_info = await query_student_info(session, identity.split('|')[0])

        except Exception as e:
            print(e)
            raise commands.BadArgument

    return student_info
