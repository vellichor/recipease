# this contains tools for turning a nested dict/list representation
# into a usable set of DB objects, and vice versa
# you must import the model definitions yourself
from recipease.db.models import * 
from recipease.utils.strings import pascal_to_snake

# we can probably do things even more smartly now that i know how to do stupid reflection.
# the following grabs the column referenced by the foreign key constraint on Recipe.author
#list(Recipe.__table__.columns['author'].foreign_keys)[0]._colspec

# for a foreign key to class MyClass, the id we are expecting is my_class_id
def class_to_foreign_key(cls):
  return "{}_id".format(pascal_to_snake(cls.__name__))

def save_list(model_list, session, **kwargs):
  for model_dict in model_list:
    model_dict.merge(kwargs) # pull in the foreign key id we netted from up top
    # don't need to capture the id of this, 
    # we will always find it using the foreign key
    save_dict(model_dict)

def save_dict(model_dict, session):
  # this is where we actually save an object to the database.
  # we should really make sure we intend to create it and not reuse another!
  # question: how do we know, based on this model's class and dictionary keys alone, 
  # what is the "natural key"?
  # normal thing that might have nested dicts or lists in it.
  nested_lists = {}
  for k,v in model_dict.iteritems():
    if type(v) == dict:
      # nested dicts are 1:1 or 1:+ represented by a foreign key id
      # create them first and add the created id in place of the nested dict
      model_dict[k] = save_dict(v, session)
    elif type(v) == list:
      # nested lists are +:1, so we need to know the id of this object 
      # we'll then create them as separate objects with the created id added in
      nested_lists[k] = model_dict.pop[k]
  model_class = model_dict.pop('class')
  model = model_class(model_dict)
  session.add(model)
  session.flush()
  # now we have an id for this dict in model.id
  # the foreign key name is derived from the current model's class
  foreign_key = {
    class_to_foreign_key(model_class): model.id
  }
  # go through the +:1 relations we pulled out, add the foreign key and save
  for k,v in nested_lists.iteritems():
    save_list(v, session, **foreign_key)
  return model.id
