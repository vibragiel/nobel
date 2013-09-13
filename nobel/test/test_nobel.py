# -*- coding: utf-8 -*-
import datetime
import sys
import mock
import pytest
import nobel
from nobel.prizes import Prize
from nobel.laureates import Laureate
from nobel.countries import Country
from nobel.api import NobelError, NotFoundError, MultipleObjectsError, \
    ServiceUnavailable, BadRequest
from nobel.data import NobelObject


class TestApi:

    def setup_method(self, method):
        self.api = nobel.Api()

    def test_base_url(self):
        assert self.api.BASE_URL == 'http://api.nobelprize.org/v1/'
        assert self.api.base_url == self.api.BASE_URL

    def test_base_url_custom(self):
        api = nobel.Api(base_url='http://example.com/v2/')
        assert api.base_url == 'http://example.com/v2/'

    def test_prizes(self):
        assert issubclass(self.api.prizes, Prize)
        assert hasattr(self.api.prizes, 'api')
        assert self.api.prizes.api == self.api

    def test_laureates(self):
        assert issubclass(self.api.laureates, Laureate)
        assert hasattr(self.api.laureates, 'api')
        assert self.api.laureates.api == self.api

    def test_countries(self):
        assert issubclass(self.api.countries, Country)
        assert hasattr(self.api.countries, 'api')
        assert self.api.countries.api == self.api

    def test_unwrap_response_no_errors(self):
        class MockedResponse(object):
            status_code = 200

            def json(self):
                return {}

        json = self.api._unwrap_response(MockedResponse())
        assert json == {}

    def test_unwrap_response_error_400(self):
        class MockedResponse(object):
            status_code = 400

            def json(self):
                return {'error': 'Test error message.'}

        with pytest.raises(BadRequest) as excinfo:
            self.api._unwrap_response(MockedResponse())
        assert excinfo.value.args[0] == 'Test error message.'

    def test_unwrap_response_error_400_message(self):
        class MockedResponse(object):
            status_code = 400

            def json(self):
                return {'error': {'message': 'Test error message.'}}

        with pytest.raises(BadRequest) as excinfo:
            self.api._unwrap_response(MockedResponse())
        assert excinfo.value.args[0] == 'Test error message.'

    def test_unwrap_response_error_503(self):
        class MockedResponse(object):
            status_code = 503

            def json(self):
                return {'error': 'Test error message.'}

        with pytest.raises(ServiceUnavailable) as excinfo:
            self.api._unwrap_response(MockedResponse())
        assert excinfo.value.args[0] == 'Test error message.'

    def test_unwrap_response_error_other(self):
        class MockedResponse(object):
            status_code = 509

            def json(self):
                return {'error': 'Test error message.'}

        with pytest.raises(NobelError) as excinfo:
            self.api._unwrap_response(MockedResponse())
        assert excinfo.value.args[0] == '509: Test error message.'

    def test_unwrap_response_error_200_with_error(self):
        class MockedResponse(object):
            status_code = 200

            def json(self):
                return {'error': 'Test error message.'}

        with pytest.raises(NobelError) as excinfo:
            self.api._unwrap_response(MockedResponse())
        assert excinfo.value.args[0] == '200: Test error message.'

    @mock.patch('nobel.api.requests')
    def test_get(self, mocked_requests):
        class MockedResponse(object):
            status_code = 200

            def json(self):
                return {'response': 'test_get'}

        mocked_requests.get = mock.MagicMock()
        mocked_requests.get.return_value = MockedResponse()
        resp = self.api._get('example.json', parameter_1='foo',
                             parameter_2='bar')
        mocked_requests.get.assert_called_once_with(
            'http://api.nobelprize.org/v1/example.json',
            params={'parameter_1': 'foo', 'parameter_2': 'bar'}
        )
        assert resp == {'response': 'test_get'}


class TestData:

    def setup_method(self, method):
        api = nobel.Api()
        self.MyObject = type('MyObject', (NobelObject,),
                             dict(attributes=('attr_a', 'attr_b', 'attr_c'),
                                  unique_together=('attr_a', 'attr_b'),
                                  resource='object', resource_plural='objects',
                                  api=api))

    def test_uncamelize(self):
        assert NobelObject._uncamelize('lower') == 'lower'
        assert NobelObject._uncamelize('Case') == 'case'
        assert NobelObject._uncamelize('mixedCaseStr') == 'mixed_case_str'
        assert NobelObject._uncamelize('District9Movie') == 'district9_movie'

    def test_camelize(self):
        assert NobelObject._camelize('lower') == 'lower'
        assert NobelObject._camelize('mixed_case_string') == 'mixedCaseString'
        assert NobelObject._camelize('district9_movie') == 'district9Movie'

    def test_parse(self):
        data = {'attrA': 4, 'attrC': 'foo', 'attrD': 'bar'}
        obj = self.MyObject._parse(data)
        assert hasattr(obj, 'attr_a')
        assert hasattr(obj, 'attr_c')
        assert not hasattr(obj, 'attr_b')
        assert not hasattr(obj, 'attr_d')
        assert not hasattr(obj, 'attrA')
        assert not hasattr(obj, 'attrC')
        assert not hasattr(obj, 'attrD')
        assert obj.attr_a == 4
        assert obj.attr_c == 'foo'
        assert obj.full is False
        full_obj = self.MyObject._parse(data, full=True)
        assert full_obj.full is True

    def test_parse_date(self):
        date = datetime.date(year=2013, month=7, day=23)
        assert NobelObject._parse_date('2013-07-23') == date
        assert NobelObject._parse_date('9999-99-99') is None
        assert NobelObject._parse_date(9999) is None
        assert NobelObject._parse_date(None) is None

    @mock.patch('nobel.Api._get')
    def test_filter(self, mocked_get):
        mocked_get.return_value = {'objects': [{'attrA': 'foo'},
                                               {'attrA': 'bar'}]}
        all_objs = self.MyObject.filter()
        mocked_get.assert_called_once_with('object.json')
        assert len(all_objs) == 2
        assert isinstance(all_objs[0], self.MyObject)
        assert isinstance(all_objs[1], self.MyObject)
        assert all_objs[0].full is True
        assert all_objs[1].full is True

    @mock.patch('nobel.Api._get')
    def test_filter_with_parameters(self, mocked_get):
        self.MyObject.filter(attr_a='foo', attr_d='bar')
        mocked_get.assert_called_once_with('object.json', attrA='foo',
                                           attrD='bar')

    @mock.patch('nobel.data.NobelObject.filter')
    def test_all(self, mocked_filter):
        self.MyObject.all()
        mocked_filter.assert_called_once_with()

    @mock.patch('nobel.Api._get')
    def test_get(self, mocked_get):
        mocked_get.return_value = {'objects': [{'attrA': 'foo'}]}
        obj = self.MyObject.get(attr_a='foo')
        mocked_get.assert_called_once_with('object.json', attrA='foo')
        assert isinstance(obj, self.MyObject)
        assert obj.full is True

    @mock.patch('nobel.Api._get')
    def test_get_multiple(self, mocked_get):
        mocked_get.return_value = {'objects': [{'attrA': 'foo'},
                                               {'attrA': 'foo'}]}
        with pytest.raises(MultipleObjectsError) as excinfo:
            self.MyObject.get(attr_a='foo')
        assert excinfo.value.args[0] == 'Multiple objects returned when only' \
                                        ' one was expected.'

    @mock.patch('nobel.Api._get')
    def test_get_not_found(self, mocked_get):
        mocked_get.return_value = {'objects': []}
        with pytest.raises(NotFoundError) as excinfo:
            self.MyObject.get(attr_a='foo')
        assert excinfo.value.args[0] == 'No resources found.'

    @mock.patch('nobel.Api._get')
    def test_update(self, mocked_get):
        obj = self.MyObject()
        obj.attr_a = 'foo'
        obj.attr_b = 'bar'
        obj.attr_e = 'baz'
        assert obj.full is False
        mocked_get.return_value = {'objects': [{'attrA': 'foo', 'attrB': 'baz',
                                                'attrC': 2, 'attrD': 'qux'}]}
        obj._update()
        assert obj.full is True
        assert obj.attr_a == 'foo'
        assert obj.attr_b == 'baz'  # updates old values
        assert hasattr(obj, 'attr_c')  # populates missing declared attributes
        assert obj.attr_c == 2
        assert not hasattr(obj, 'attr_d')  # undeclared attrs not populated
        assert obj.attr_e == 'baz'  # other attributes respected

    @mock.patch('nobel.Api._get')
    def test_undefined_attribute_access(self, mocked_get):
        obj = self.MyObject()
        obj.attr_a = 1
        obj.attr_b = 'foo'
        mocked_get.return_value = {'objects': [{'attrA': 'foo', 'attrB': 'baz',
                                                'attrC': 2, 'attrD': 'qux'}]}
        assert obj.attr_c == 2

    @mock.patch('nobel.Api._get')
    def test_undefined_full_attribute_access(self, mocked_get):
        obj = self.MyObject()
        del obj.full
        assert obj.full is False

    def test_repr(self):
        obj = self.MyObject()
        obj.attr_a = u'fóo'
        obj.attr_b = 2
        assert obj.__repr__() == '<MyObject attr_a="fóo" attr_b=2>'

    def test_str(self):
        obj = self.MyObject()
        obj.attr_a = u'fóo'
        obj.attr_b = 2
        assert obj.__str__() == 'MyObject'

    def test_unicode(self):
        obj = self.MyObject()
        obj.attr_a = u'fóo'
        obj.attr_b = 2
        if sys.version_info < (3, 0):
            assert obj.__unicode__() == u'MyObject'


class TestLaureate:

    def setup_method(self, method):
        self.api = nobel.Api()

    @mock.patch('nobel.api.Api.countries')
    @mock.patch('nobel.prizes.Prize._parse')
    def test_parse(self, mocked_parse, mocked_countries):
        mocked_parse.return_value = 'prize object'
        mocked_countries.side_effect = [type('Country', (), {})(),
                                        type('Country', (), {})()]
        data = {u'id': u'4', u'firstname': u'Alfred', u'surname': u'Nobel',
                u'bornCountry': u'Sweden', u'bornCity': u'Stockholm',
                u'diedCountry': u'Italy', u'diedCity': u'Sanremo',
                u'gender': u'male', u'born': u'1833-10-21',
                u'died': u'1896-12-10', u'prizes': ['prize_1', 'prize_2'],
                u'bornCountryCode': 'SE', u'diedCountryCode': u'IT'
                }
        obj = self.api.laureates._parse(data)
        assert obj.id == 4
        assert obj.born == datetime.date(year=1833, month=10, day=21)
        assert obj.died == datetime.date(year=1896, month=12, day=10)
        mocked_parse.assert_any_call('prize_1', full=False)
        mocked_parse.assert_any_call('prize_2', full=False)
        assert mocked_parse.call_count == 2
        assert obj.prizes == ['prize object', 'prize object']
        assert obj.born_country.name == u'Sweden'
        assert obj.born_country.code == u'SE'
        assert obj.died_country.name == u'Italy'
        assert obj.died_country.code == u'IT'

    def test_unicode(self):
        data = {u'id': u'4', u'firstname': u'Toño', u'surname': u'Ñandú'}
        obj = self.api.laureates._parse(data)
        if sys.version_info < (3, 0):
            assert obj.__unicode__() == u'Toño Ñandú'
        else:
            assert obj.__str__() == 'Toño Ñandú'

    @mock.patch('nobel.data.NobelObject.__getattr__')
    def test_unicode_without_surname(self, mocked_getattr):
        mocked_getattr.side_effect = AttributeError
        data = {u'id': u'4', u'firstname': u'Toño'}
        obj = self.api.laureates._parse(data)
        if sys.version_info < (3, 0):
            assert obj.__unicode__() == u'Toño'
        else:
            assert obj.__str__() == 'Toño'


class TestPrize:

    def setup_method(self, method):
        self.api = nobel.Api()

    @mock.patch('nobel.laureates.Laureate._parse')
    def test_parse(self, mocked_parse):
        mocked_parse.return_value = 'laureate object'
        data = {u'category': u'physics', u'year': u'2006',
                u'laureates': ['laureate_1', 'laureate_2']}
        obj = self.api.prizes._parse(data)
        assert obj.year == 2006
        mocked_parse.assert_any_call('laureate_1', full=False)
        mocked_parse.assert_any_call('laureate_2', full=False)
        assert mocked_parse.call_count == 2
        assert obj.laureates == ['laureate object', 'laureate object']

    @mock.patch('nobel.laureates.Laureate._parse')
    def test_parse_motivation_in_laureate(self, mocked_parse):
        mocked_parse.return_value = 'laureate object'
        data = {u'category': u'physics', u'year': u'2006',
                u'laureates': [{u'id': 1, u'motivation': u'because'}]}
        obj = self.api.prizes._parse(data)
        assert obj.motivation == u'because'

    @mock.patch('nobel.laureates.Laureate._parse')
    def test_parse_motivation_in_prize(self, mocked_parse):
        mocked_parse.return_value = 'laureate object'
        data = {u'category': u'physics', u'year': u'2006',
                u'motivation': u'because'}
        obj = self.api.prizes._parse(data)
        assert obj.motivation == u'because'

    def test_unicode(self):
        data = {u'category': u'physics', u'year': u'2006'}
        obj = self.api.prizes._parse(data)
        if sys.version_info < (3, 0):
            assert obj.__unicode__() == u'Physics, 2006'
        else:
            assert obj.__str__() == 'Physics, 2006'


class TestCountry:

    def setup_method(self, method):
        self.api = nobel.Api()

    def test_unicode(self):
        data = {u'name': u'Spain', u'code': u'ES'}
        obj = self.api.countries._parse(data)
        if sys.version_info < (3, 0):
            assert obj.__unicode__() == u'Spain'
        else:
            assert obj.__str__() == 'Spain'
