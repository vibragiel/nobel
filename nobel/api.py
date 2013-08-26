import requests


class NobelError(Exception):
    """Nobel API error."""


class NotFoundError(NobelError):
    """Specified resource not found."""


class MultipleObjectsError(NobelError):
    """Multiple objects returned."""


class ServiceUnavailable(NobelError):
    """The service is temporarily unavailably."""


class BadRequest(NobelError):
    """Error in data provided in the request."""


class Api(object):
    """API wrapper.

    If needed, API base url (defaulting to Api.BASE_URL) can be set
    using the `base_url` optional argument."""

    BASE_URL = 'http://api.nobelprize.org/v1/'

    def __init__(self, base_url=None):

        self.base_url = base_url or self.BASE_URL
        self._prize_class = None
        self._laureate_class = None
        self._country_class = None

    @staticmethod
    def _unwrap_response(resp):
        code = resp.status_code
        json = resp.json()
        errmsg = {}
        if 'error' in json:
            if isinstance(json['error'], unicode):
                errmsg = json['error']
            else:
                errmsg = json.get('message', 'Unknown error.')

        # For some reson, errors in the country resource come as HTTP 200
        if code == 200 and not 'error' in json:
            return json
        elif code == 400:
            raise BadRequest(errmsg)
        elif code == 503:
            raise ServiceUnavailable(errmsg)
        else:
            raise NobelError('%d: %s' % (code, errmsg))

    def _get(self, resource, **kwargs):
        url = self.base_url + resource
        resp = requests.get(url, params=kwargs)
        return self._unwrap_response(resp)

    @property
    def prizes(self):
        if self._prize_class is None:
            from .prizes import Prize
            self._prize_class = type('Prize', (Prize,), dict(api=self))
        return self._prize_class

    @property
    def laureates(self):
        if self._laureate_class is None:
            from .laureates import Laureate
            self._laureate_class = type('Laureate', (Laureate,),
                                        dict(api=self))
        return self._laureate_class

    @property
    def countries(self):
        if self._country_class is None:
            from .countries import Country
            self._country_class = type('Country', (Country,),
                                       dict(api=self))
        return self._country_class
