# _decomplie_PhamAnhTien_

import json
import time
import asyncio
import aiohttp
import websockets
import random
import os
from rich.console import Console
import backoff
from cachetools import TTLCache
import art

console = Console()

# Mau sac in ra terminal
mo, dong = "[bold black][", "[bold black]]"
red, green, black = "[bold red]", "[bold green]", "[bold black]"

# Bien cau hinh
HEARTBEAT_TIMEOUT = 15
RECONNECT_DELAY = 2
cache = TTLCache(maxsize=500, ttl=600)
statuses = ["invisible", "idle", "online", "dnd"]

# Quan ly session HTTP
class TokenManager:
    def __init__(self):
        self.session = None
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        }

    async def init_session(self):
        self.session = aiohttp.ClientSession(headers=self.headers)

    async def close(self):
        if self.session:
            await self.session.close()

token_manager = TokenManager()

def xoa():
    os.system('cls' if os.name == 'nt' else 'clear')

def banner(text="Trong Nhan"):
    console.print(art.text2art(text), style="green", justify="center")

async def main():
    await token_manager.init_session()
    xoa()
    banner()

    tokenfile = console.input(f"{mo}{green}Nhap File Chua Token{dong} {black}>> ").strip()
    idkenh = console.input(f"{mo}{green}Nhap ID Kenh Voice{dong} {black}>> ").strip()
    self_mute = console.input(f"{mo}{green}Tat Mic? (Y/N){dong} {black}>> ").strip().lower() == 'y'
    self_deaf = console.input(f"{mo}{green}Tat Loa? (Y/N){dong} {black}>> ").strip().lower() == 'y'
    enable_stream = console.input(f"{mo}{green}Bat Stream? (Y/N){dong} {black}>> ").strip().lower() == 'y'

    try:
        with open(tokenfile, 'r') as f:
            tokens = [line.strip() for line in f if line.strip()]
    except Exception as e:
        console.print(f"{red}Loi Äoc file token: {e}")
        return

    try:
        await asyncio.gather(*(handle_token(token, idkenh, self_mute, self_deaf, enable_stream) for token in tokens))
    except Exception as e:
        console.print(f"{red}Loi chay main: {e}")
    finally:
        await token_manager.close()

async def handle_token(token, channel_id, self_mute, self_deaf, enable_stream):
    guild_id = await get_guild_id(token, channel_id)
    if not guild_id:
        console.print(f"{red}{token[-5:]} {black}| {red}Khong co trong server")
        return

    attempts = 0
    while attempts < 50:
        try:
            gateway_url = await get_gateway_url(token)
            if not gateway_url:
                attempts += 1
                await asyncio.sleep(RECONNECT_DELAY)
                continue

            async with websockets.connect(
                gateway_url, ping_interval=20,
                ping_timeout=HEARTBEAT_TIMEOUT
            ) as ws:
                await authenticate_websocket(ws, token)
                session_id, user_id, username = await wait_for_ready(ws, token)
                if session_id and user_id:
                    await maintain_voice_connection(ws, guild_id, channel_id, user_id, username, self_mute, self_deaf, enable_stream)
        except websockets.exceptions.ConnectionClosed as e:
            if e.code in (1006, 4004):
                msg = "Mat ket noi" if e.code == 1006 else "Token khong hop le"
                console.print(f"{red}{token[-5:]} {black}| {red}{msg}")
                return
        except Exception as e:
            console.print(f"{red}{token[-5:]} {black}| {red}Loi: {e}")
        await asyncio.sleep(RECONNECT_DELAY)
        attempts += 1

async def authenticate_websocket(ws, token):
    await ws.send(json.dumps({
        "op": 2,
        "d": {
            "token": token,
            "intents": 641,
            "properties": {"$os": "windows", "$browser": "chrome", "$device": "pc"},
            "presence": {"status": random.choice(statuses), "afk": False}
        }
    }))

async def wait_for_ready(ws, token):
    try:
        while True:
            msg = await asyncio.wait_for(ws.recv(), timeout=HEARTBEAT_TIMEOUT)
            data = json.loads(msg)
            if data.get("op") == 10:
                await ws.send(json.dumps({"op": 1, "d": None}))
            if data.get("t") == "READY":
                u = data["d"]["user"]
                console.print(f"{green}{token[-5:]} {black}>> {green}Äa ket noi voi {u['username']}#{u.get('discriminator', '0')}")
                return data["d"]["session_id"], u["id"], u["username"]
            if data.get("op") == 9:
                console.print(f"{red}{token[-5:]} {black}| {red}Invalid session. Äang thu lai...")
                return None, None, None
    except asyncio.TimeoutError:
        console.print(f"{red}{token[-5:]} {black}| {red}Timeout Äoi READY")
        return None, None, None

async def maintain_voice_connection(ws, guild_id, channel_id, user_id, username, self_mute, self_deaf, enable_stream):
    await send_join_voice(ws, guild_id, channel_id, self_mute, self_deaf)
    last_heartbeat = time.time()
    while True:
        if time.time() - last_heartbeat >= 30:
            await ws.send(json.dumps({"op": 1, "d": None}))
            last_heartbeat = time.time()
        try:
            msg = await asyncio.wait_for(ws.recv(), timeout=0.1)
            data = json.loads(msg)
            if data.get("op") == 11:
                continue
            if data.get("t") == "VOICE_STATE_UPDATE" and data["d"].get("user_id") == user_id:
                if data["d"].get("channel_id") == channel_id:
                    console.print(f"{green}{username} {black}>> {green}Äa vao voice channel")
                    if enable_stream:
                        await send_go_live(ws, guild_id, channel_id)
                elif data["d"].get("channel_id") is None:
                    await send_join_voice(ws, guild_id, channel_id, self_mute, self_deaf)
        except asyncio.TimeoutError:
            continue
        except Exception as e:
            console.print(f"{red}{username} {black}| {red}Loi voice: {e}")
            break

async def send_join_voice(ws, guild_id, channel_id, self_mute, self_deaf):
    await ws.send(json.dumps({
        "op": 4,
        "d": {
            "guild_id": guild_id,
            "channel_id": channel_id,
            "self_mute": self_mute,
            "self_deaf": self_deaf
        }
    }))

async def send_go_live(ws, guild_id, channel_id):
    await ws.send(json.dumps({
        "op": 18,
        "d": {
            "type": "guild",
            "guild_id": guild_id,
            "channel_id": channel_id,
            "preferred_region": None
        }
    }))

@backoff.on_exception(backoff.expo, aiohttp.ClientError, max_tries=5)
async def get_gateway_url(token):
    if "gateway_url" in cache:
        return cache["gateway_url"]
    async with token_manager.session.get("https://discord.com/api/v9/gateway", headers={"Authorization": token}) as resp:
        if resp.status == 200:
            data = await resp.json()
            url = data["url"] + "/?v=9&encoding=json"
            cache["gateway_url"] = url
            return url
        return None

@backoff.on_exception(backoff.expo, aiohttp.ClientError, max_tries=5)
async def get_guild_id(token, channel_id):
    if channel_id in cache:
        return cache[channel_id]
    async with token_manager.session.get(f"https://discord.com/api/v9/channels/{channel_id}", headers={"Authorization": token}) as resp:
        if resp.status == 200:
            data = await resp.json()
            guild_id = data.get("guild_id")
            if guild_id:
                cache[channel_id] = guild_id
                return guild_id
        return None

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print(f"{red}Äa dung")