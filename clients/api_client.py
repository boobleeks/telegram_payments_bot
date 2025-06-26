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

    def _generate_signature(self, dt: str = None, user_id: str = None, method: str = None, amount: float = None, language: str = "ru", code: str = None) -> str:
        """Генерирует подпись для запроса"""
        if method == "find_player":
            # Для метода find_player
            step1_str = f"hash={self.hash_key}&userid={user_id}&cashdeskid={self.cashdeskid}"
            step2_str = f"userid={user_id}&cashierpass={self.cashierpass}&hash={self.hash_key}"
            step1_hash = hashlib.sha256(step1_str.encode()).hexdigest()
            step2_hash = hashlib.md5(step2_str.encode()).hexdigest()
            return hashlib.sha256((step1_hash + step2_hash).encode()).hexdigest()
        
        elif method == "get_balance":
            # Для метода get_balance
            step1_str = f"hash={self.hash_key}&cashierpass={self.cashierpass}&dt={dt}"
            step2_str = f"dt={dt}&cashierpass={self.cashierpass}&cashdeskid={self.cashdeskid}"
            step1_hash = hashlib.sha256(step1_str.encode()).hexdigest()
            step2_hash = hashlib.md5(step2_str.encode()).hexdigest()
            return hashlib.sha256((step1_hash + step2_hash).encode()).hexdigest()
        
        elif method == "deposit":
            step1_str = f"hash={self.hash_key}&lng={language}&userid={user_id}"
            step1 = hashlib.sha256(step1_str.encode()).hexdigest()
            step2_str = f"summa={amount}&cashierpass={self.cashierpass}&cashdeskid={self.cashdeskid}"
            step2 = hashlib.md5(step2_str.encode()).hexdigest()

            signature = hashlib.sha256((step1+step2).encode()).hexdigest()

            return signature
        
        elif method == "withdraw":
            step1_str = f"hash={self.hash_key}&lng={language}&userid={user_id}"
            step1 = hashlib.sha256(step1_str.encode()).hexdigest()
            step2_str = f"code={code}&cashierpass={self.cashierpass}&cashdeskid={self.cashdeskid}"
            step2 = hashlib.md5(step2_str.encode()).hexdigest()

            signature = hashlib.sha256((step1+step2).encode()).hexdigest()

            return signature


        step1_hash = hashlib.sha256(step1_str.encode()).hexdigest()
        step2_hash = hashlib.md5(step2_str.encode()).hexdigest()
        return hashlib.sha256((step1_hash + step2_hash).encode()).hexdigest()

    async def get_balance(self) -> dict:
        """Получает баланс кассы"""
        method = "get_balance"
        dt = datetime.now(timezone.utc).strftime("%Y.%m.%d %H:%M:%S")
        url = f"{self.base_url}Cashdesk/{self.cashdeskid}/Balance?confirm={self._generate_confirm()}&dt={dt}"
        headers = {"sign": self._generate_signature(dt, method=method)}
        
        async with self.session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            response.raise_for_status()

    async def player_exists(self, user_id: str) -> bool:
        method = "find_player"
        url = f"{self.base_url}Users/{user_id}?confirm={self._generate_confirm(user_id)}&cashdeskId={self.cashdeskid}"
        headers = {"sign": self._generate_signature(user_id=user_id, method=method)}

        try:
            async with self.session.get(url, headers=headers) as response:
                text = await response.text()
                response.raise_for_status()
                data = json.loads(text)

                if str(data['UserId']) == str(user_id):
                    return data
                else:
                    return False

        except aiohttp.ClientResponseError as e:
            if e.status == 404:
                return False
            raise
    

    async def deposit(self, user_id: str, amount: float, language: str = "ru"):
        method = "deposit"
        if not self.session:
            raise RuntimeError("Session not initialized. Use async with.")
            
        payload = {
            "cashdeskId": int(self.cashdeskid),
            "lng": language,
            "summa": amount,
            "confirm": self._generate_confirm(user_id)
        }

        url = f"{self.base_url}Deposit/{user_id}/Add"
        headers = {
            "sign": self._generate_signature(user_id=user_id, amount=amount, method=method)
        }

        async with self.session.post(url, json=payload, headers=headers) as response:
            response.raise_for_status()
            return await response.json()



    async def withdraw(self, user_id: str, code: str, language: str = "ru"):
        method = "withdraw"
        if not self.session:
            raise RuntimeError("Session not initialized. Use async with.")
            
        payload = {
            "cashdeskId": self.cashdeskid,
            "lng": language,
            "code": code,
            "confirm": self._generate_confirm(user_id)
        }

        url = f"{self.base_url}Deposit/{user_id}/Payout"
        headers = {
            "sign": self._generate_signature(user_id=user_id, code=code, method=method)
        }

        async with self.session.post(url, json=payload, headers=headers) as response:
            response.raise_for_status()
            return await response.json()


# async def main():
#     async with AsyncCashdeskBotClient() as client:
#         try:
#             exists = await client.player_exists(1259446209)
#             print(f"Игрок существует: {exists}")
            
#             balance = await client.get_balance()
#             print(f"Баланс кассы: {balance}")

#             # deposit = await client.deposit(user_id='1259446209', amount=30094.00)
#             # print(f"Успешно! {deposit}")

#             # withdraw = await client.withdraw(user_id='1259446209', code="df56")
#             # print(f"Успешно! {withdraw}")

#         except Exception as e:
#             print(f"Ошибка: {e}")

# asyncio.run(main())