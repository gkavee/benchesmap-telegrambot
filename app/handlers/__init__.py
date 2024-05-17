from aiogram import Router


def setup_routers() -> Router:
    from . import start, benches_handler

    router = Router()
    router.include_router(start.router)
    router.include_router(benches_handler.router)
    
    return router
