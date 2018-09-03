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
import jinja2

import os
import re
import random
import hashlib
import hmac
from string import letters

from google.appengine.ext import db


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

secret = 'secretsctring'

USER_RE = re.compile("^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile("^.{3,20}$")
EMAIL_RE = re.compile("^[\S]+@[\S]+.[\S]+$")

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

# Key
def blog_key(name='default'):
    return db.Key.from_path('blogs', name)

def users_key(group='default'):
    return db.Key.from_path('users', group)

# Valid user, password and email
def valid_username(username):
    return username and USER_RE.match(username)

def valid_password(password):
    return password and PASSWORD_RE.match(password)

def valid_email(email):
    return not email or EMAIL_RE.match(email)

# Cookies
def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

# Security
def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, pw, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, pw, salt)



class Handler(webapp2.RequestHandler):
    """docstring for Handler"""
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_cookie(self, name, val):
        new_cookie_val = make_secure_val(val)
        self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/' % (name, new_cookie_val))

    def read_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)
    
    def login(self, user):
        self.set_cookie('user_id', str(user.key().id()))

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        userID_cookie = self.read_cookie('user_id')



class MainPage(Handler):
    def get(self):
        self.response.write('Basic Blog!')


class Profile(db.Model):
    username = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty()
        

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
            self.redirect('/wellcome?username=' + username)

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


class Login(Handler):
    def get(self):
        self.render('login.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        slef.redirect('/blog')


        

class WellcomeHandler(Handler):
    def get(self):
        username = self.request.get('username')
        if valid_username(username):
            self.render('wellcome.html', username=username)
        else:
            self.redirect('signup.html')  

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
    ('/signup/?', SignupHandler),
    ('/wellcome', WellcomeHandler),
    ('/blog/?', MyBlogFront),
    ('/blog/([0-9]+)', PostPage),
    ('/blog/newpost', NewPost),
    ('/login', Login),
], debug=True)
