from datetime import datetime, timedelta
from calendar import HTMLCalendar
from .models import Assignment

class Calendar(HTMLCalendar):
	def __init__(self, year=None, month=None):
		self.year = year
		self.month = month
		super(Calendar, self).__init__()

	def formatday(self, day, month, year, assignments):
		events_per_day = assignments
		d = ''
		for event in events_per_day:
			if (event.deadline.day == day) and (event.deadline.year == year) and (event.deadline.month == month):
				d += f'<li> {event.title} </li>'

		if day != 0:
			return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
		return '<td></td>'

	def formatweek(self, theweek, assignments):
		week = ''
		for d, weekday in theweek:
			week += self.formatday(d, assignments)
		return f'<tr> {week} </tr>'

	def formatmonth(self, request_user):
                assignments = Assignment.objects.filter(user=request_user)

                next_month = self.month + 1
                if (next_month > 12):
                        next_month = 1
                        next_year = self.year + 1
                else:
                        next_year = self.year
        
                prev_month = self.month - 1
                if (prev_month < 1):
                        prev_month = 12
                        prev_year = self.year - 1
                else:
                        prev_year = self.year
                        
                cal = f'<table class="calendar table">\n'
                #<tr>
                cal += f'<a class="btn btn-info left" href="/organizer/assignments/view/calendar/{prev_month}/{prev_year}"> Previous Month </a>'
                #< th>
                cal += f'{self.formatmonthname(self.year, self.month, withyear=True)}\n'
                #</th>
                cal += f'<a class="btn btn-info left" href="/organizer/assignments/view/calendar/{next_month}/{next_year}"> Next Month </a>'
                #<tr>
                cal += f'{self.formatweekheader()}\n'
                for week in self.monthdays2calendar(self.year, self.month):
                        cal += "<tr>"
                        for d, weekday in week:
                                cal += self.formatday(d, self.month, self.year, assignments)
                        cal += "</tr>"
                cal += "</table>"
                return cal

