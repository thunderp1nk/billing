import logging
from functools import wraps

from aiohttp import web

from core.errors import ValidationError
from core.utils import check_required_args


logger = logging.getLogger()


def dataclass_connector(dataclass=None):

    def wrapper(handler_method):

        @wraps(handler_method)
        async def request_handler_wrapper(request):
            json_data = await request.json()

            try:
                check_required_args(json_data, dataclass)
                return await handler_method(request, json_data, dataclass)
            except ValidationError as e:
                return web.json_response(data={'error': e.error}, status=400)
            except OSError as e:
                logger.error([str(e), type(e)])
                return web.Response(status=500)

        return request_handler_wrapper
    return wrapper
