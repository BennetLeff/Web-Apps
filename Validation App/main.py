import webapp2
import logging
import cgi

form = """
<form method="post">
What is your birthday?
<br>
<label> Month <input type="text" name="month" value="%(month)s"> </label>
<label> Day <input type="text" name="day" value="%(day)s"> </label>
<label> Year <input type="text" name="year" value="%(year)s"> </label>
<input type="submit">
<br>
</form>
"""

class MainPage(webapp2.RequestHandler):
    def valid_day(self, day):
        if (day.isdigit()):
            if (int(day) > 0 and int(day) < 31):
                return int(day)
    def valid_month(self, month):
        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        for i in months:
            if (i == month): 
                return month[:3] 
    def valid_year(self, year):
        if (year.isdigit()):
            if (int(year) > 1900 and int(year) < 2020):
                return int(year)
    def get(self):
        self.response.write(form % {"month":"month", "day":"day", "year":"year"})
    def post(self):
        user_day = self.valid_day(self.request.get('day'))
        user_month = self.valid_month(self.request.get('month'))
        user_year = self.valid_year(self.request.get('year'))
        if not (user_day and user_month and user_year):
            wrongAns = cgi.escape(str(self.request.get('month')), True) + " " + cgi.escape(str(self.request.get('day')), True) + ", " + cgi.escape(str(self.request.get('year')), True)
            self.response.write("""%s is not a valid date!<br>""" % wrongAns)
            self.response.write(form % {"month":self.request.get('month'), "day":self.request.get('day'), "year":self.request.get('year')})
        else:
            self.response.write(str(user_month) + " " + str(user_day) + ", " + str(user_year) + "\n")
            self.response.write("is a totally valid date!")
    def escape_html(s):
        return cgi.escape(s, quoute = True)

app = webapp2.WSGIApplication([
    ('/', MainPage),   # maps the URL '/' to MainPage
    #('/testform', TestHandler),   
], debug=True)