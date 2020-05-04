from recipease.routes import app
from recipease.utils.jinja import env
from flask import request
import requests # this won't get confusing

@app.route("/")
def homepage():
  body = env.get_template("home.html").render()
  return app.response_class(response=body,
                              status=200,
                              mimetype='text/html')

@app.route("/decode", methods=['GET', 'POST'])
def decode():
  if request.form:
    url = request.form.get('url')
    if url:
      pass
  # render the page, with or without a decoded card.
  body = "nothing to see here, folks"
  return app.response_class(response=body,
                              status=200,
                              mimetype='text/html')
