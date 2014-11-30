import webapp2
import logging
import re
import cgi
import jinja2
import os
import hashlib
from hashes import *
from google.appengine.ext import db

## see http://jinja.pocoo.org/docs/api/#autoescaping
def guess_autoescape(template_name):
   if template_name is None or '.' not in template_name:
      return False
      ext = template_name.rsplit('.', 1)[1]
      return ext in ('html', 'htm', 'xml')

JINJA_ENVIRONMENT = jinja2.Environment(
   autoescape=guess_autoescape,     ## see http://jinja.pocoo.org/docs/api/#autoescaping
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

class Handler(webapp2.RequestHandler):
    def write(self, *items):    
        self.response.write(" : ".join(items))

    def render_str(self, template, **params):
        tplt = JINJA_ENVIRONMENT.get_template('templates/'+template)
        return tplt.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(Handler):   
    def get(self):
        logging.info("********** MainPage GET **********")
        self.response.headers['Content-Type'] = 'text/plain'
        ##1 Assign the variable 'visits' to the value of the 'visits' 
        ##1 cookie obtained from the browsers HTTP response. If the cookie 
        ##1 does not exist, set the variable 'visits' to '0'
        visits = self.request.cookies.get('visits', make_secure_value(0))
        logging.info(visits)
        ##2 If the variable visits is an integer (i.e. use str.isdigit())
        ##2 increment visits by 1
        ##2 else set visits to 0
        if (check_secure_value(visits)): # if the hash is untampered
            visits = int(check_secure_value(visits)) # visits = int val of hash 
            visits += 1 # visits increases by one
            logging.info(visits)
            self.response.headers.add_header("Set-Cookie", "visits={0}".format(make_secure_value(visits)))
            ##3 Add the 'Set-Cookie:' header with the value set to the 
            ##3 variable 'visits' to the HTTP response
            ##4 if visits > 10000, 
            ##4   write out a congratulations message
            if (visits > 10000):
                self.response.write("Congrats")
            ##4 else
            ##4   write out a message stating how many times the user has visited
            else:
                self.response.write("You have visited %s times" % visits)
        else:
            self.response.write("Don't mess with my cookie!!!!\n")
        
        

    def post(self):
        logging.info("DBG: MainPage POST")

app = webapp2.WSGIApplication([
    ('/', MainPage)
], debug=True)
