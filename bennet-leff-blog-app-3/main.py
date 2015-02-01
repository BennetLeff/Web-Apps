import webapp2
import logging
import re
import cgi
import jinja2
import os
import time
import datetime
import urllib2
from xml.dom import minidom
from hashes import *
from google.appengine.ext import db


# see http://jinja.pocoo.org/docs/api/#autoescaping
def guess_autoescape(template_name):
    if template_name is None or '.' not in template_name:
        return False
    ext = template_name.rsplit('.', 1)[1]
    return ext in ('html', 'htm', 'xml')

JINJA_ENVIRONMENT = jinja2.Environment(
    autoescape=guess_autoescape,     # see http://jinja.pocoo.org/docs/api/#autoescaping
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

# content in a post
newpost = {
    "ph_subject": "",
    "ph_content": "",
    "ph_error": ""
}

# user data
form = {
    'username': {'value': '', 'error': ''},
    'password': {'value': '', 'error': ''},
    'verify': {'value': '', 'error': ''},
    'email': {'value': '', 'error': ''}
}

# --- templates --- #
mainTemplate = JINJA_ENVIRONMENT.get_template('templates/main.html')
loginTemplate = JINJA_ENVIRONMENT.get_template('templates/login.html')
# ----------------- #

def get_coords(ip):
    # uses urlib2 library to "open" any url so I can check any ip with a http get request
    url = urllib2.urlopen("http://freegeoip.net/xml/{0}".format(ip))
    xml = minidom.parseString(url.read())

    lat = xml.getElementsByTagName("Latitude")[0].childNodes[0].nodeValue
    long = xml.getElementsByTagName("Longitude")[0].childNodes[0].nodeValue
    coords = tuple([float(lat), float(long)])

    return db.GeoPt(coords[0], coords[1])


class BlogHandler(webapp2.RequestHandler):
    def write(self, *items):    
        self.response.write(" : ".join(items))

    def render_str(self, template, **params):
        tplt = JINJA_ENVIRONMENT.get_template('templates/'+template)
        return tplt.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class Blog(db.Model):
    # DEFINE YOUR DATABASE PROPERTIES HERE
    subject = db.StringProperty()
    content = db.TextProperty()
    created = db.DateTimeProperty(auto_now=True)
    coords = db.GeoPtProperty()


class BlogFront(BlogHandler):
    def get(self):
        # get 10 most recent posts from data base
        # render all the posts using the posts.html template
        posts = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC limit 10")
        currentuser = self.request.cookies.get('currentuser', "")
        user = db.GqlQuery("SELECT * FROM User WHERE password=:1", currentuser)

        # logging.info(self.request.remote_addr)

        if currentuser:
            self.render("posts.html", posts=posts, username=form['username']['value'])
        else:
            self.redirect('/')


class Permalink(BlogHandler):
    def get(self, post_id):
        # get post with the id post_id
        # render the self.render("permalink.html",post=post)
        post = {
                "subject": "",
                "content": "",
                "created": time.time(),
                "error": "",
                "username": ""
        }
        post["subject"] = Blog.get_by_id(int(post_id)).subject
        post["content"] = Blog.get_by_id(int(post_id)).content
        post["created"] = Blog.get_by_id(int(post_id)).created.date().strftime("%c")
        self.render("permalink.html", **post)


class NewPost(BlogHandler):
    def get(self):
        # render the blank blog form
        self.render("newpost.html", **newpost)
        post_ip = ""

    def post(self):
        # get what the user typed into the form
        newpost["subject"] = self.request.get("subject")
        newpost["content"] = self.request.get("content")
        # newpost["ip_address"] = re.escape(self.request.get("ip_address"))
        post_ip = re.escape(self.request.get("ip_address"))
        # verify that what the user typed in
        # if what user typed in is good
        self.blog = Blog()
        if newpost["subject"] and newpost["content"] and post_ip:
            # put the the information in the database
            self.blog.subject = newpost["subject"]
            self.blog.content = newpost["content"]
            self.blog.coords = get_coords(self.request.get("ip_address"))
            self.blog.put()
            time.sleep(0.2)
            # get the id of the database entry
            id = self.blog.key().id()
            self.redirect("/blog/permalink/" + str(id))
        else:
            # render the newpost page with an error message
            # self.response.write("error")
            newpost["error"] = "Please provide input in all fields"
            self.render("newpost.html", **newpost)


class MainPage(BlogHandler):
    def get(self):
        user = self.request.cookies.get('currentuser', "")
        if not(check_secure_value(user)):
            self.redirect("/blog/signup")
        else:
            self.redirect("/blog/welcome")


class Welcome(BlogHandler):
    def get(self):
        self.response.write("Welcome")


class User(db.Model):
    username = db.StringProperty()
    password = db.StringProperty()
    email = db.StringProperty()


class SignUp(webapp2.RequestHandler):

    def validUsername(self, username):
        return re.match(r"^[a-z0-9_-].{3,20}", username)

    def validPassword(self, password):
        return re.match(r"^[a-z0-9_-].{3,20}", password)

    def validVerify(self, password, verify):
        return password == verify

    def validEmail(self, email):
        return re.match(r"[\w._%-]+@[\w.-]+.[a-zA-z]{2,4}", email)

    def get(self):
        self.response.write(mainTemplate.render(form))    

    def post(self):
        # replace with User class
        username = self.validUsername(str(self.request.get('username')))
        form['username']['value'] = str(self.request.get('username'))
        password = self.validUsername(str(self.request.get('password')))
        verify = self.validVerify(str(self.request.get('password')), str(self.request.get('verify')))
        email = self.validEmail(str(self.request.get('email')))
        if not username:
            form['username']['error'] = 'Invalid Username'
            self.get()
        elif not password:
            form['password']['error'] = 'Invalid Password'
            self.get()
        elif not verify:
            form['verify']['error'] = 'Passwords do not match'
            self.get()
        elif len(self.request.get('email')) > 0 and not email:
            form['email']['error'] = 'Invalid Email'
            self.get()
        else:
            user = db.GqlQuery("SELECT * FROM User WHERE username=:1", self.request.get('username'))
            user = user.get()
            if user:  # users.username == form['username']['value']):
                form['username']['error'] = 'Username taken'
                self.get()
            else:    
                currentuser = User()
                currentuser.username = form['username']['value']
                currentuser.password = make_pw_hash(self.request.get('username'), self.request.get('password'))
                currentuser.email = form['email']['value']
                currentuser.put()
                self.response.headers.add_header('Set-Cookie', 'currentuser={0}; expires={1}; PATH=/'.format(make_secure_value(currentuser.key().id()), datetime.datetime.utcnow() + datetime.timedelta(seconds=60)))
                form['username']['value'] = currentuser.username
                self.redirect('/blog')

    def escape_html(s):
        return cgi.escape(s, quoute = True)


class LogIn(webapp2.RequestHandler):
    def valid_username(self, username):
        return re.match(r"^[a-z0-9_-].{3,20}", username)

    def validPassword(self, password):
        return re.match(r"^[a-z0-9_-].{3,20}", password)

    def validVerify(self, password, verify):
        return password == verify

    def get(self):
        form['username']['value'] == self.request.get('username')
        self.response.write(loginTemplate.render(form))

    def post(self):
        # replace with User class
        username = self.valid_username(str(self.request.get('username')))
        form['username']['value'] = str(self.request.get('username'))
        password = self.valid_username(str(self.request.get('password')))
        if not username:
            form['username']['error'] = 'Invalid Username'
            self.get()
        elif not password:
            form['password']['error'] = 'Invalid Password'
            self.get()
        else:
            user = db.GqlQuery("SELECT * FROM User WHERE username=:1", self.request.get('username'))
            user = user.get()
            if user:  #users.username == form['username']['value']):
                if valid_pw(self.request.get('username'), self.request.get('password'), user.password):
                    self.response.headers.add_header('Set-Cookie', 'currentuser={0}; expires={1}; PATH=/'.format(make_secure_value(user.key().id()), datetime.datetime.utcnow() + datetime.timedelta(seconds=60)))
                    form['username']['value'] = user.username
                    self.redirect('/blog/welcome')
                else:
                    form['username']['error'] = 'Invalid Login'
                    self.get()
            else:
                form['username']['error'] = 'Invalid Login'
                self.get()
        
    def escape_html(s):
        return cgi.escape(s, quoute = True)


class LogOut(webapp2.RequestHandler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', 'currentuser=; PATH=/')
        self.redirect('/blog/signup')


class Map(BlogHandler):
    def get(self):
        all_coords = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC limit 10")
        built_string_of_coords = ""
        for coordinate in all_coords:
            logging.info(coordinate.coords)
            if coordinate.coords:
                built_string_of_coords += "&markers=" + str(coordinate.coords)
        coords = {"coords_string": built_string_of_coords}
        logging.info("coordinate string for google api url is " + coords["coords_string"])
        self.render("map.html", **coords)

app = webapp2.WSGIApplication([
    (r'/', MainPage),
    (r'/blog/welcome.{0,1}', Welcome),
    (r'/blog/login.{0,1}', LogIn),
    (r'/blog/logout.{0,1}', LogOut),
    (r'/blog/signup.{0,1}', SignUp),
    (r'/blog.{0,1}', BlogFront),
    (r'/blog/newpost.{0,1}', NewPost),
    (r'/blog/permalink/(\d+)', Permalink),
    (r'/blog/map', Map),
    # (r'/blog/map.{0,1})', Map),
], debug=True)