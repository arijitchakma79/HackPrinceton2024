from flask import Blueprint
from handlers.handlers import Handlers

Routes = Blueprint('routes', __name__)


handlers = Handlers()


@Routes.route('/', methods=['GET'])
def print_hello_world():
    return handlers.print_hello_world()
