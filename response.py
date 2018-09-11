class Response(object):

    def __init__(self, body, headers=None):
        self.body = body
        self.status_code = 200
        self.headers = {
            'Content-Type': 'text/html',
        }
        if headers is not None:
            self.headers.update(headers)

    def add_header(self, headers):
        self.headers.update(headers)

    def formatted_header(self):
        phrase = {
            200: '200 OK',
            301: '301 Moved Permanently',
            302: '302 Move temporarily',
        }
        header = 'HTTP/1.1 {}\r\n'.format(phrase[self.status_code])
        header += ''.join([
            '{}: {}\r\n'.format(k, v) for k, v in self.headers.items()
        ])
        return header

    def get_bytes(self):
        header = self.formatted_header()
        r = header + '\r\n' + self.body
        return r.encode()

    def set_cookie(self, key, value, max_age=3600,
                   expires=None, path='/', domain=None,
                   secure=None, samesite=None, httponly=True):
        s = '{}={}; '.format(key, value)
        if expires is not None:
            s += 'Expires={}; '.format(expires)
        if domain is not None:
            s += 'Domain={}; '.format(domain)
        if secure is not None:
            s += 'Secure={}; '.format(secure)
        if samesite is not None:
            samesite: str
            samesite = samesite.capitalize()
            if samesite not in ('Strict', 'Lax'):
                raise TypeError('The samesite must be Strict or Lax.')
            else:
                s += 'SameSite={}; '.format(samesite)
        if httponly:
            s += 'HttpOnly; '
        s += 'Max-Age={}; Path={}'.format(
            max_age,
            path,
        )

        h = {
            'Set-Cookie': s,
        }
        self.add_header(h)
