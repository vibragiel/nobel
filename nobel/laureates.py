from .data import NobelObject


__all__ = ['Laureate']


class Laureate(NobelObject):
    """Nobel Laureate."""

    attributes = ('id', 'firstname', 'surname', 'born_country', 'born_city',
                  'died_country', 'died_city', 'gender', 'born', 'died',
                  'prizes')
    unique_together = ('id',)
    resource = 'laureate'
    resource_plural = 'laureates'

    @classmethod
    def _parse(cls, data, full=False):
        obj = super(Laureate, cls)._parse(data, full)
        obj.id = int(data['id'])
        if 'born' in data:
            obj.born = cls._parse_date(data['born'])
        if 'died' in data:
            obj.died = cls._parse_date(data['died'])
        if 'prizes' in data:
            obj.prizes = [cls.api.prizes._parse(p, full=False)
                          for p in data['prizes']]
        for country_field in ('born_country', 'died_country'):
            if cls._camelize(country_field) in data and \
               cls._camelize(country_field + '_code') in data:
                country = cls.api.countries()
                country.name = data[cls._camelize(country_field)]
                country.code = data[cls._camelize(country_field + '_code')]
                obj.__setattr__(country_field, country)

        return obj

    def __unicode__(self):
        if hasattr(self, 'surname'):
            return u'%s %s' % (self.firstname, self.surname)
        else:
            return self.firstname
