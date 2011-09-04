def _evaluate_rule(rule, environ):
    if isinstance(rule, basestring):
        if rule in environ:
            yield environ[rule]
    elif callable(rule):
        for value in rule(environ):
            yield value
    else:
        for sub_rule in rule:
            for value in _evaluate_rule(sub_rule, environ):
                yield value


def bind(environ, kw):
    args = {}
    for argname, rule in kw.iteritems():
        for value in _evaluate_rule(rule, environ):
            args[argname] = value
            break
    return args


class wee(object):
    def __new__(cls, __app=None, **kw):
        if __app is None:
            def dec_wee(app):
                return cls(app, **kw)
            return dec_wee
        return object.__new__(cls)

    def __init__(self, app, **kw):
        if isinstance(app, wee):
            kw = dict(app.kw, **kw)
            app = app.app
        self.app = app
        self.kw = kw

    def __get__(self, obj, cls):
        bound = wee(self.app.__get__(obj, cls), **self.kw)
        return bound

    def __call__(self, environ, start_response=None):
        ret = self.app(environ, **bind(environ, self.kw))
        if start_response is None:
            return ret
        status, headers, body = ret
        start_response(status, headers)
        return body
