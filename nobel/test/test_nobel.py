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
