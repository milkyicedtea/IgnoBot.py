import asyncio
import time
from typing import Literal

import aiohttp
import dotenv
import requests

from Utils.logger import logger
from cogs.Cog_Utils.osspy.Enums import GameMode
from cogs.Cog_Utils.osspy.models.beatmap import BeatmapExtended, Beatmap, Beatmapset, Score


class OsuToken:
    def __init__(self, token: dict):
        self.__token_type: str = token['token_type']
        self.__expires_in: int = token['expires_in']
        self.__access_token: str = token['access_token']

    def get_token_type(self) -> str:
        return self.__token_type

    def get_expires_in(self) -> int:
        return self.__expires_in

    def get_access_token(self) -> str:
        return self.__access_token


class RateLimiter:
    def __init__(self, calls: int, period: float):
        self.calls = calls
        self.period = period
        self.timestamps = []

    async def __aenter__(self):
        while len(self.timestamps) >= self.calls:
            now = time.time()
            if now - self.timestamps[0] > self.period:
                self.timestamps.pop(0)
            else:
                await asyncio.sleep(self.period - (now - self.timestamps[0]))
        self.timestamps.append(time.time())
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class Osspy:
    def __init__(self):
        self.client_id: str = dotenv.get_key('.env', 'OSU_CLIENT_ID')
        self.client_secret: str = dotenv.get_key('.env', 'OSU_CLIENT_SECRET')
        self.token: OsuToken = self.auth()  # Authenticate on init
        self.base_url = 'https://osu.ppy.sh/api/v2'
        self.rate_limiter = RateLimiter(calls = 60, period = 60)

    def auth(self) -> OsuToken:
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials',
            'scope': 'public',
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        token_json = requests.post("https://osu.ppy.sh/oauth/token", params, headers = headers).json()
        logger.debug(token_json)
        return OsuToken(token_json)

    async def _request(self, endpoint: str, params: dict = None) -> dict:
        async with self.rate_limiter:
            url = f'{self.base_url}/{endpoint}'
            headers = {"Authorization": f"Bearer {self.token.get_access_token()}"}

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers = headers, params = params) as response:
                    if response.status == 401:
                        # token expired, refresh and retry
                        self.token = self.auth()
                        headers["Authorization"] = f'Bearer {self.token.get_access_token()}'
                        async with session.get(url, headers = headers, params = params) as retry_response:
                            return await retry_response.json()
                    return await response.json()

    async def get_beatmap(self, beatmap_id: int) -> BeatmapExtended:
        beatmap_data = await self._request(f'beatmaps/{beatmap_id}')
        print(beatmap_data)
        print(beatmap_data['data']['embeds'])
        return BeatmapExtended(**beatmap_data)

    async def get_beatmapset(self, beatmapset_id) -> Beatmapset:
        print('getting beatmapset..')
        beatmapset = await self._request(f'beatmapsets/{beatmapset_id}')
        return Beatmapset(**beatmapset)

    async def get_score(
            self,
            user_id: int | str = None,
            score_type: Literal['best', 'firsts', 'recent'] | None = None
    ) -> Score:
        if not user_id:
            scores = await self._request('scores', {'ruleset': 'osu'})
            score = scores['scores'][0]
            return Score(**score)
        else:
            if score_type:
                score = await self._request(
                    f'users/{user_id}/scores/{score_type}',
                    {'ruleset': 'osu', 'limit': '1'}
                )
            else:
                score = await self._request(
                    f'users/{user_id}/scores/recent',
                    {'ruleset': 'osu', 'limit': '1'}
                )
            return Score(**score)


    async def get_user(self, user_id: int) -> dict:
        return await self._request(f'users/{user_id}')

    async def get_user_scores(self, user_id: int, score_type: Literal['best', 'recent'] = 'recent', include_fails: bool = True) -> list:
        """Get user scores. score_type can be 'best', 'recent' or"""
        params = {'include_fails': '1' if include_fails else '0'}
        return [await self._request(f'users/{user_id}/scores/{score_type}', params)]

    async def get_user_recent_activity(self, user_id: int, limit: int = 5) -> list:
        return [await self._request(f'users/{user_id}/recent_activity', {'limit': limit})]

    async def get_user_beatmaps(self, user_id: int, map_type: Literal['favourite', 'graveyard', 'loved', 'ranked'] = 'favourite') -> list:
        """Get user beatmaps. map_type can be 'favourite', 'graveyard', 'loved', or 'ranked'"""
        response = requests.get(
            url = f'https://osu.ppy.sh/api/v2/users/{user_id}/beatmapsets/{map_type}',
            headers = {"Authorization": f"Bearer {self.token.get_access_token()}"}
        )
        return response.json()

    async def get_user_kudosu(self, user_id: int) -> dict:
        """Get user's kudosu history"""
        return await self._request(f"users/{user_id}/kudosu")

    async def search_beatmaps(self, query: str, mode: GameMode = None) -> list[Beatmap]:
        """Search for beatmaps"""
        params = {"q": query}
        if mode:
            params["m"] = mode.value
        data = await self._request("beatmaps/search", params)
        return [Beatmap(**map_data) for map_data in data["beatmaps"]]
