import datetime
import re
from .api import NotFoundError, MultipleObjectsError


class NobelObject(object):
    """Nobel data object.

    Internal class, inteded to be subclassed by the other objects
    representing data from the Nobel API (Prize, Laureate, Country).

    Do not use directly.

    """

    attributes = []
    unique_together = []
    resource = ''
    resource_plural = ''
    api = None

    @staticmethod
    def _uncamelize(name):
        """Convert from mixedCase to lower_case_with_underscores."""

        first = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', first).lower()

    @staticmethod
    def _camelize(name):
        """Convert from lower_case_with_underscores to mixedCase."""

        def camelcase():
            yield type(name).lower
            while True:
                yield type(name).capitalize

        camel = camelcase()
        return "".join(camel.next()(x) if x else '_' for x in name.split("_"))

    @classmethod
    def _parse(cls, data, full=False):
        """Factory method.

        Parses JSON data and returns resource instance. Attributes must be
        defined in the `attributes` class attribute. Takes care of conversion
        from Nobel API mixedCase to friendlier lower_case_with_underscores.

        """

        obj = cls()
        for attr in data:
            if cls._uncamelize(attr) in cls.attributes:
                setattr(obj, cls._uncamelize(attr), data[attr])
        obj.full = full
        return obj

    @staticmethod
    def _parse_date(data):
        """Convert a string date into a proper Python datetime."""

        try:
            return datetime.datetime.strptime(data, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            return None

    @classmethod
    def filter(cls, **kwargs):
        """Filter objects.

        Returns a list of resource instances filtered by the arguments passed,
        which must be valid query parameters for the resource as defined by
        the Nobel API. Conversion from Nobel API mixedCase to friendlier
        lower_case_with_underscores and vice versa is automatic.

        """

        camel_kwargs = dict((cls._camelize(k), v) for k, v in kwargs.items())
        data = cls.api._get(cls.resource + '.json', **camel_kwargs)
        return [cls._parse(p, full=True) for p in data[cls.resource_plural]]

    @classmethod
    def all(cls):
        """List all objects.

        Returns a list of all resource instances.

        """
        return cls.filter()

    @classmethod
    def get(cls, **kwargs):
        """Get a single object.

        Return a single resource instance univocally defined by the arguments
        passed. See the `unique_together` attribute.

        """

        data = cls.api._get(cls.resource + '.json', **kwargs)
        if len(data[cls.resource_plural]) == 0:
            raise NotFoundError('No resources found.')
        elif len(data[cls.resource_plural]) > 1:
            raise MultipleObjectsError('Multiple objects returned when only '
                                       'one was expected.')
        obj = cls._parse(data[cls.resource_plural][0], full=True)
        return obj

    def __init__(self):
        self.full = False

    def _update(self):
        """Update object data.

        Updates instance attributes with fresh data from the API server.
        Populates possibly missing attributes and sets `full` to `True`.
        Attributes which univocally define an object must be included in the
        `unique_together` class attribute.

        """

        obj = self.__class__.get(**dict([(field, self.__getattribute__(field))
                                         for field in self.unique_together]))
        for attribute in self.__class__.attributes:
            if hasattr(obj, attribute):
                self.__setattr__(attribute, obj.__getattribute__(attribute))
        self.full = True

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        classname = self.__class__.__name__
        params = []
        for field in self.unique_together:
            if hasattr(self, field):
                value = self.__getattribute__(field)
                if isinstance(value, basestring):
                    params.append('%s="%s"' % (field, value))
                else:
                    params.append('%s=%s' % (field, value))
        return '<%s %s>' % (classname, " ".join(params))

    def __getattr__(self, name):
        """Updates instance with fresh data from the server if a well-known
        but undefined attribute is accessed."""

        if name == 'full':
            self.full = False
        if not self.full and name in self.__class__.attributes:
            self._update()
        return self.__getattribute__(name)
