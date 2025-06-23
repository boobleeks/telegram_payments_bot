import hashlib
import aiohttp
from datetime import datetime, timezone
from dotenv import load_dotenv
import os
import asyncio
import json

load_dotenv()

class AsyncCashdeskBotClient:
    def __init__(self):
        self.hash_key = os.getenv("CASHDESK_HASH_KEY")
        self.cashierpass = os.getenv("CASHIER_PASS")
        self.login = os.getenv("LOGIN")
        self.cashdeskid = os.getenv("CASHDESK_ID")
        self.base_url = "https://partners.servcul.com/CashdeskBotAPI/"
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    def _generate_confirm(self, user_id: str = None) -> str:
        """Генерирует confirm строку для запроса"""
        confirm_str = f"{user_id or self.cashdeskid}:{self.hash_key}"
        return hashlib.md5(confirm_str.encode()).hexdigest()

    def _generate_signature(self, dt: str = None, user_id: str = None) -> str:
        """Генерирует подпись для запроса"""
        if user_id:
            # Для метода find_player
            step1_str = f"hash={self.hash_key}&userid={user_id}&cashdeskid={self.cashdeskid}"
            step2_str = f"userid={user_id}&cashierpass={self.cashierpass}&hash={self.hash_key}"
        else:
            # Для метода get_balance
            step1_str = f"hash={self.hash_key}&cashierpass={self.cashierpass}&dt={dt}"
            step2_str = f"dt={dt}&cashierpass={self.cashierpass}&cashdeskid={self.cashdeskid}"

        step1_hash = hashlib.sha256(step1_str.encode()).hexdigest()
        step2_hash = hashlib.md5(step2_str.encode()).hexdigest()
        return hashlib.sha256((step1_hash + step2_hash).encode()).hexdigest()

    async def get_balance(self) -> dict:
        """Получает баланс кассы"""
        dt = datetime.now(timezone.utc).strftime("%Y.%m.%d %H:%M:%S")
        url = f"{self.base_url}Cashdesk/{self.cashdeskid}/Balance?confirm={self._generate_confirm()}&dt={dt}"
        headers = {"sign": self._generate_signature(dt)}
        
        async with self.session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            response.raise_for_status()

    async def player_exists(self, user_id: str) -> bool:
        url = f"{self.base_url}Users/{user_id}?confirm={self._generate_confirm(user_id)}&cashdeskId={self.cashdeskid}"
        headers = {"sign": self._generate_signature(user_id=user_id)}

        try:
            async with self.session.get(url, headers=headers) as response:
                text = await response.text()
                response.raise_for_status()
                data = json.loads(text)
                if str(data['UserId']) == str(user_id):
                    return True
                else:
                    return False

        except aiohttp.ClientResponseError as e:
            if e.status == 404:
                return False
            raise



# async def main():
#     async with AsyncCashdeskBotClient() as client:
#         try:
#             exists = await client.player_exists(661875169)
#             print(f"Игрок существует: {exists}")
            
#             # balance = await client.get_balance()
#             # print(f"Баланс кассы: {balance}")
#         except Exception as e:
#             print(f"Ошибка: {e}")

# asyncio.run(main())