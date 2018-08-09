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


USER_RE = re.compile("^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile("^.{3,20}$")
EMAIL_RE = re.compile("^[\S]+@[\S]+.[\S]+$")

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(autoescape=True, loader = jinja2.FileSystemLoader(template_dir))


def valid_username(username):
    return USER_RE.match(username)


def valid_password(password):
    return PASSWORD_RE.match(password)

def valid_email(email):
    return EMAIL_RE.match(email)


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


class BaseHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)


class MainPage(BaseHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Quiz ROT 13 and Signup')


class Rot13Handler(BaseHandler):
    """docstring for Rot13Handler"""
    def get(self):
        self.render('rot13-main.html')

    def post(self):
        rot13 = ''
        text = self.request.get('text')
        if text:
            rot13 = text.encode('rot13')
        self.render('rot13-main.html', text=rot13)


class SignupHandler(BaseHandler):
    """docstring for SignupHandler"""
    def get(self):
        self.render('signup.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        passwordVerify = self.request.get('verify')
        email = self.request.get('email')

        valid_user = valid_username(username)
        valid_pass = valid_password(password)
        valid_mail = valid_email(email)
        
        if valid_user:
            self.redirect('/wellcome')
        if not valid_user or not valid_pass:
            nameError = ''
            passError = ''
            if not valid_user:
                nameError = "That's not a valid username."
            if not valid_pass:
                passError = "That wasn't a valid password."
            self.render('signup.html', nameError=nameError, passError=passError) 
        else:
            self.render('signup.html')


class WellcomeHandler(BaseHandler):
    """docstring for WellcomeHandler"""
    def get(self):
        self.render('wellcome.html', username='testeudacity')
        

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/rot13', Rot13Handler),
    ('/signup', SignupHandler),
    ('/wellcome', WellcomeHandler),
], debug=True)
