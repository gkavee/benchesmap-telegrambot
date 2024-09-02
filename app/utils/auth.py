import aiohttp

from config import API_URL


async def get_token(username: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{API_URL}/auth/tg/login?telegram_username={username}"
        ) as response:
            if response.status == 200:
                data = await response.json()
                if "token" in data:
                    return data["token"]
            return "token is none"
