import unittest
from mock import Mock, sentinel, patch

from weewsgi.wee import *


class TestWee(unittest.TestCase):
    @patch('weewsgi.wee.bind')
    def test_changes_wsgi_call_to_wee_call(self, bind):
        bind.return_value = {'a': sentinel.a}
        start_response = Mock()
        app = Mock()
        app.return_value = sentinel.status, sentinel.headers, sentinel.body
        wee_app = wee(app, a='a', b='b')
        self.assertIs(
            wee_app(sentinel.environ, start_response),
            sentinel.body
        )
        bind.assert_called_once_with(sentinel.environ, dict(a='a', b='b'))
        app.assert_called_once_with(sentinel.environ, **bind.return_value)
        start_response.assert_called_once_with(
            sentinel.status, sentinel.headers)

    def test_works_with_instancemethods(self):
        class App(object):
            def __init__(self):
                self.calls = []
            @wee
            def __call__(self, environ):
                self.calls.append((self, environ))
                return sentinel.status, sentinel.headers, sentinel.body
        app = App()
        start_response = Mock()
        self.assertIs(
            app(sentinel.environ, start_response),
            sentinel.body
        )
        self.assertEqual(app.calls, [(app, sentinel.environ)])
        start_response.assert_called_once_with(
            sentinel.status, sentinel.headers)

    @patch('weewsgi.wee.bind')
    def test_wee_calls_pass_through_with_bindings(self, bind):
        bind.return_value = {'a': sentinel.a}
        app = Mock()
        wee_app = wee(app)
        self.assertIs(
            wee_app(sentinel.environ),
            app.return_value
        )
        app.assert_called_once_with(sentinel.environ, **bind.return_value)

    @patch('weewsgi.wee.bind')
    def test_when_called_without_app_it_is_a_decorator(self, bind):
        bind.return_value = {'a': sentinel.a}
        start_response = Mock()
        app = Mock()
        app.return_value = sentinel.status, sentinel.headers, sentinel.body
        wee_app = wee(a='a', b='b')(app)
        self.assertIs(
            wee_app(sentinel.environ, start_response),
            sentinel.body
        )
        bind.assert_called_once_with(sentinel.environ, dict(a='a', b='b'))
        app.assert_called_once_with(sentinel.environ, **bind.return_value)
        start_response.assert_called_once_with(
            sentinel.status, sentinel.headers)

    def test_stacking_wees_collapses_them(self):
        app = Mock()
        wee1 = wee(app, a='a1')
        wee2 = wee(wee1, b='b')
        wee3 = wee(wee2, a='a2', c='c')
        self.assertIs(wee3.app, app)
        self.assertEqual(wee3.kw, dict(a='a2', b='b', c='c'))

    def test_stacking_wee_decorators_collapses_them(self):
        @wee(a='a2', c='c')
        @wee(b='b')
        @wee(a='a1')
        def app():
            pass
        self.assertTrue(isinstance(app, wee))
        self.assertFalse(isinstance(app.app, wee))
        self.assertEqual(app.kw, dict(a='a2', b='b', c='c'))


class TestBind(unittest.TestCase):
    def test_string_rules_pull_keys_out_of_environ(self):
        environ = {'key1': sentinel.key1, 'key2': sentinel.key2}
        rules = {'arg1': 'key1', 'arg2': 'key2'}
        self.assertEqual(
            bind(environ, rules),
            {'arg1': sentinel.key1, 'arg2': sentinel.key2}
        )

    def test_ignores_keys_missing_from_environ(self):
        environ = {}
        rules = {'arg1': 'key1', 'arg2': 'key2'}
        self.assertEqual(bind(environ, rules), {})

    def test_sequence_rules_bind_elements_recursively(self):
        environ = {'key2': sentinel.key2}
        rules = {'arg': ('key1', 'key2')}
        self.assertEqual(
            bind(environ, rules),
            {'arg': sentinel.key2}
        )

    def test_callable_rules_are_iterated_over(self):
        environ = {'key2': sentinel.key2}
        rules = {'arg': lambda environ: [environ['key2']]}
        self.assertEqual(
            bind(environ, rules),
            {'arg': sentinel.key2}
        )


if __name__ == '__main__':
    unittest.main()
