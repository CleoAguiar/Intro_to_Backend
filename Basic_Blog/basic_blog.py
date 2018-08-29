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
import re
import random
import string
import hashlib

from google.appengine.ext import db

USER_RE = re.compile("^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile("^.{3,20}$")
EMAIL_RE = re.compile("^[\S]+@[\S]+.[\S]+$")

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

def valid_username(username):
    return username and USER_RE.match(username)


def valid_password(password):
    return password and PASSWORD_RE.match(password)


def valid_email(email):
    return not email or EMAIL_RE.match(email)


# Security
def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))


def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s|%s' % (salt, h)


def valid_pw(name, pw, h):
    salt = h.split('|')[0]
    return h == make_pw_hash(name, pw, salt)


def blog_key(name='default'):
    return db.Key.from_path('blogs', name)


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


class Handler(webapp2.RequestHandler):
    """docstring for Handler"""
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class MainPage(Handler):
    def get(self):
        self.response.write('Basic Blog!')


# class Profile(db.Model):
#     username = db.StringProperty(required=True)
#     password = db.TextProperty(required=True)
#     email = db.DateTimeProperty(auto_now_add=True)

#     def render(self):
#         self._render_text = self.content.replace('\n', '<br>')
#         return render_str("post.html", p=self)
        

class SignupHandler(Handler):
    def get(self):
        self.render('signup.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        passwordVerify = self.request.get('verify')
        email = self.request.get('email')
        nameError = ''
        passError = ''
        verifyError = ''
        emailError = ''
        valid_user = valid_username(username)
        valid_pass = valid_password(password)
        valid_mail = valid_email(email)

        if passwordVerify == password:
            verify_password = True
        else:
            verify_password = False
            verifyError = "Your passwords did'nt match."

        if valid_user and valid_pass and verify_password:
            new_cookie_val = make_pw_hash(username, password)
            self.response.headers.add_header('Set-Cookie', 'user_id=%s; Path=/wellcome' % new_cookie_val)
            # self.redirect('/wellcome?username=' + username)
            self.redirect('/wellcome?')

        else:
            if not valid_user:
                nameError = "That's not a valid username."
            if not valid_pass:
                passError = "That wasn't a valid password."
                verifyError = ''
            if not valid_mail:
                emailError = "That's not a valid email."

            self.render('signup.html',
                        nameError=nameError,
                        passError=passError,
                        verifyError=verifyError,
                        emailError=emailError,
                        username=username,
                        email=email)


class WellcomeHandler(Handler):
    def get(self):
        username = self.request.get('username')
        password = self.request.get('password')

        self.response.write('Welcome!')

        # self.response.headers['Content-Type'] = 'text/plain'
        # user_id = 0
        # userID_cookie_str = self.request.cookies.get('user_id')
        # if userID_cookie_str:
        #     cookie_val = valid_pw(username, password, userID_cookie_str)
        #     if cookie_val:
        #         self.render('wellcome.html', username=username)
        #     else:
        #         self.redirect('/blog/signup/?')
                # user_id = int(cookie_val)

        # user_id += 1

        
        # if user_id > 1000:
        #     self.write("You're the best!")
        # else:
        #     self.write("You've been here %s times!" % user_id)        


# Blog stuff

class Post(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p=self)


class MyBlogFront(Handler):
    """docstring for MyBlogFront"""
    def get(self):
        # posts = Post.all().order('-created')
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")
        self.render("myblog.html", posts=posts)


class PostPage(Handler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        self.render("permalink.html", post=post)


class NewPost(Handler):
    """docstring for NewPost"""
    def get(self):
        self.render("newpost.html")

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            p = Post(parent=blog_key(), subject=subject, content=content)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))

        else:
            error = "We need both a Subject and some Blog!"
            self.render("newpost.html", subject=subject, content=content,
                        error=error)


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog/signup/?', SignupHandler),
    ('/wellcome', WellcomeHandler),
    ('/blog/?', MyBlogFront),
    ('/blog/([0-9]+)', PostPage),
    ('/blog/newpost', NewPost),
], debug=True)
