import webapp2
import random
form = """
<form method="post" action="/testform">
<input name="q">
<input type="submit">
</form>
"""

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(form)

class TestHandler(webapp2.RequestHandler):
    randNum = random.randrange(1, 100)
    def post(self):
        q = int(self.request.get("q")) # get 'q' from request
        self.response.write(q)     # response from server
        self.response.write("Hello")
        if (q == randNum):
            self.response.write("Good Job")
        else:
            self.response.write(form)
            if (randNum > q):
                self.response.write("lower")
            else:
                self.response.write("higher")

application = webapp2.WSGIApplication([
    ('/', MainPage),   # maps the URL '/' to MainPage
    ('/testform', TestHandler),   
], debug=True)

