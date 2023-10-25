from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.apiwrapper.events import GameState, Command


def process_tick(game_state: GameState) -> Command:
    pass
