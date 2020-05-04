import requests # NOT flask.request! different!!
from bs4 import BeautifulSoup
from recipease.utils.errors import NoRecipeCardFoundError
import json

# here's a sample page with json+ld: https://preppykitchen.com/moist-vanilla-cupcake-recipe/

def extract_recipe_schema(schema):
  if schema.get('@type') == 'Recipe':
    return schema
  elif '@graph' in schema:
    for s in schema['@graph']:
      r = extract_recipe_schema(s)
      if r:
        return r
  # fell through, no schema can be extracted
  return None

def get_recipe(url):
  r = requests.get(url) # throws if there's a problem
  #print(r.text)
  bs = BeautifulSoup(r.text, 'lxml') # slurp all the content
  for s in bs.find_all('script'):
    if s.get('type') == "application/ld+json":
      schema = json.loads(s.string)
      recipe = extract_recipe_schema(schema)
      if recipe:
        return recipe
  # if we fell through, apologize
  raise NoRecipeCardFoundError(url)
