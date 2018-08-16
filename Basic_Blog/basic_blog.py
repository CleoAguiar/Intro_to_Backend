# Copyright 2016 Google Inc.
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

import webapp2

import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

class Handler(webapp2.RequestHandler):
    """docstring for Handler"""
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class Blog(db.Model):
    subject = db.StringProperty(required=True)
    blog = db.TextProperty(required=True)
    created = db.DateProperty(auto_now_add=True)
        

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write('Basic Blog!')


class MyBlog(Handler):
    """docstring for MyBlog"""
    def get(self):
        self.render("myblog.html")


class NewPost(Handler):
    """docstring for NewPost"""
    def render_front(self, subject="", blog="", error=""):
        # blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC")

        self.render("newpost.html", subject=subject, blog=blog, error=error)

    def get(self):
        self.render_front()

    def post(self):
        subject = self.request.get("subject")
        blog = self.request.get("blog")

        if subject and blog:
            b = Blog(subject=subject, blog=blog)
            b.put()
            self.redirect("/" + b.key().id())
            # self.response.write("OK")

        else:
            error = "We need both a Subject and some Blog!"
            self.render_front(subject, blog, error)
        

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', MyBlog),
    ('/blog/newpost', NewPost),
], debug=True)
