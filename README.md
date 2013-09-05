# A Pythonic wrapper for the Nobel Prize API
[![Build Status](https://travis-ci.org/vibragiel/nobel.png)](https://travis-ci.org/vibragiel/nobel)[![Coverage Status](https://coveralls.io/repos/vibragiel/nobel/badge.png)](https://coveralls.io/r/vibragiel/nobel)

A simple Python wrapper for the [Nobel Prize API](http://www.nobelprize.org/nobel_organizations/nobelmedia/nobelprize_org/developer/).

## Quickstart

First, initialize the API wrapper:

```python
import nobel
api = nobel.Api()
```

Now you have access to the resources defined by the API (`prizes`,
`laureates` and `countries`) and their methods.

For example, to list all laureates:

```python
>>> for laureate in api.laureates.all():
...     print '%s (%s)' % (laureate, laureate.born_country)
```

To filter (check the [Nobel Prize API](http://www.nobelprize.org/nobel_organizations/nobelmedia/nobelprize_org/developer/) documentation
for all available filtering parameters):

```python
>>> api.laureates.filter(gender='female', born_country='Iran')
[<Laureate id=773>, <Laureate id=817>]
>>> api.prizes.filter(year=1969)
[<Prize category="physics" year=1969>, <Prize category="chemistry" year=1969>,
<Prize category="medicine" year=1969>, <Prize category="literature" year=1969>,
<Prize category="peace" year=1969>, <Prize category="economics" year=1969>]
```

To retrieve a single resource:

```python
>>> laureate = api.laureates.get(id=26)
>>> laureate.firstname
u'Albert'
>>> laureate.surname
u'Einstein'
>>> laureate.prizes
[<Prize category="physics" year=1921>]
>>> laureate.born_country
<Country code="DE" name="Germany">
>>> laureate.died_country
<Country code="US" name="USA">

>>> prize = api.prizes.get(year=2000, category='economics')
>>> print ", ".join([str(l) for l in prize.laureates])
James J. Heckman, Daniel L. McFadden
```

As you can see, every `Prize` object is given a `laureates` attribute populated
with a list of its `Laureate` objects. Likewise, every `Laureate` objects is
given a `prizes` attribute with `Prize` objects.

Attributes and query parameters in the Nobel Prize API are `mixedCase`, but
this wrapper uses the more pythonic `lower_case_with_underscores` style and
takes care of the conversion when filtering and accessing attributes.

## Installation

To install Nobel, simply:

```sh
$ pip install nobel
```

## TODO

* Documentation and full reference
* Tests
* More ORM-ish stuff, like filtering using Prize, Laureate or Country objects
  as arguments
* Add relation attributes, like affiliations.

## Credits

This is inspired by the beautifully written [hipchat-api](https://github.com/dobarkod/hipchat-api) wrapper.