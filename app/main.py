# import the routes module where any extended routes are defined
from recipease.routes import app

# by default start the flask app.
if __name__ == "__main__":
  # Only for debugging while developing
  app.run(host='0.0.0.0', debug=True, port=80)