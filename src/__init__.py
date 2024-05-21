from typing import Union


# ██╗░░██╗░█████╗░██╗░░░░░░█████╗░  ░██╗░░░░░░░██╗░█████╗░░██████╗  ██╗░░██╗███████╗██████╗░███████╗
# ╚██╗██╔╝██╔══██╗██║░░░░░██╔══██╗  ░██║░░██╗░░██║██╔══██╗██╔════╝  ██║░░██║██╔════╝██╔══██╗██╔════╝
# ░╚███╔╝░██║░░██║██║░░░░░██║░░██║  ░╚██╗████╗██╔╝███████║╚█████╗░  ███████║█████╗░░██████╔╝█████╗░░
# ░██╔██╗░██║░░██║██║░░░░░██║░░██║  ░░████╔═████║░██╔══██║░╚═══██╗  ██╔══██║██╔══╝░░██╔══██╗██╔══╝░░
# ██╔╝╚██╗╚█████╔╝███████╗╚█████╔╝  ░░╚██╔╝░╚██╔╝░██║░░██║██████╔╝  ██║░░██║███████╗██║░░██║███████╗
# ╚═╝░░╚═╝░╚════╝░╚══════╝░╚════╝░  ░░░╚═╝░░░╚═╝░░╚═╝░░╚═╝╚═════╝░  ╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝╚══════╝

class Main:
    def __init__(self, guild_id: int, owner_ids: list[int], bot_info: dict[dict[Union[int, str], str], dict[Union[int, str], str]], tracker_webhook: str, premium: dict[list], nuke_settings: dict[Union[str, int, dict]], top_nuker_channel_id: int, top_nuker_guild_channel_webhook: str, proxies: list[str]):
        self.guild_id = guild_id
        self.owner_ids = owner_ids
        self.bot_info = bot_info
        self.tracker_webhook = tracker_webhook
        self.premium = premium
        self.nuke_settings = nuke_settings
        self.top_nuker_channel_id = top_nuker_channel_id
        self.top_nuker_guild_channel_webhook = top_nuker_guild_channel_webhook
        self.proxies = proxies