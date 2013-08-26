from .data import NobelObject


__all__ = ['Country']


class Country(NobelObject):
    """Country."""

    attributes = ('name', 'code',)
    unique_together = ('code', 'name',)
    resource = 'country'
    resource_plural = 'countries'

    def __unicode__(self):
        return self.name
