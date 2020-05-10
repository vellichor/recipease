# this contains tools for turning a nested dict/list representation
# into a usable set of DB objects, and vice versa
# you must import the model definitions yourself
from recipease.db.models import * 
from recipease.utils.strings import pascal_to_snake

from sqlalchemy.schema import UniqueConstraint
from sqlalchemy import tuple_

# for a foreign key to class MyClass, the id we are expecting is my_class_id
def class_to_foreign_key(cls):
  return "{}_id".format(pascal_to_snake(cls.__name__))

def save_list(model_list, session, **kwargs):
  for model_dict in model_list:
    model_dict.update(kwargs) # pull in the foreign key id we netted from up top
    # don't need to capture the id of this, 
    # we will always find it using the foreign key
    save_dict(model_dict, session)

# this presumes that all nested items have been precreated.
# for a dict that may be nested, use save_dict() to resolve the nesting first.
def get_or_save_simple_dict(simple_dict, session):
  # this is where we actually save an object to the database.
  model_class = simple_dict.get('class')
  # don't modify the original dict, just make another one without the class
  model_dict = {k: simple_dict[k] for k in filter(lambda x: x != 'class', simple_dict.keys())}
  # we should really make sure we intend to create it and not reuse another!
  # reflect on any unique constraints in here.
  for c in filter(lambda x: isinstance(x, UniqueConstraint),
                  model_class.__table__.constraints):
    cols = c.columns.keys()
    attrs = tuple(map(lambda x: getattr(model_class, x), cols))
    vals = [tuple(map(lambda x: model_dict.get(x), cols))] # tuple of the tuple
    #results = session.query(Unit).filter(Unit.name == 'cup')
    results = session.query(model_class).filter(tuple_(*attrs).in_(vals)).all()
    if len(results) > 0: # found a match that would break uniqueness.
      model = results[0]
      # we may still need to update it.
      for c in simple_dict.keys():
        if c in model.__table__.columns.keys():
          setattr(model, c, simple_dict[c])
      session.flush()
      return model
  # did not find an object that would violate uniqueness.
  # save this one.
  model = model_class(**model_dict)
  session.add(model)
  session.flush()
  return model

def save_dict(model_dict, session):
  # normal thing that might have nested dicts or lists in it.
  # resolve all nested items and then use get_or_save_simple_dict to store the bare object
  nested_lists = {}
  for k,v in model_dict.items():
    if type(v) == dict:
      # nested dicts are 1:1 or 1:+ represented by a foreign key id
      # create them first and add the created id in place of the nested dict
      model_dict[k] = save_dict(v, session)
    elif type(v) == list:
      # nested lists are +:1, so we need to know the id of this object 
      # we'll then create them as separate objects with the created id added in
      nested_lists[k] = model_dict.pop[k]
  # save the resolved dict
  model_class = model_dict['class'] # this will be popped off by the inner call
  model = get_or_save_simple_dict(model_dict, session)
  # now we have an id for this dict in model.id
  # the foreign key name is derived from the current model's class
  foreign_key = {
    class_to_foreign_key(model_class): model.id
  }
  # go through the +:1 relations we pulled out, add the foreign key and save
  for k,v in nested_lists.items():
    save_list(v, session, **foreign_key)
  return model.id

## return an (attrs, vals) tuple ready to be used in a query
#def make_selection_spec(model_class, value_dict, columns):
#  return ( tuple(map(lambda x: getattr(model_class, x), columns)),
#          [tuple(map(lambda x: value_dict.get(x), columns))] )
#
#def get_primary_key_cols(model_class):
#  # a table has exactly one primary key, which may have many columns
#  return filter(lambda x: isinstance(x, PrimaryKeyConstraint),
#                model_class.__table__.constraints)[0].columns.keys()
#
#def get_foreign_key_ids
#
#def load_simple_dict(model_class, session, **kwargs):
#  # find out what columns we're selecting on, 
#  # ignoring those that aren't in the model's spec
#  model_fields = model_class.__table__.columns.keys()
#  cols = filter(lambda x: x in model_fields, kwargs.keys())
#  if len(cols)==0:
#    raise ValueError("No field in {} was a valid field of {} ({})" \
#      .format(kwargs, model_class.__name__, model_fields))
#  attrs,vals = make_selection_spec(model_class, kwargs, cols)
#  print("Looking for instances where {} are {}".format(attrs, vals))
#  results = session.query(model_class).filter(tuple_(*attrs).in_(vals)).all()
#  if len(results) > 0:
#    model = results[0]
#
#
#
#def load_dict_inner(model_class, session, **kwargs):
#  pass
#
#def load_dict(model_class, session, **kwargs):
#  # create the base dictionary
#  # find out what this table's primary keys are
#  cols = []
#  for c in filter(lambda x: isinstance(x, PrimaryKeyConstraint),
#                  model_class.__table__.constraints):
#    cols += c.columns.keys()
#  attrs = tuple(map(lambda x: getattr(model_class, x), cols))
#  vals = [tuple(map(lambda x: kwargs.get(x), cols))] # tuple of the tuple
#  print("Looking for instances where {} are {}".format(attrs, vals))
#  results = session.query(model_class).filter(tuple_(*attrs).in_(vals)).all()
#  if len(results) > 0: # found a match that would break uniqueness.
#    model = results[0]
#    # ok we have the base dictionary! now resolve all foreign keys.
#    f
#    # we do this with an inner function that only goes one layer deep,
#    # since we don't want to follow the foreign key relationships back!
#
#
#    return model
#  else:
#    return None
#


