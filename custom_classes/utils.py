import re
from enum import Enum

class SchoolDays(Enum):
	MONDAY = 0
	TUESDAY = 1
	WEDNESDAY = 2
	THURSDAY = 3
	FRIDAY = 4

def get_identity(ctx):
	r = re.compile(r'[a-z A-Z-]*\, [a-z A-Z-]*\|\d{1,}')
	identity = [r.match(role.name).string
     			for role in ctx.author.roles 
				if r.match(role.name)]
	return identity

def parse_timetable(prefix, periods):
    period_classes = {}
    colspans = []
    for period in periods:
        row_classes = period.find_parent('tr').findAll('td')
        parsed_row_classes = []

        for colspan in colspans:
            parsed_row_classes.insert(colspan, "HOLIDAY")  

        for i in range(len(row_classes)):
            parsed_row_classes.append(row_classes[i])

            if 'timetable-holiday' in row_classes[i]['class']:
                colspans.append(i)

        period_classes[f'{prefix}{period.text.strip()}'] = parsed_row_classes

    return period_classes

def format_description(description): 
	return '\n'.join([line.strip() 
					 for line in description.split('\n') 
					 if line.strip() != ''])