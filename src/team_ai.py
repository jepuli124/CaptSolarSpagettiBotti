from apiwrapper.websocket_wrapper import ClientContext
from src.apiwrapper.models import GameState, Command


def process_tick(context: ClientContext, game_state: GameState) -> Command:
    pass
