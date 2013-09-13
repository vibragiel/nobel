from .data import NobelObject


__all__ = ['Prize']


class Prize(NobelObject):
    """Nobel Prize."""

    attributes = ('category', 'year', 'laureates', 'motivation')
    unique_together = ('category', 'year',)
    resource = 'prize'
    resource_plural = 'prizes'

    @classmethod
    def _parse(cls, data, full=False):
        obj = super(Prize, cls)._parse(data, full)
        obj.year = int(data['year'])
        if 'laureates' in data:
            obj.laureates = [cls.api.laureates._parse(l, full=False)
                             for l in data['laureates']]
            if 'motivation' in data['laureates'][0]:
                obj.motivation = data['laureates'][0]['motivation']

        return obj

    def __unicode__(self):
        return u"%s, %d" % (self.category.capitalize(), self.year)
