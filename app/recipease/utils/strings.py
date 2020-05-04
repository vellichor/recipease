from fractions import Fraction
import re

def get_partial_frac(qty):
  f = Fraction(qty).limit_denominator(16)
  whole = int(f.numerator / f.denominator)
  fractional_numerator = f.numerator - (whole * f.denominator)
  return (whole, fractional_numerator, f.denominator)

def printable_qty(qty):
  (whole, f_num, f_denom) = get_partial_frac(qty)
  parts = []
  if whole != 0:
    parts.append(str(whole))
  if f_num != 0:
    parts.append("{}/{}".format(f_num, f_denom))
  return " ".join(parts)

def pluralize(noun):
  if re.search(r'(s|sh|z)$', noun):
    return noun+"es"
  else:
    return noun+"s"

# case changes. half of these are trivial.

# non-trivial
def snake_to_pascal(snake_str):
  return "".join(map(lambda x: x[0].upper()+x[1:], snake_str.split('_')))

# less trivial (REGEXES AAAH)
def pascal_to_snake(p_str):
  return '_'.join(map(lambda x: x.lower(), re.sub(r'([A-Z])', r' \1', p_str).strip().split(' ')))

# QUITE non-trivial
def mixed_to_camel(m_str):
  c_str = m_str
  uniboob = r'_(.)'
  match = re.search(uniboob, c_str)
  while match:
    c_str = c_str[:match.start()] + match.group(1).upper() + c_str[match.end():]
    match = re.search(uniboob, c_str)
  return c_str

# all totally silly from here.
def pascal_to_camel(p_str):
  return p_str[0].lower()+p_str[1:]

def snake_to_camel(snake_str):
  return pascal_to_camel(snake_to_pascal)

def camel_to_snake(c_str):
  return pascal_to_snake(c_str) # LOL!
