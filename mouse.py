from .exception import *

route_dict = {}


def route(path):
    def decorator(f):
        route_dict[path] = f
        return f

    return decorator


def register_route(mou, url_prefix=''):
    for path, func in mou.route_dict.items():
        new_path = url_prefix + path
        if route_dict.get(new_path) is None:
            route_dict[new_path] = func
        else:
            raise PathError('This path <{}> is used.'.format(new_path))


class Mou(object):

    def __init__(self, name):
        self.name = name
        self.route_dict = {}

    def route(self, path):
        def decorator(f):
            self.add_route(path, f)
            return f

        return decorator

    def add_route(self, path, func):
        if self.route_dict.get(path) is None:
            self.route_dict[path] = func
        else:
            raise PathError('This path <{}> is used.'.format(path))
