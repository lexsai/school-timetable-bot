import asyncio
import json

import aiohttp
from bs4 import BeautifulSoup

async def fetch_student(session, query):
    params = {
        'query' : query,
        'search_inactive' : 'false',
        'show_external_id' : 'false'
    }

    resp = await session.request('get', 'https://web1.normanhurb-h.schools.nsw.edu.au/timetables/ajax/searchStudents', params = params)
    print('[QUERY]', resp.status, resp.reason)  
    return await resp.text()

async def fetch_timetable(session, student_id):
    resp = await session.request('get', 
                                 'https://web1.normanhurb-h.schools.nsw.edu.au/timetables/timetable', 
                                  params = {'student' : str(student_id)})

    print('[TIMETABLE]', resp.status, resp.reason)  
    return await resp.text()

async def main():
    async with aiohttp.ClientSession() as session:
        query_resp = await fetch_student(session, 'andrew huang')
        student_info = json.loads(query_resp)['results'][0]

        timetable_html = await fetch_timetable(session, student_info['id'])

        soup = BeautifulSoup(timetable_html, 'html.parser')

        timetabled_classes = soup.findAll('td', {'class' : 'timetable-dayperiod today'})

        print([today_class.find('strong').text for today_class in timetabled_classes])

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())