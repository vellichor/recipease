import isodate
from isodate.isoerror import ISO8601Error
from datetime import datetime, timedelta

from recipease.db.models import *

NUM_WORDS={
  "one": 1,
  "a": 1,
  "an": 1,
  "two": 2,
  "three": 3,
  "four": 4,
  "five": 5,
  "six": 6,
  "seven": 7,
  "eight": 8,
  "nine": 9,
  "ten": 10,
  "eleven": 11,
  "twelve": 12
}

def parse_num(num_str):
  num_str = num_str.strip()
  parts = re.split(r'[\-\s]+', num_str)
  if len(parts) > 1:
    return float(parts[0]) + parse_num("".join(parts[1:]))
  else:
    # might be a bare fraction
    parts = list(map(lambda x: x.strip(), re.split(r'\/', num_str)))
    if len(parts) > 1:
      return int(parts[0]) / int(parts[1])
    else:
      # guess it could also be a bare float
      return float(num_str)
  # if none of that worked somehow, bail.
  raise ValueError("Couldn't parse {} as a numeric string".format(num_str))

def parse_num_word(num_str):
  num_str = num_str.strip()
  # find dozen if it's there
  dozen_search = re.search(r'dozen', num_str)
  if dozen_search:
    num_str = num_str[0:dozen_search.start()].strip()
  # the rest musta matched a number word
  value = NUM_WORDS[num_str]
  if dozen_search:
    value *= 12
  return value

# TODO: deal with dozen and other meta-numerics better
def parse_ingredient(ingr):
  # might be like
  # about 3 cups of rice
  # 3 1/2 teaspoons tomato paste
  # one apple
  # salt to taste
  # a pinch of cumin
  # an egg
  ingr = ingr.lower()
  num_regex=r'^[0-9\s\/\-\.]*[0-9] '
  num_word_regex=r'^(an|a|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve ?)(dozen ?)?'

  # pull "about " right off the front if it is there because fuck all that
  ingr = re.sub(r'^about ', '', ingr)
  qty = None
  # see if we have any quantifier we know about in front
  num_search = re.search(num_regex, ingr)
  num_word_search = re.search(num_word_regex, ingr)
  if num_search:
    qty = parse_num(num_search.group())
    ingr = ingr[num_search.end():].strip()
  elif num_word_search:
    qty = parse_num_word(num_word_search.group())
    ingr = ingr[num_word_search.end():].strip()
  # probably got the numeric quantity off, if there was one.

  # now units. we will look for the units we know about.
  units = get_known_units()
  unit_regex = "^({}) ".format("|".join(units.keys()))
  unit_search = re.search(unit_regex, ingr)
  unit = None
  if unit_search:
    unit_name = unit_search.group().strip()
    unit = units[unit_name]
    ingr = ingr[unit_search.end():].strip()

  # the rest we presume to be the ingredient
  # if it starts with "of " knock that off
  ingr = ingr.strip()
  if ingr.startswith("of "):
    ingr = ingr[3:]
  return {
    'class': RecipeIngredient,
    'qty': qty,
    'unit': unit, # get the id
    'ingredient': {
      'class': Ingredient,
      'name': ingr
    }
  }

def get_known_units():
  units = {}
  with session_scope as session:
    for u in session.query(Unit).all():
      units.merge(reduce(lambda x, y: x.merge(y),
                          map(lambda x: {x: u.id},
                              filter(lambda x: x is not None, 
                                      [u.name, u.plural_name, u.shortname]))))
  return units

def parse_ingredients(ingredients):
  return list(map(parse_ingredient, ingredients))

def parse_author(author):
  return {
    'class': Author,
    'author': author.get('name'),
    'email': author.get('email')
  }

def parse_images(images):
  # did we get a bare string? if so, listify it.
  if type(images) == str:
    images = [images]
  # wrap each url in an image object and then save it to the db
  return {
    'class': ImageSet,
    'images': list(map(lambda x: {
                        'class': Image,
                        'url': x
                        },
                      images))
  }

def parse_step(step):
  return {
    'class': Step,
    'name': step.get('name'),
    'text': step.get('text'),
    'url': step.get('url'),
    'image': parse_images(step.get('image', []))
  }

def parse_section(section):
  return {
    'class': Section,
    'name': section.get('name'),
    'steps': parse_steps(section.get('itemListElement'))
  }

def parse_steps(steps, name=None):
  steps_list = []
  # this may recur.
  for step in steps:
    if step['@type'] == 'HowToSection':
      steps_list.append(parse_section(step))
    else:
      steps_list.append(parse_step(step))
  # we now have to just brute force whang the order into the dictionary
  for i in range(len(steps_list)):
    steps_list[i]['order'] = i
  return steps_list

def parse_datetime(d_str):
  try:
    return isodate.parse_datetime(d_str)
  except(ISO8601Error):
    try:
      date = isodate.parse_date(d_str)
      return datetime.combine(date, datetime.min.time())
    except(ISO8601Error):
      return None

# from an ISO8601 duration, give the minutes as an int
def duration_to_minutes(dur_str):
  try:
    td = isodate.parse_duration(dur_str)
    return int(((td.days * (24*60*60)) + td.seconds) / 60)
  except(Exception):
    return None

def minutes_to_duration(min):
  return isodate.duration_isoformat(timedelta(seconds=min*60))

def parse_recipe(recipe):
  recipe_dict = {
    'class': Recipe,
    # direct attributes
    'name': recipe.get('name'),
    'description': recipe.get('description'),
    'date_published': parse_datetime(recipe.get('datePublished')),
    'prep_time': duration_to_minutes(recipe.get('prepTime')),
    'cook_time': duration_to_minutes(recipe.get('cookTime')),
    'category': recipe.get('recipeCategory'),
    'cuisine': recipe.get('recipeCuisine'),
    # one to many
    'author': parse_author(recipe.get('author')),
    # many to many
    'images': parse_images(recipe.get('image', [])),
    # many to one
    'ingredients': parse_ingredients(recipe.get('recipeIngredient', [])),
    'steps': parse_steps(recipe.get('recipeInstructions', []))
  }
  # HACK i don't want to build new models at 10pm
  if isinstance(recipe_dict['category'], list):
    recipe_dict['category'] = recipe_dict['category'][0]
  if isinstance(recipe_dict['cuisine'], list):
    recipe_dict['cuisine'] = recipe_dict['cuisine'][0]
  if not (recipe_dict['name'] and recipe_dict['images'] and len(recipe_dict['steps']) > 0):
    raise ValueError("Recipe must have name, image, and recipeInstructions");
  return recipe_dict

