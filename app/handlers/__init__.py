from aiogram import Router


def setup_routers() -> Router:
    from . import benches_handler, start

    router = Router()
    router.include_router(start.router)
    router.include_router(benches_handler.router)

    return router
