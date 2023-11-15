from __future__ import annotations

from logging import getLogger
from time import time, sleep
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apiwrapper.websocket_wrapper import ClientContext
from apiwrapper.models import GameState, Command


ai_logger = getLogger("team_ai")
"""You can use this logger to track the behaviour of your bot. 

This is preferred to calling print("msg") as it offers 
better configuration (see README.md in root)

Examples:
    >>> ai_logger.debug("A message that is not important but helps with understanding the code during problem solving.")
    >>> ai_logger.info("A message that you want to see to know the state of the bot during normal operation.")
    >>> ai_logger.warning("A message that demands attention, but is not yet causing problems.")
    >>> ai_logger.error("A message about the bot reaching an erroneous state")
    >>> ai_logger.exception("A message that is same as error, but can be only called in Except blocks. " +
    >>>                     "Includes exception info in the log")
    >>> ai_logger.critical("A message about a critical exception, usually causing a premature shutdown")
"""


def process_tick(context: ClientContext, game_state: GameState) -> Command | None:
    """Main function defining the behaviour of the AI of the team

    Arguments:
        context (ClientContext): persistent context that can store data and state between ticks. Wiped on game creation
        game_state (GameState): the current state of the game

    Returns:
        Command: `apiwrapper.models.Command` instance containing the type and data of the command to be executed on the
        tick.
    """
    start_time = time()
    ai_logger.info("processing tick")

    # please add your code here

    ai_logger.debug(f"tick processed in {((time() - start_time) * 1000):.2f} milliseconds")
    return None
