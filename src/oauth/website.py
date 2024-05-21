from fastapi import APIRouter, Request, Header
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import uvicorn

from . import oauth


# ██╗░░██╗░█████╗░██╗░░░░░░█████╗░  ░██╗░░░░░░░██╗░█████╗░░██████╗  ██╗░░██╗███████╗██████╗░███████╗
# ╚██╗██╔╝██╔══██╗██║░░░░░██╔══██╗  ░██║░░██╗░░██║██╔══██╗██╔════╝  ██║░░██║██╔════╝██╔══██╗██╔════╝
# ░╚███╔╝░██║░░██║██║░░░░░██║░░██║  ░╚██╗████╗██╔╝███████║╚█████╗░  ███████║█████╗░░██████╔╝█████╗░░
# ░██╔██╗░██║░░██║██║░░░░░██║░░██║  ░░████╔═████║░██╔══██║░╚═══██╗  ██╔══██║██╔══╝░░██╔══██╗██╔══╝░░
# ██╔╝╚██╗╚█████╔╝███████╗╚█████╔╝  ░░╚██╔╝░╚██╔╝░██║░░██║██████╔╝  ██║░░██║███████╗██║░░██║███████╗
# ╚═╝░░╚═╝░╚════╝░╚══════╝░╚════╝░  ░░░╚═╝░░░╚═╝░░╚═╝░░╚═╝╚═════╝░  ╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝╚══════╝


class AsyncFastAPIApp(oauth.auth):
    def __init__(self, Main):
        self.Main = Main
        super().__init__()
        self.router = APIRouter()
        self.setup_routes()
        self.request_timestamps = {}

    def setup_routes(self):
        async def async_endpoint(request: Request, code: str):
            if not self.check_rate_limit(request.client.host):
                return JSONResponse(status_code=429, content={"message": "Beep Boop you failled to do your shit :()"})
            return await self.discord_user_callback(code)

        self.router.add_api_route(f"{self.Main.bot_info['oauth']['auth_uri']}", async_endpoint, methods=["GET"])

    def check_rate_limit(self, client_host: str) -> bool:
        max_requests = 5
        time_window = timedelta(minutes=1)
        current_time = datetime.now()

        if client_host in self.request_timestamps:
            self.request_timestamps[client_host] = [t for t in self.request_timestamps[client_host] if current_time - t < time_window]
        else:
            self.request_timestamps[client_host] = []

        self.request_timestamps[client_host].append(current_time)

        return len(self.request_timestamps[client_host]) <= max_requests
    async def run(self):
        config = uvicorn.Config(app=self.router, host="0.0.0.0", port=8000, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
