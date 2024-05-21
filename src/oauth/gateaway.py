
# ██╗░░██╗░█████╗░██╗░░░░░░█████╗░  ░██╗░░░░░░░██╗░█████╗░░██████╗  ██╗░░██╗███████╗██████╗░███████╗
# ╚██╗██╔╝██╔══██╗██║░░░░░██╔══██╗  ░██║░░██╗░░██║██╔══██╗██╔════╝  ██║░░██║██╔════╝██╔══██╗██╔════╝
# ░╚███╔╝░██║░░██║██║░░░░░██║░░██║  ░╚██╗████╗██╔╝███████║╚█████╗░  ███████║█████╗░░██████╔╝█████╗░░
# ░██╔██╗░██║░░██║██║░░░░░██║░░██║  ░░████╔═████║░██╔══██║░╚═══██╗  ██╔══██║██╔══╝░░██╔══██╗██╔══╝░░
# ██╔╝╚██╗╚█████╔╝███████╗╚█████╔╝  ░░╚██╔╝░╚██╔╝░██║░░██║██████╔╝  ██║░░██║███████╗██║░░██║███████╗
# ╚═╝░░╚═╝░╚════╝░╚══════╝░╚════╝░  ░░░╚═╝░░░╚═╝░░╚═╝░░╚═╝╚═════╝░  ╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝╚══════╝

import asyncio
import json
import websockets
import aiohttp

from . import oauth

class DiscordGateway(oauth.auth.add_user):
    def __init__(self, Main):
        self.Main = Main
        super().__init__()
        self.token = Main.bot_info["oauth"]["token"]
        self.gateway_url = 'wss://gateway.discord.gg/?v=10&amp;encoding=json'
        self.session_id = None
        self.heartbeat_interval = None
        self.sequence = None

    async def register_commands(self, guild_id):
        url = f"https://discord.com/api/v10/applications/{self.Main.bot_info['oauth']['client_id']}/guilds/{guild_id}/commands"
        
        headers = {
            "Authorization": f"Bot {self.token}",
            "Content-Type": "application/json"
        }
        json_data = {
            "name": "oauth_pull",
            "description": "Handle OAuth Pull",
            "type": 1
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=json_data) as response:
                if response.status not in [200, 201]:
                    print(f"Failed to register command for {'global' if not guild_id else f'guild {guild_id}'}: {response.status}")
                else:
                    print(f"Command registered successfully for {'global' if not guild_id else f'guild {guild_id}'}")
                    
    async def connect(self):
        while True:
            try:
                async with websockets.connect(self.gateway_url) as ws:
                    await self.identify(ws)
                    await self.listen(ws)
            except websockets.ConnectionClosed:
                print("Connection closed, reconnecting...")
                continue

    async def identify(self, ws):
        payload = {
            "op": 2,
            "d": {
                "token": self.token,
                "intents": 513 | 1 << 15 | 1 << 12,
                "properties": {
                    "$os": "windows",
                    "$browser": "my_library",
                    "$device": "my_library"
                }
            }
        }
        await ws.send(json.dumps(payload))

    async def listen(self, ws):
        while True:
            try:
                message = await ws.recv()
                await self.handle_message(ws, message)
            except websockets.ConnectionClosed:
                print("Connection lost during message reception, attempting to reconnect...")
                break

    async def handle_message(self, ws, message):
        data = json.loads(message)
        if data['op'] == 10:
            self.heartbeat_interval = data['d']['heartbeat_interval'] / 1000
            asyncio.create_task(self.heartbeat(ws))
        
        if data['op'] == 11:
            print("Heartbeat acknowledged")
        
        if data['t'] == 'INTERACTION_CREATE':
            interaction = data['d']
            if interaction['data']['name'] == 'oauth_pull':
                user_id = int(interaction["member"]['user']['id']) if interaction.get("member") else int(interaction['user']['id'])
                if user_id in self.Main.owner_ids:
                    await self.handle_oauth_pull(interaction)
                    
        if data['t'] == 'GUILD_CREATE':
            guild_id = data['d']['id']
            await self.register_commands(guild_id)
            
        if data.get('s'):
            self.sequence = data['s']

    async def heartbeat(self, ws):
        while True:
            await asyncio.sleep(self.heartbeat_interval)
            payload = {
                "op": 1,
                "d": self.sequence
            }
            await ws.send(json.dumps(payload))

    async def handle_oauth_pull(self, interaction):
        response_content = 'Handling OAuth Pull...'
        
        response_payload = {
            "content": response_content,
            "tts": False,
            "flags": 64
        }

        response_url = f'https://discord.com/api/v10/interactions/{interaction["id"]}/{interaction["token"]}/callback'
        headers = {
            "Authorization": f"Bot {self.token}",
            "Content-Type": "application/json"
        }
        callback_payload = {
            "type": 4,
            "data": response_payload
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(response_url, headers=headers, json=callback_payload) as resp:
                if resp.status == 204:
                    await self.add_users_to_guild()
                else:
                    print(f"Failed to send response: {resp.status}")