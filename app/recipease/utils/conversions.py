#from sqlalchemy import in_

from recipease.db.models import Unit, Conversion
from recipease.db.dictdb import *

# from sqlalchemy import or_, and_, not_
from sqlalchemy.orm.exc import NoResultFound

# basic units we always have
# as (longname, plural, shortname)
# only longname is required
units = [
  ## volume, imperial
  ("smidgen", None, None),
  ("dash", None, None),
  ("pinch", None, None),
  ("teaspoon", None, "tsp"),
  ("tablespoon", None, "tbsp"),
  ("fluid ounce", None, 'fl oz'),
  ("cup", None, "c"),
  ("pint", None, 'pt'),
  ("qt", None, 'qt'),
  ("gallon", None, 'gal'),
  ## weight, imperial
  ("ounce", None, 'oz'),
  ("pound", None, 'lb'),
  ("stone", None, 'st'),
  ("ton", None, 't'), # lol
  ## volume, metric -- we'll handle prefixing in code here.
  ("liter", None, "L"),
  ## weight, metric -- we'll use this with density if someone wants mass conversions
  ("Newton", None, "N"),
  ## mass, metric -- ditto
  ("gram", None, "g")
]

# we have some authoritative conversions to add.
# we will give "3 tsp = 1 tbsp" as (3, "tsp", 1, "tbsp")

conversions = [
  [2, "smidgen", 1, "dash "],
  [2, "dash", 1, "pinch"],
  [8, "pinch", 1, "tsp"],
  [3, "tsp", 1, "tbsp"],
  [2, "tbsp", 1, "fl oz"],
  [8, "fl oz", 1, "c"],
  [2, "c", 1, "pt"],
  [2, "pt", 1, "qt"],
  [4, "qt", 1, "gal"],
  [8, "oz", 1, "lb"],
  [14, "lb", 1, "st"],
  [2000, "lb", 1, "ton"],
  # cross-system
  [3.78541, "L", 1, "gal"],
  # weight to weight, we'll use g to get to mass JUST IN CASE lol 
  [1, "lb", 4.45, "N"]
]

# these use save_dict, which is idempotent.
def create_all_units(session):
  for u in map(lambda x: {"name": x[0],
                          "plural_name": x[1],
                          "shortname": x[2],
                          "class": Unit
                          },
                units):
    save_dict(u, session)

def create_all_conversions(session):
  for c in map(lambda x: {"num_qty": x[0],
                          "num_unit_id": get_unit(x[1], session).id,
                          "denom_qty": x[2],
                          "denom_unit_id": get_unit(x[3], session).id,
                          "class": Conversion
                          },
                conversions):
    save_dict(c, session)

# prefixes as (name, exponent, shortname)
# we will only go to 15 because what the hell are we going to want with a yg of cinnamon
# like seriously only a homeopathic "doctor" would care
# like how much even does a molecule of cinnamol weigh
# ok it's 1.276zg so a yg of cinnamol doesn't even exist
# and a Yg is the mass of the EARTH
# this is why you don't let the nerds have the computer
# late at night when they've been drinking
metric_prefixes = [
  ("deci", -1, "d"),
  ("centi", -2, "c"),
  ("milli", -3, "m"),
  ("micro", -6, "u"),
  ("nano", -9, "n"),
  ("pico", -12, "p"),
  ("femto", -15, "f"),
  ("deca", 1, "da"),
  ("hecto", 2, "h"),
  ("kilo", 3, "k"),
  ("mega", 6, "M"),
  ("giga", 9, "G"),
  ("tera", 12, "T"),
  ("exa", 15, "E")
]

def get_unit(name, session):
  # look it up by name, shortname, or plural name
  try:
    return session.query(Unit).filter((Unit.name == name) \
                              | (Unit.shortname == name) \
                              | (Unit.plural_name == name)) \
      .one()
  except(NoResultFound) as exc:
    raise ValueError("No unit named {}".format(name))

def get_unit_by_id(id, session):
  try:
    return session.query(Unit).filter(Unit.id == id).one()
  except(NoResultFound) as exc:
    raise ValueError("No unit with id {}".format(id))

# get a density in terms of the density of room temperature water
def get_density(vol_unit, vol_qty, amt_unit, amt_qty, session, g=None):
  # water is 1g/mL
  # convert the volume to liters, since mL is not a true unit
  l_vol = convert_qty(vol_qty, vol_unit, get_unit('liter', session), session, g=g)
  g_mass = convert_qty(amt_qty, amt_unit, get_unit('g', session), session, g=g)
  return g_mass / (l_vol * 1000)

def get_metaconversions(from_unit, from_qty, session, density=1, g=9.81):
  converted = {} # leave room for many metaconversions if we decide to change how we do prefixes
  # do any metaconversion that's appropriate
  if (from_unit.name == 'Newton'):
    # make sure they aren't aliens
    if g/9.81 > 1.000000001 or 9.81/g > 1.000000001:
      print("Dude, where the fuck ARE you?")
    converted[get_unit('gram', session)] = (from_qty * 1000) / g
  if (from_unit.name == 'gram'):
    converted[get_unit('Newton', session)] = (from_qty / 1000) * g
  # need to do density in base units but it's always given in g/mL for human reasons
  # we can suppress these conversions by explicitly passing density=None
  if density:
    if (from_unit.name == 'liter'):
      converted[get_unit('gram', session)] = from_qty * 1000 / density
    if (from_unit.name == 'gram'):
      converted[get_unit('liter', session)] = from_qty * density / 1000
  return converted

# to_unit is what we are looking for and we'll recursively crawl down until we find it.
# note that we mostly actually have discrete objects for prefix-derived SI units!
# we nice up the display at display time.
def convert_qty(from_unit, from_qty, to_unit, session, density=1, g=9.81, depth=0, known_units=None):
  # safety check
  if depth > 30:
    raise RecursionError("max recursion depth exceeded for conversion")
  # base case 1: identity
  if from_unit == to_unit:
    return {'unit': from_unit,
            'qty': from_qty}
  # base case 2: direct conversion exists
  # get all possible direct conversions from this unit
  # (that haven't been tried in a previous iteration)
  if not known_units:
    known_units=set()
  known_units.add(from_unit)
  conversions = get_metaconversions(from_unit, from_qty, session, density, g)
  conversions.update(get_conversions_for(from_unit, from_qty, \
                                          session, known_units))
  if to_unit in conversions.keys():
    return {'unit': to_unit, 
            'qty': conversions[to_unit]
            }
  # not in the direct conversions either.
  # recursively convert each direct conversion of this, and return any success.
  # don't check units we saw already.
  known_units.update(conversions.keys())
  for unit, qty in conversions.items():
    conversion = convert_qty(unit, qty, to_unit, session, density=density, g=g, depth=depth+1, known_units=known_units)
    if conversion is not None:
      return conversion
  # we have seen every unit and found no conversion!
  return None

def get_conversions_for(from_unit, from_qty, session, known_units=[]):
  known_unit_ids = list(map(lambda x: x.id, known_units))
  # convert this by all possible direct unit conversions (that we have not seen)
  conversions = {}
  # forward
  for c in session.query(Conversion) \
            .filter((Conversion.num_unit_id == from_unit.id) \
                    & (~ (Conversion.denom_unit_id.in_(known_unit_ids))))\
            .all():
    # perform the conversion
    conversions[get_unit_by_id(c.denom_unit_id, session)] \
      = from_qty * c.denom_qty / c.num_qty
  # backward
  for c in session.query(Conversion) \
            .filter((Conversion.denom_unit_id == from_unit.id) \
                    & (~ (Conversion.num_unit_id.in_(known_unit_ids))))\
            .all():
    # perform the conversion
    conversions[get_unit_by_id(c.num_unit_id, session)] \
      = from_qty * c.num_qty / c.denom_qty
  return conversions

# WIP ON PRESENTATION CONVERSIONS
#
# We want to be able to take a measure like "56 cups"
# and know that "7 gallons" is a way better thing to display.
#
# We should also show appropriate SI prefixes on metric values.
#
## what's a nice number?
# niceness is a comparator.
#def is_nice(qty):
#  (whole, f_num, f_denom) = get_partial_frac(qty)
#  # a small whole number is nice
#  if f_num = 0 and whole < 10:
#    return True
#  # a fraction with a small denominator is nice
#  if f_denom <= 4:
#    return True
#  return False
#
## what are all the values we could convert this number to?
#def get_all_conversions(unit, qty, depth=0, conversions=set()):
#  if depth > 10: # bail!
#    return set()
#  # what conversions do we already know?
#  known_units=map(lambda x: x['unit'], conversions)
#  with session_scope() as session:
#    # get all the conversions for this unit that we don't know already.
#    for c in session.query(Conversion)\
#                    .filter(Conversion.num=unit \
#                        and Conversion.denom not in known_units).all():
#      # forward conversion, add it.
#      conv_qty = qty * c.denom_qty / c.num_qty
#      conversions.add(c.num)
#
#
#
## recursively walk towards an optimal representation of this measure
#def auto_convert(unit_name, qty, depth=0):
#  # we generally want nice numbers and small denominators.
#  # see if there is a valid conversion in our conversion table that gets us
#  # a nicer number.
#  # don't iterate more than 5 times.
#  if depth = 5:
#    return (unit, qty)
#  # if we already have a "nice" number, stop iterating
#  (whole, f_num, f_denom) = get_partial_frac(qty)
#  if f_num = 0 
#