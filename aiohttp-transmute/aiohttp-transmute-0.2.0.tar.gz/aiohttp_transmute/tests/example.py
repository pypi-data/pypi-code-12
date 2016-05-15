from aiohttp import web
import aiohttp_transmute
from aiohttp_transmute import (
    describe, TransmuteUrlDispatcher, add_swagger
)

async def handle(request):
    text = "Hello, can you hear me?"
    return web.Response(body=text.encode('utf-8'))


@aiohttp_transmute.describe(paths="/multiply")
async def multiply(request, left: int, right: int) -> int:
    return left * right


@aiohttp_transmute.describe(paths="/id/{my_id}")
async def get_id(request, my_id: str) -> str:
    return "your id is: " + my_id


def create_app(loop):
    app = web.Application(loop=loop, router=TransmuteUrlDispatcher())
    app.router.add_route('GET', '/', handle)
    app.router.add_transmute_route(multiply)
    app.router.add_transmute_route(get_id)
    # this should be at the end, to ensure all routes are considered when
    # constructing the handler.
    add_swagger(app, "/swagger.json", "/swagger")
    return app
