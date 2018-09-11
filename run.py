import _thread
import socket
import threading
import traceback

from .utils import log
from .requset import Request
from .helper import *
from .static import static
from .mouse import route_dict

request = Request()


def finalize_request(content):
    if isinstance(content, bytes):
        return content
    else:
        r = make_response(content)
        return r.get_bytes()


def dispatch_request():
    """
    根据 path 调用相应的处理函数
    没有处理的 path 会返回 404
    """
    route_function = route_dict.get(request.path, error)
    log('request', request, route_function)
    if request.path.startswith('/static'):
        return static(request)
    b = route_function()
    return finalize_request(b)


def receive_request(connection):
    req = b''
    buffer_size = 521
    while True:
        r = connection.recv(buffer_size)
        req += r
        print('buffer_size: ', r)
        # 取到的数据长度不够 buffer_size 的时候，说明数据已经取完了。
        if len(r) < buffer_size:
            req = req.decode()
            log('request\n {}'.format(req))
            return req


def process_request(connection):
    """
    接受请求并返回响应
    """
    with connection:
        r = receive_request(connection)
        log('request log:\n <{}>'.format(r))
        # 把原始请求数据传给 Request 对象
        try:
            request.set(r)
            response = dispatch_request()
        except:
            log('Internal Server Error')
            traceback.print_exc()
            response = error(500)
        log("response log:\n <{}>".format(response))
        # 把响应发送给客户端
        connection.sendall(response)


def run(host, port):
    """
    启动服务器
    """
    log('开始运行于', 'http://{}:{}'.format(host, port))
    with socket.socket() as s:
        s.bind((host, port))
        s.listen()
        while True:
            connection, address = s.accept()
            log('ip {}'.format(address))
            _thread.start_new_thread(process_request, (connection,))
