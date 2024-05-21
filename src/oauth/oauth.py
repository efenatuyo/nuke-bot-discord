import aiohttp, random, datetime, json, asyncio
from fastapi.responses import JSONResponse


# ██╗░░██╗░█████╗░██╗░░░░░░█████╗░  ░██╗░░░░░░░██╗░█████╗░░██████╗  ██╗░░██╗███████╗██████╗░███████╗
# ╚██╗██╔╝██╔══██╗██║░░░░░██╔══██╗  ░██║░░██╗░░██║██╔══██╗██╔════╝  ██║░░██║██╔════╝██╔══██╗██╔════╝
# ░╚███╔╝░██║░░██║██║░░░░░██║░░██║  ░╚██╗████╗██╔╝███████║╚█████╗░  ███████║█████╗░░██████╔╝█████╗░░
# ░██╔██╗░██║░░██║██║░░░░░██║░░██║  ░░████╔═████║░██╔══██║░╚═══██╗  ██╔══██║██╔══╝░░██╔══██╗██╔══╝░░
# ██╔╝╚██╗╚█████╔╝███████╗╚█████╔╝  ░░╚██╔╝░╚██╔╝░██║░░██║██████╔╝  ██║░░██║███████╗██║░░██║███████╗
# ╚═╝░░╚═╝░╚════╝░╚══════╝░╚════╝░  ░░░╚═╝░░░╚═╝░░╚═╝░░╚═╝╚═════╝░  ╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝╚══════╝

class auth:
    async def discord_user_callback(self, code):
        async with aiohttp.ClientSession() as session:
            try:
                data = {
                    "client_id": self.Main.bot_info["oauth"]["client_id"],
                    "client_secret": self.Main.bot_info["oauth"]["client_secret"],
                    "grant_type": "authorization_code",
                    "code": code,
                    "scope": "identify guilds.join",
                    "redirect_uri": self.Main.bot_info["oauth"]["server_uri"] + self.Main.bot_info["oauth"]["auth_uri"]
                }
                headers = {
                    "Authorization": f'Bot {self.Main.bot_info["oauth"]["token"]}'
                }
                async with session.post("https://discord.com/api/oauth2/token", data=data, headers=headers, proxy=random.choice(self.Main.proxies), ssl=False) as response:
                    if response.status != 200:
                        raise Exception
                    auth_data = await response.json()
                    access_token = auth_data['access_token']
                    refresh_token = auth_data['refresh_token']
                    user = await self.get_discord_id(session, access_token)
                    info = {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "expires_in": str(datetime.timedelta(seconds=int(auth_data['expires_in'])) + datetime.datetime.now())
                    }
                    self.add_user_to_database(str(user), info)
                    await self.give_user_role(session, user)
                    return JSONResponse(status_code=200, content={"success": True})
            except:
                return JSONResponse(status_code=500, content={"success": False})
    
    async def get_discord_id(self, session, access_token):
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        async with session.get("https://discordapp.com/api/users/@me", headers=headers, proxy=random.choice(self.Main.proxies), ssl=False) as response:
            if response.status != 200:
                raise Exception

            return (await response.json())['id']
    
    async def give_user_role(self, session, user):
        return await session.put(f"https://discord.com/api/v9/guilds/{self.Main.guild_id}/members/{user}/roles/{self.Main.bot_info['oauth']['verify_role_id']}", proxy=random.choice(self.Main.proxies), ssl=False)
    
    async def refresh_token(self, session, refresh_token, user):
        data = {
            "client_id": self.Main.bot_info["oauth"]["client_id"],
            "client_secret": self.Main.bot_info["oauth"]["client_secret"],
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        try:
            async with session.post("https://discord.com/api/v9/oauth2/token", data=data, proxy=random.choice(self.Main.proxies), ssl=False) as response:
                if response.status != 200:
                    raise Exception
                auth_data = response.json()
                access_token = auth_data['access_token']
                refresh_token = auth_data['refresh_token']
                info = {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expires_in": str(datetime.timedelta(seconds=int(auth_data['expires_in'])) + datetime.datetime.now())
                }
                self.add_user_to_database(user, info)
                return access_token
        except:
            self.remove_user_from_database(user)
            return False
    
    def add_user_to_database(self, user, info):
        data = json.loads(open("database.json", "r").read())
        data["oauth_users"][user] = info
        open("database.json", "w").write(json.dumps(data, indent=4))
        
    def remove_user_from_database(self, user):
        data = json.loads(open("database.json", "r").read())
        if data["oauth_users"].get(user):
            del data["oauth_users"][user]
            open("database.json", "w").write(json.dumps(data, indent=4))
    
    async def check_access_token(self, session, refresh_token, user):
        if datetime.datetime.strptime(json.loads(open("database.json", "r").read())["oauth_users"][user]['expires_in'], '%Y-%m-%d %H:%M:%S.%f') > datetime.datetime.now():
            return True
        else:
            return await self.refresh_token(session, refresh_token, user)
    
    class add_user:
        async def add_users_to_guild(self):
            async with aiohttp.ClientSession() as session:
                for user, info in json.loads(open("database.json", "r").read())["oauth_users"].items():
                    self.add_user_to_guild(session, user, info)
        
        async def add_user_to_guild(self, session, user, info):
                status = await auth.check_access_token(self, session, info["refresh_token"], user)
                if status and isinstance(status, bool):
                    headers = {
                        "Authorization": f'Bot {self.Main.bot_info["oauth"]["token"]}'
                    }
                    data = {
                        "access_token": info["access_token"]
                    }
                    while True:
                     async with session.put(f"https://discord.com/api/v9/guilds/{self.Main.guild_id}/members/{user}", headers=headers, json=data, proxy=random.choice(self.Main.proxies), ssl=False) as response:
                        if response.status == 201:
                            print(f"Added user {user} to guild")
                            return
                        elif response.status == 204:
                            print(f"User {user} is already in group")
                            return
                        elif response.status == 429:
                            await asyncio.sleep((await response.json()).get("retry_after", 0))
                        else:
                            print(await response.json())
                            return