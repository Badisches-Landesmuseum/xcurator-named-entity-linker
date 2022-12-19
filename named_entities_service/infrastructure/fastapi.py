import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from infrastructure import kubernetes_endpoint


class FastAPIServer:

    def __init__(self, webserver_config: dict = None):
        self.app = FastAPI()
        self.port = 8080 if webserver_config is None else webserver_config['port']
        self.app.add_middleware(CORSMiddleware,
                                allow_origins='*',
                                allow_credentials=True,
                                allow_methods=["*"],
                                allow_headers=["*"], )
        self.__setup_routes__()

    def get(self) -> FastAPI:
        return self.app

    def startup_event(self, callback):
        self.app.add_event_handler("startup", callback)

    def shutdown_event(self, callback):
        self.app.add_event_handler("shutdown", callback)

    def register_endpoint(self, relative_url: str, app, name: str = None):
        if relative_url.startswith('http'):
            raise ValueError(f"Given url is not relative! Url: {relative_url}")

        if name is None:
            self.app.add_route(relative_url, app)
        else:
            self.app.add_route(relative_url, app, name)

    def __setup_routes__(self):
        self.app.include_router(kubernetes_endpoint.router, prefix='/_status')

    def start(self):
        # 2022.05.04 - Decision was made to archive all -web repositories and deprecate static mini-frontend functionality
        # Frontend - ATTENTION: have to be registered last!
        # import pathlib
        # if 'named_entities_service' in str(pathlib.Path().parent.absolute()):
        #     self.app.mount("/", StaticFiles(directory="static", html=True), name="static")
        # else:
        #     self.app.mount("/", StaticFiles(directory="named_entities_service/static", html=True), name="static")

        uvicorn.run(self.app, host="0.0.0.0", port=self.port, loop='asyncio')
