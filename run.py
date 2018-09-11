import _thread
import socket
import traceback

from .utils import log
from .requset import Request
from .helper import *
from .static import static
from .mouse import route_dict


def finalize_request(content):
    if isinstance(content, bytes):
        return content
    else:
        return make_response(content)


def dispatch_request(request):
    """
    根据 path 调用相应的处理函数
    没有处理的 path 会返回 404
    """
    route_function = route_dict.get(request.path, '')
    log('request', request, route_function)
    if route_function == '':
        # 请求静态文件
        if request.path.startswith('/static'):
            return static(request)
        else:
            return error(404)
    b = route_function(request)
    return finalize_request(b)


def receive_request(connection):
    request = b''
    buffer_size = 1024
    while True:
        r = connection.recv(buffer_size)
        request += r
        print('buffer_size: ', r)
        # 取到的数据长度不够 buffer_size 的时候，说明数据已经取完了。
        if len(r) < buffer_size:
            request = request.decode()
            log('request\n {}'.format(request))
            return request


def process_request(connection):
    """
    接受请求并返回响应
    """
    with connection:
        r = receive_request(connection)
        log('request log:\n <{}>'.format(r))
        # 把原始请求数据传给 Request 对象
        try:
            request = Request(r)
            response = dispatch_request(request)
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
    # 初始化 socket 套路
    # 使用 with 可以保证程序中断的时候正确关闭 socket 释放占用的端口
    log('开始运行于', 'http://{}:{}'.format(host, port))
    with socket.socket() as s:
        s.bind((host, port))
        # 监听 接受 读取请求数据 解码成字符串
        s.listen()
        # 无限循环来处理请求
        while True:
            connection, address = s.accept()
            # 第二个参数类型必须是 tuple
            log('ip {}'.format(address))
            _thread.start_new_thread(process_request, (connection,))
