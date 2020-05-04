from recipease.db.models import Unit, Conversion
from recipease.db.connection import session_scope

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