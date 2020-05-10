from recipease.routes import app
from recipease.utils.jinja import env
from flask import request
import requests # this won't get confusing

from recipease.utils.parsing import parse_recipe
from recipease.db.dictdb import save_dict
from recipease.utils.web import *

@app.route("/")
def homepage():
  body = env.get_template("home.html").render()
  return app.response_class(response=body,
                              status=200,
                              mimetype='text/html')

@app.route("/decode", methods=['GET', 'POST'])
def decode():
  body = "nothing to see here, folks"
  mimetype = 'text/html'
  if request.form:
    url = request.form.get('url')
    if url:
      recipe = parse_recipe(get_recipe(url))
      recipe_dict = save_dict(recipe)
      body = recipe_dict
      mimetype = 'application/json'
  # render the page, with or without a decoded card.
  return app.response_class(response=body,
                              status=200,
                              mimetype=mimetype)
