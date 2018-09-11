import datetime
import json
import os
import time
import uuid

from jinja2 import FileSystemLoader, Environment
from .session import Session


def initialized_environment():
    parent = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(parent, 'templates')
    # 创建一个加载器, jinja2 会从这个目录中加载模板
    loader = FileSystemLoader(path)
    # 用加载器创建一个环境, 有了它才能读取模板文件
    e = Environment(loader=loader)
    return e


class MouTemplate:
    e = initialized_environment()

    @classmethod
    def render(cls, filename, *args, **kwargs):
        # 调用 get_template() 方法加载模板并返回
        template = cls.e.get_template(filename)
        # 用 render() 方法渲染模板
        # 可以传递参数
        return template.render(*args, **kwargs)


def error(code):
    """
    根据 code 返回不同的错误响应
    目前只有 404
    """
    # 之前上课我说过不要用数字来作为字典的 key
    # 但是在 HTTP 协议中 code 都是数字似乎更方便所以打破了这个原则
    e = {
        404: b'HTTP/1.x 404 NOT FOUND\r\n\r\n<h1>NOT FOUND</h1>',
        500: b'HTTP/1.x 500 Internal Server Error\r\n\r\n<h1>Internal Server Error</h1>'
    }
    return e.get(code, b'')


def format_expired_time(t):
    date = datetime.datetime.utcfromtimestamp(t)
    gmt_format = '%a, %d %b %Y %H:%M:%S GMT'
    ts = date.strftime(gmt_format)
    return ts


def formatted_header(headers, code):
    """
    Content-Type: text/html
    Set-Cookie: user=gua
    """
    state_message = {
        200: 'OK',
        302: 'Move temporarily',
    }
    header = 'HTTP/1.1 {} {}\r\n'.format(code, state_message[code])
    header += ''.join([
        '{}: {}\r\n'.format(k, v) for k, v in headers.items()
    ])
    return header


def redirect(url, headers=None, **kwargs):
    """
    浏览器在收到 302 响应的时候
    会自动在 HTTP header 里面找 Location 字段并获取一个 url
    然后自动请求新的 url
    """
    h = {
        'Location': url,
    }
    if headers is None:
        headers = h
    else:
        headers.update(h)
    return make_response('', code=302, headers=headers, **kwargs)


def set_cookie(form):
    session_id = str(uuid.uuid4())
    expired_time = form.pop('expired_time', time.time() + 3600)
    path = form.pop('path', '/')
    cookie = 'session_id={}; Expires={}; Path={}'.format(
        session_id,
        format_expired_time(expired_time),
        path
    )
    if form.get('max_age', None) is not None:
        cookie += '; Max-Age={}'.format(form.pop('max_age'))
    if form.get('domain', None) is not None:
        cookie += '; Domain={}'.format(form.pop('domain'))
    if form.get('secure', None) is not None:
        cookie += '; Secure={}'.format(form.pop('secure'))
    if form.get('samesite', None) is not None:
        cookie += '; SameSite={}'.format(form.pop('samesite'))
    if form.pop('httponly', True):
        cookie += '; HttpOnly'
    form['session_id'] = session_id
    form['expired_time'] = expired_time
    Session.new(form)
    return cookie


def make_response(body, code=200, headers=None, cookie=None):
    h = {
        'Content-Type': 'text/html',
    }
    if headers is None:
        headers = h
    else:
        headers.update(h)

    if cookie is not None:
        headers['Set-Cookie'] = set_cookie(cookie)
    header = formatted_header(headers, code)
    r = header + '\r\n' + body
    return r.encode()


def make_json(data):
    """
    返回 json 格式的 body 数据
    """
    header = {
        'Content-Type': 'application/json',
    }
    body = json.dumps(data, ensure_ascii=False, indent=2)
    return make_response(body, headers=header)
