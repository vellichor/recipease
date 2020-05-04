from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.schema import ForeignKey
from recipease.utils.strings import *

Base = declarative_base()

class Unit(Base):
  __tablename__='unit'
  id=Column(Integer, primary_key=True)
  name=Column(String, nullable=False)
  plural_name=Column(String) # for irregular plurals
  shortname=Column(String) # eg c for cup or tbsp for tablespoon

  def get_singular(self):
    return self.name

  def get_plural(self):
    if self.plural_name:
      return self.plural_name
    else:
      return pluralize(self.name)

  def get_shortname(self):
    if self.shortname:
      return self.shortname
    else:
      return self.name

  def get_qty(self, qty):
    unit = self.get_singular()
    if qty > 1:
      unit = self.get_plural()
    return "{} {}".format(printable_qty(qty), unit)

  def __repr__(self):
    return "<Unit {}>".format(self.name)


class Ingredient(Base):
  __tablename__='ingredient'
  id=Column(Integer, primary_key=True)
  name=Column(String, nullable=False)
  unit_id=Column(Integer, ForeignKey('unit.id')) #nullable, this is an optional "typical" measure of this thing

  def __repr__(self):
    _unit_str = ""
    if self.typical_unit:
      _unit_str=", typically given by {}".format(self.typical_unit).name
    _str = "<Ingredient {}".format(self.name)

class Conversion(Base): # 3 teaspoons = 1 tablespoon
  __tablename__='conversion'
  id=Column(Integer, primary_key=True)
  num_unit_id=Column(Integer, ForeignKey('unit.id'), nullable=False)
  num_qty=Column(Integer, nullable=False)
  denom_unit_id=Column(Integer, ForeignKey('unit_id'), nullable=False)
  denom_qty=Column(Integer, nullable=False)

  def __repr__(self):
    return "<Conversion {} = {}>".format(self.num.get_quantity(self.num_qty), 
                                          self.denom.get_quantity(self.denom_qty))

class Author(Base):
  __tablename__='author'
  id=Column(Integer, primary_key=True)
  name=Column(String, nullable=False)
  email=Column(String)

  def __repr__(self):
    return "<Author {} ({})>".format(self.name, self.email)

class Image(Base):
  __tablename__='image'
  id=Column(Integer, primary_key=True)
  image_set_id=Column(Integer, ForeignKey('image_set.id'), nullable=False)
  url=Column(String, nullable=False)

  def __repr__(self):
    return "<Image {} in set {}>".format(self.url, self.image_set)

class ImageSet(Base):
  __tablename__='image_set'
  id=Column(Integer, primary_key=True)

# a section can be in a recipe or in another section
class Section(Base):
  __tablename__='section'
  id=Column(Integer, primary_key=True)
  recipe_id=Column(Integer, ForeignKey('recipe.id'))
  section_id=Column(Integer, ForeignKey('section.id'))
  # hackS! make sure to reorder ALL steps when writing back a modified record
  order=Column(Integer, nullable=False)
  name=Column(String, nullable=False) # all sections have names

# a step can be in a recipe or a section
class Step(Base):
  __tablename__='step'
  id=Column(Integer, primary_key=True)
  recipe_id=Column(Integer, ForeignKey('recipe.id'))
  section_id=Column(Integer, ForeignKey('section.id'))
  # hackS! make sure to reorder ALL steps when writing back a modified record
  order=Column(Integer, nullable=False)
  name=Column(String)
  text=Column(String)
  url=Column(String)
  image_set_id=Column(Integer, ForeignKey('image_set.id'))

class RecipeIngredient(Base):
  __tablename__='recipe_ingredient'
  id=Column(Integer, primary_key=True)
  recipe_id=Column(Integer, ForeignKey('recipe.id'), nullable=False)
  ingredient_id=Column(Integer, ForeignKey('ingredient.id'), nullable=False)
  qty=Column(Float)
  unit_id=Column(Integer, ForeignKey('unit.id'))
  amt=Column(String)
  notes=Column(String)

  def __repr__(self):
    # by default, just name it
    ingr_str = self.name
    if self.qty:
      # if we have a numeric quantity, make it pretty
      p_qty = printable_qty(self.qty)
      if self.unit:
        ingr_str = "{} {} {}".format(p_qty, self.unit.name, self.name)
      else:
        ingr_str = "{} {}".format(p_qty, self.name)
    elif self.amt:
      # we may instead have a description of how much we want.
      ingr_str = "{}, {}".format(self.name, self.amt)
    return "<RecipeIngredient {}>".format(ingr_str)

class Recipe(Base):
  __tablename__='recipe'
  id=Column(Integer, primary_key=True)
  name=Column(String, nullable=False)
  author_id=Column(Integer, ForeignKey('author.id'))
  description=Column(String)
  date_published=Column(DateTime)
  prep_time=Column(Integer)
  cook_time=Column(Integer)
  recipe_yield=Column(Integer)
  category=Column(String)
  cuisine=Column(String)
  image_set_id=Column(Integer, ForeignKey('image_set.id'), nullable=False)



