from recipease.db.models import Unit, Conversion
from recipease.db.connection import session_scope

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
  [2, "smidgen", 1, "dash"],
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
  [3.78541, "L", 1, "gal"]
  # assume we're on earth!
  [101.97, "g", 1, "N"]
]

def create_all_units():
  with session_scope as session:
    for u in map(lambda x: {"name": x[0],
                            "plural_name": x[1],
                            "shortname": x[2],
                            "class": Unit
                            },
                  units):
      save_dict(u, sesssion)

def create_all_conversions():
  with session_scope as session:
    for c in map(lambda x: {"num_qty": x[0],
                            "num_unit_id": get_unit(x[1]),
                            "denom_qty": x[2],
                            "denom_unit_id": get_unit(x[3]),
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
# this is why you don't let the nerds have the computer late at night when they've been drinking
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

def get_unit(name):
  # look it up by name, shortname, or plural name
  with session_scope as session:
    return session.query(Unit).filter(Unit.name == name \
                                or Unit.shortname == name \
                                or Unit.plural_name == name) \
      .fetch_one()

# get a density in terms of the density of room temperature water
def get_density(vol_unit, vol_qty, amt_unit, amt_qty, g=None):
  # water is 1g/mL
  # convert the volume to milliliters
  ml_vol = convert(vol_qty, vol_unit, 'mL')
  g_mass = convert(amt_qty, amt_unit, 'g', g)
  return g_mass / ml_vol

def get_metaconversions(from_qty, from_unit, density=1, g=9.81):
  converted = []
  # do any metaconversion that's appropriate
  if (from_unit.name == 'Newton'):
    # make sure they aren't aliens
    if g/9.81 > 1.000000001 or 9.81/g > 1.000000001:
      print("Dude, where the fuck ARE you?")
    converted.append({
                      'unit': get_unit('gram'),
                      'qty': g / from_qty
                    }
  if (from_unit.name == 'gram'):
    converted.append({
                      'unit': get_unit('Newton'),
                      'qty': from_qty / g
                    }
  # need to do density in base units but it's always given in g/mL for human reasons
  if (from_unit.name == 'liter'):
    converted.append({
                      'unit': get_unit('gram'),
                      'qty': from_qty / (1000 * density)
                    }
  if (from_unit.name == 'liter'):
    converted.append({
                      'unit': get_unit('gram'),
                      'qty': from_qty / (1000 * density)
                    }


# to_unit is what we are looking for and we'll recursively crawl down until we find it.
def convert_qty(from_qty, from_unit, to_unit, density=1, g=9.81, depth=0, known_units=[]):
  # safety check
  if depth > 30:
    raise RecursionError("max recursion depth exceeded for conversion")
  # base case
  if from_unit == to_unit:
    return {'unit': from_unit,
            'qty': from_qty}
  # not there yet. get all possible direct conversions from this unit
  # (that haven't been tried in a previous iteration)
  known_units += from_unit
  converted = get_metaconversions(from_qty, from_unit, density, g) \
    + get_conversions_for(from_qty, from_unit, known_units)
  # 
  known_units += list(map(lambda x: x.unit, converted))
  for c in converted:
    # check them all.
    conversion = convert_qty(c.qty, c.unit, to_unit, density=density, g=g, depth=depth+1, known_units=known_units)
    if conversion is not None:
      return conversion

def get_conversions_for(from_qty, from_unit, known_units=[]):
  known_unit_ids = list(map(lambda x: x.id, known_units))
  # convert this by all possible direct unit conversions (that we have not seen)
  conversions = []
  # forward
  for c in session.query(Conversion)\
            .filter(Conversion.num_unit_id == from_unit.id \
                    and Conversion.denom_unit_id not in known_unit_ids)\
            .join(Unit)
            .all():
    # perform the conversion
    conversions.add({
                      'unit': c.unit.name,
                      'qty': from_qty * c.denom_qty / c.num_qty
                    })
  # backward
  for c in session.query(Conversion)\
            .filter(Conversion.denom_unit_id == from_unit.id \
                    and Conversion.num_unit_id not in known_unit_ids)\
            .join(Unit)
            .all():
    # perform the conversion
    conversions.add({
                      'unit': c.unit.name,
                      'qty': from_qty * c.denum_qty / c.denom_qty
                    })
  return conversions

# niceness is a comparator.
## what's a nice number?
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