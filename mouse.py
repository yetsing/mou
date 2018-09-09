import _thread
import socket
import traceback

from .utils import log
from .requset import Request
from .helper import *
from .static import static


class Mou(object):

    def __init__(self):
        self.routes_dict = {}
        self.methods_for_path = {}

    def route(self, path, methods='GET'):

        def decorator(f):
            self.routes_dict[path] = f
            self.methods_for_path[path] = methods
            return f

        return decorator

    @staticmethod
    def make_response(body):
        if isinstance(body, bytes):
            return body
        else:
            return html_response(body)

    def dispatch_request(self, request):
        """
        根据 path 调用相应的处理函数
        没有处理的 path 会返回 404
        """
        # 请求静态文件
        if request.path.startswith('/static'):
            return static(request)

        methods = self.methods_for_path.get(request.path, '')
        print(methods, request.method)
        if request.method not in methods:
            raise MethodException('HTTP method {} is not added.'.format(request.method))

        route_function = self.routes_dict.get(request.path, '')
        log('request', request, route_function, methods)

        if route_function == '':
            return error(404)

        b = route_function(request)
        return self.make_response(b)

    @staticmethod
    def receive_request(connection):
        request = b''
        buffer_size = 1024
        while True:
            r = connection.recv(buffer_size)
            request += r
            # 取到的数据长度不够 buffer_size 的时候，说明数据已经取完了。
            if len(r) < buffer_size:
                request = request.decode()
                log('request\n {}'.format(request))
                return request

    def process_request(self, connection):
        """
        接受请求并返回响应
        """
        with connection:
            r = self.receive_request(connection)
            log('request log:\n <{}>'.format(r))
            # 把原始请求数据传给 Request 对象
            try:
                request = Request(r)
                response = self.dispatch_request(request)
            except Exception as e:
                log('Internal Server Error\n', e)
                traceback.print_exc()
                response = error(500)
            log("response log:\n <{}>".format(response))
            # 把响应发送给客户端
            connection.sendall(response)

    def run(self, host, port):
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
                _thread.start_new_thread(self.process_request, (connection,))
