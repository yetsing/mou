import datetime
import json
import os
import time
import uuid

from jinja2 import FileSystemLoader, Environment

from .response import Response
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


def error(status_code=404):
    """
    根据 status_code 返回不同的错误响应
    目前只有 404
    """
    # 之前上课我说过不要用数字来作为字典的 key
    # 但是在 HTTP 协议中 status_code 都是数字似乎更方便所以打破了这个原则
    e = {
        404: b'HTTP/1.x 404 NOT FOUND\r\n\r\n<h1>NOT FOUND</h1>',
        500: b'HTTP/1.x 500 Internal Server Error\r\n\r\n<h1>Internal Server Error</h1>'
    }
    return e.get(status_code, b'')


def format_expired_time(t):
    date = datetime.datetime.utcfromtimestamp(t)
    gmt_format = '%a, %d %b %Y %H:%M:%S GMT'
    ts = date.strftime(gmt_format)
    return ts


def redirect(url, status_code=302, headers=None, **kwargs):
    h = {
        'Location': url,
    }
    if headers is None:
        headers = h
    else:
        headers.update(h)

    body = '''
    <!DOCTYPE html>
    <html>
        <head>
            <meta charset="UTF-8">
            <title>跳转中......</title>
        </head>
        <body>
            <p>如果页面没有自动跳转，请点击下面的链接手动跳转。</p>
            <a>{}</a>
        </body>
    </html>
    '''.format(url)

    response = Response(body, headers=headers)
    response.status_code = status_code
    return response


def make_response(content):
    headers = None
    status_code = None
    response = content

    if isinstance(content, tuple):
        length = len(content)
        if length == 3:
            body, status_code, headers = content
        elif length == 2:
            if isinstance(content[1], dict):
                body, headers = content
            else:
                body, status_code = content
        else:
            raise TypeError(
                'The view function did not return a valid response tuple.'
                ' The tuple must have the form (body, status_code, headers),'
                ' (body, status_code), or (body, headers).'
            )
    if content is None:
        raise TypeError(
            'The view function return None.'
        )

    if not isinstance(content, Response):
        if isinstance(content, str):
            response = Response(content)
        else:
            raise TypeError(
                'The view function did not return a valid response string.'
            )
    if headers is not None:
        response.add_header(headers)

    if status_code is not None:
        response.status_code = status_code

    return response


def make_json(data):
    """
    返回 json 格式的 body 数据
    """
    headers = {
        'Content-Type': 'application/json',
    }
    body = json.dumps(data, ensure_ascii=False, indent=2)
    return Response(body, headers=headers)
