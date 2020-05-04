from recipease.routes import app

class NoRecipeCardFoundError(Exception):
  def __init__(self, url):
    message = "No conforming recipe JSON found on '{}'."
    self.message = message.format(url)

### construct response bodies based on exceptions
