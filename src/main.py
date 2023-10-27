from apiwrapper.helpers import get_config
from apiwrapper.websocket_wrapper import connect_websocket
from logging_setup import setup_logging

if __name__ == '__main__':
    setup_logging()
    websocket_url = get_config("websocket_url")
    websocket_port = int(get_config("websocket_port"))
    token = get_config("token")
    connect_websocket(websocket_url, websocket_port, token)
