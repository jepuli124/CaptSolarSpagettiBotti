from apiwrapper.helpers import get_config
from apiwrapper.websocket_wrapper import connect_websocket

if __name__ == '__main__':
    websocket_url = get_config("websocket_url")
    websocket_port = int(get_config("websocket_port"))
    connect_websocket(websocket_url, websocket_port)