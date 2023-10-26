from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.apiwrapper.models import GameState, Command


def process_tick(context, game_state: GameState) -> Command:
    pass


if __name__ == '__main__':
    pass
