import os


def safe_path(path):
    if '..' in path:
        raise FileNotFoundError("No such file or directory: '{}'".format(path))
    else:
        return path


def static(request):
    """
    静态资源的处理函数, 读取图片（或 JS 代码）并生成响应返回
    """
    parent = os.path.dirname(os.path.dirname(__file__))
    print('parent', parent)
    filename = safe_path(request.path)
    path = parent + filename
    if not os.path.isfile(path):
        raise FileNotFoundError("No such file or directory: '{}'".format(path))
    with open(path, 'rb') as f:
        header = b'HTTP/1.x 200 OK\r\n\r\n'
        r = header + f.read()
        return r
