from .mouse import Mou, route, register_route
from .helper import (
    redirect,
    make_json,
    MouTemplate,
    make_response,
)
from .model import Model
from .utils import log
from .run import run

render_template = MouTemplate.render
