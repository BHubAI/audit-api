import logging

import lambdawarmer
from mangum import Mangum

from presentation.api.main import app
from presentation.di_container import Container

logger = logging.getLogger()
logger.setLevel(level=logging.INFO)


handler = Mangum(app)
container = Container()


@lambdawarmer.warmer
def request_handler(event, context):
    """
    This function is used to handle API requests.
    """
    return handler(event, context)
