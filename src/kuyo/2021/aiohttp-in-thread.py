"""
裏で aiohttp (3.7.3で確認)のサーバを起動するようなのの試作

* 参考: https://stackoverflow.com/questions/51610074/how-to-run-an-aiohttp-server-in-a-thread

  * ``on_cleanup`` が正しく呼ばれるようにスレッドの外からサーバを止められるようにした

* いい方法ではないっぽいので ``asyncio.gather`` とかで対応できるならそうした方がいい
"""
import asyncio
import logging
import threading

from aiohttp import web


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def aiohttp_app():
    async def on_startup(app):
        logger.debug("on_startup")

    async def on_cleanup(app):
        logger.debug("on_cleanup")

    async def say_hello(request):
        return web.Response(text="Hello, world")

    app = web.Application()
    app.add_routes([
        web.get("/", say_hello),
    ])
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    return app


if __name__ == "__main__":
    app = aiohttp_app()
    runner = web.AppRunner(app)

    # スレッド用のループだが、サーバの起動・終了時はメインスレッドで使う
    # (メインスレッドで async が使えない環境を想定)
    loop = asyncio.new_event_loop()

    try:
        loop.run_until_complete(runner.setup())
        site = web.TCPSite(runner, "localhost", 8080)
        loop.run_until_complete(site.start())

        t = threading.Thread(target=loop.run_forever)
        t.start()

        # t.join() して KeyboardInterrupt をとってもいいが、
        # それだとスレッド使う意味がないので input() を使った例
        while True:
            msg = input("Type `quit` to stop server: ")
            if msg == "quit":
                loop.call_soon_threadsafe(loop.stop)
                t.join()  # スレッドが止まるまで待つ
                loop.run_until_complete(runner.cleanup())
                break
    finally:
        loop.close()
