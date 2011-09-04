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
    def __init__(self, app, **kw):
        self.app = app
        self.kw = kw

    def __get__(self, obj, cls):
        bound = wee(self.app.__get__(obj, cls), **self.kw)
        return bound

    def __call__(self, environ, start_response):
        status, headers, body = self.app(environ, **bind(environ, self.kw))
        start_response(status, headers)
        return body
