import time

from .base_model import Model
from .utils import log


class Session(Model):
    """
    Session 是用来保存 session 的 model
    """

    def __init__(self, form):
        super().__init__(form)
        self.session_id = form.pop('session_id', '')
        self.expired_time = form.pop('expired_time', time.time() + 3600)

        form.pop('id', None)
        for k, v in form.items():
            setattr(self, k, v)

    def expired(self):
        now = time.time()
        result = self.expired_time < now
        log('expired', result, self.expired_time, now)
        return result
