import webapp2
import logging
import re
import cgi
import jinja2
import os
import time

from google.appengine.ext import db

newpost = {"ph_subject": "", "ph_content": "", "ph_error": ""}


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

class BlogHandler(webapp2.RequestHandler):
    def write(self, *items):    
        self.response.write(" : ".join(items))

    def render_str(self, template, **params):
        tplt = JINJA_ENVIRONMENT.get_template('templates/'+template)
        return tplt.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
   ## DEFINE YOUR DATABASE PROPERTIES HERE
    subject = db.StringProperty()
    content = db.TextProperty()
    created = db.DateTimeProperty(auto_now=True)

class BlogFront(BlogHandler):
    def get(self):
        logging.debug("BlogHandler get")
      ## get 10 most recent posts from data base
      ## render all the posts using the posts.html template
        
        posts = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC limit 10")
        logging.info(posts)
        self.render("posts.html", posts=posts)


class Permalink(BlogHandler):
    def get(self, post_id):
      ## get post with the id post_id
      ## render the self.render("permalink.html",post=post)
        post = {"subject": "", "content": "", "created": time.time(), "error": ""}
        post["subject"] = Blog.get_by_id(int(post_id)).subject
        post["content"] = Blog.get_by_id(int(post_id)).content
        post["created"] = Blog.get_by_id(int(post_id)).created.date().strftime("%c")
        self.render("permalink.html", **post)

class NewPost(BlogHandler):
    def get(self):
      ## render the blank blog form
        self.render("newpost.html", **newpost)
    def post(self):
        logging.debug("NewPost post")
    ## get what the user typed into the form
        newpost["subject"] = self.request.get("subject")
        newpost["content"] = self.request.get("content")
    ## verify that what the user typed in
    ## if what user typed in is good
        self.blog = Blog()
        if (newpost["subject"] and newpost["content"]):
      ##   put the the information in the database
            self.blog.subject = newpost["subject"]
            self.blog.content = newpost["content"]
            self.blog.put()
            time.sleep(0.2)
      ##    get the id of the database entry 
            id = self.blog.key().id()
            self.redirect("/permalink/" + str(id))
        else:
      ##   render the newpost page with an error message
            #self.response.write("error")
            newpost["error"] = "Please provide input in both fields"
            self.render("newpost.html", **newpost)

class MainPage(BlogHandler):
    def get(self):
      ## redirect to /blog
      self.redirect("/blog/")

app = webapp2.WSGIApplication([
   ('/', MainPage),
   (r'/blog.*', BlogFront),
   (r'/newpost.*', NewPost), #r'REGEX', NewPost),
   (r'/permalink/(\d+)', Permalink),
], debug=True)
