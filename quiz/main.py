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


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(autoescape=True, loader = jinja2.FileSystemLoader(template_dir))



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
        self.response.write('Quiz ROT 13')


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
        

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/rot13', Rot13Handler),
    ('/signup', SignupHandler),
], debug=True)
