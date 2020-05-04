# Recipe Book

This tool enables rich interactions with the Recipe JSON-LD schema given by Google: https://developers.google.com/search/docs/data-types/recipe

You will be able to

* Extract recipes from compliant websites
* Create your own
* View, browse, and search your collection
* Print a recipe on a card
* Try to extract 

## Run the tests

```
docker-compose run web pytest /test
```

## Local Server

```
docker-compose up
```

## Stack

This tool is built with Python3, Flask, SqlAlchemy, BeautifulSoup4, Jinja2, and a whole lot of totally messy handrolled parsing.

SqlAlchemy doesn't seem to have a great way to translate between foreign key relationships in the DB and a nested Python dict representation of an object's whole extended set of friends and relations. You'll find the code to do it for you in `recipease.db.dictdb` for all the good it may do you.

This tool attempts to do some light, rule-based parsing of numeric words in ingredient lists, like "a pinch of cumin" or "two dozen eggs" or "2 1/2 tsps vanilla". To really do this right we would need some dependency parsing and I've got my eye on spaCy but good gravy that's a lot of effort to go to for a cookbook. THAT SAID, parsed ingredient lists are necessary for autoscaling recipes so this is a major nice to have.