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

@app.route("/recipe/import", methods=['GET', 'POST'])
def decode():
  print("IS THIS THING ON")
  recipes=[]
  if request.form:
    print("Got a form submission")
    url = request.form.get('url')
    print("Got recipe url {}".format(url))
    if url:
      recipe = parse_recipe(get_recipe(url))
      print("Got recipe {}".format(recipe))
      recipes.add(recipe)
      #recipe_dict = save_dict(recipe)
  body = env.get_template("import.html").render(recipes=recipes)
  return app.response_class(response=body,
                              status=200,
                              mimetype='text/html')
