#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import cgi, re, webapp2, jinja2, os

# Environment setup
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])
# a working form
#form = {"username": "bennet", "password": "bennet", "verify": "bennet", "email": "bennetleff@gmail.com"}
# empty form
form = {"username": "", "password": "", "verify": "", "email": ""}

template = JINJA_ENVIRONMENT.get_template('templates/main.html')

class MainHandler(webapp2.RequestHandler):
    def validUsername(self, username):
        if (re.match(r"^[a-z0-9_-].{3,20}", username)):
            return True
        else:
            return False
    def validPassword(self, password):
        if (re.match(r"^[a-z0-9_-].{3,20}", password)):
            return False
        else:
            return True
    def validVerify(self, password, verify):
        if (password != verify):    
            return False
        else:
            return True
    def validEmail(self, email):
        if (re.match(r"[\w._%-]+@[\w.-]+.[a-zA-z]{2,4}", email)):
            return True
        else:
            return False
    def get(self):
        self.response.write(template.render(form))    
    def post(self):
        username = self.validUsername(str(self.request.get('username')))
        password = self.validUsername(str(self.request.get('password')))
        verify = self.validVerify(str(self.request.get('password')), str(self.request.get('verify')))
        email = self.validEmail(str(self.request.get('email')))
        if not (username):
            self.get()
            self.response.write('<p style="color:red;">Invalid username</p>')
        elif (not password):
            self.get()
            self.response.write('<p style="color:red;">Invalid password</p>')
        elif (not verify):
            self.get()
            self.response.write('<p style="color:red;">Passwords do not match</p>')
        elif (not email):
            self.get()
            self.response.write('<p style="color:red;">Invalid email</p>')
        else:
            self.redirect("/success")
    def escape_html(s):
        return cgi.escape(s, quoute = True)

class SuccessHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write("Welcome")

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ("/success", SuccessHandler)
], debug=True)
