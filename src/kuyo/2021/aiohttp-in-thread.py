"""
裏で aiohttp (3.7.3で確認)のサーバを起動するようなのの試作

* 参考: https://stackoverflow.com/questions/51610074/how-to-run-an-aiohttp-server-in-a-thread

  * ``on_cleanup`` が正しく呼ばれるようにスレッドの外からサーバを止められるようにした

* いい方法ではないっぽいので ``asyncio.gather`` とかで対応できるならそうした方がいい

  * それが無理ならサブプロセスでやった方が良さそうな気がするので基本的にこいつの出番はないのではと思うがなんかあるかなぁ
"""
import asyncio
import logging
import threading

from aiohttp import web


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def on_startup(app):
    logger.debug("on_startup")

async def on_cleanup(app):
    logger.debug("on_cleanup")


def aiohttp_runner():
    async def say_hello(request):
        return web.Response(text='Hello, world')

    app = web.Application()
    app.add_routes([
        web.get('/', say_hello),
    ])
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    runner = web.AppRunner(app)
    return runner


async def stop_server(loop, runner):
    await runner.cleanup()
    loop.stop()
    loop.close()


if __name__ == '__main__':
    runner = aiohttp_runner()

    main_loop = asyncio.get_event_loop()
    loop = asyncio.new_event_loop()

    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, 'localhost', 8080)
    loop.run_until_complete(site.start())

    t = threading.Thread(target=loop.run_forever)
    t.start()

    # loop が実行中なので別のループを使う必要がある
    # main_loop.run_until_complete(asyncio.sleep(1))

    # t.join() して KeyboardInterrupt をとってもいいが、
    # それだとスレッド使う意味がないので input() を使った例
    while True:
        msg = input('Type `quit` to stop server: ')
        if msg == 'quit':
            asyncio.run_coroutine_threadsafe(stop_server(loop, runner), loop)
            break
