# -*- coding: utf-8 -*-

"""
Nobel API wrapper
~~~~~~~~~~~~~~~~~

Nobel is a python wrapper for the Nobel Prize REST API. Please, read the terms
of use and full API documentation at <http://www.nobelprize.org>.

Quick listing:

   >>> import nobel
   >>> api = nobel.Api()
   >>> prizes = api.prizes.all()
   >>> laureates = api.laureates.all()
   >>> prizes[-1]
   <Prize category="peace" year=1901>
   >>> prizes[-1].laureates
   [<Laureate id=462>, <Laureate id=463>]
   >>> for laureate in prizes[-1].laureates:
   ...     print laureate, laureate.born
   ...
   Jean Henry Dunant 1828-05-08
   Frédéric Passy 1822-05-20

... or filtering:

   >>> api.laureates.filter(gender='female', born_country='Iran')
   [<Laureate id=773>, <Laureate id=817>]

... or retrieving a single resource:

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


:copyright: (c) 2013 by Gabriel Rodríguez Alberich.
:license: Apache 2.0, see LICENSE for more details.

"""

__version__ = '0.2'

from .api import Api
