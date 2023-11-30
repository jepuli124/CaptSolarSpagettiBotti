from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apiwrapper.websocket_wrapper import ClientContext
from apiwrapper.models import ActionType, GameState, Command, MoveActionData, ShootActionData, TurnActionData
from helpers import *

import random


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
        tick. Returning None tells server to move 0 steps forward.

    Note:
        You can get tick time in milliseconds from `context.tick_length_ms` and ship turn rate in 1/8th circles from
        `context.turn_rate`.

        If your function takes longer than the max tick length the function is cancelled and None is returned.
    """



    ai_logger.info("processing tick")

    y = -1
    ourShip = [-1,-1]
    heat = -1
    target = [-1,-1]
    targetAudio = [-1,-1]
    direction = None
    for slideOfMap in game_state.game_map:
        y += 1
        x = -1
        for cell in slideOfMap:
            x += 1
            if cell.cell_type == CellType.Ship:
                if cell.data.id == 'ship:SpagettiHolvi1211:main':
                    heat = cell.data.heat
                    ourShip[0] = cell.data.position.x
                    ourShip[1] = cell.data.position.y
                    direction = cell.data.direction
                else:
                    target[0] = cell.data.position.x
                    target[1] = cell.data.position.y
            if cell.cell_type == CellType.AudioSignature:
                targetAudio[0] = x
                targetAudio[1] = y
            if cell.cell_type != CellType.OutOfVision and cell.cell_type != CellType.Empty:
                print(cell, x, y)
    print(ourShip)
    print(target, targetAudio)
    print(direction)
    wantedDirection = None
    if target[0] != -1:
        x = ourShip[0]-target[0]
        y = ourShip[1]-target[1]
        if x > 0 and y > 0:
            wantedDirection = CompassDirection.NorthEast
        if x > 0 and y == 0:
            wantedDirection = CompassDirection.East
        if x > 0 and y < 0:
            wantedDirection = CompassDirection.SouthEast
        if x == 0 and y < 0:
            wantedDirection = CompassDirection.South
        if x < 0 and y < 0:
            wantedDirection = CompassDirection.SouthWest
        if x < 0 and y == 0:
            wantedDirection = CompassDirection.West
        if x < 0 and y > 0:
            wantedDirection = CompassDirection.NorthWest
        if x == 0 and y > 0:
            wantedDirection = CompassDirection.North
    else:
        x = ourShip[0]-targetAudio[0]
        y = ourShip[1]-targetAudio[1]
        if x > 0 and y > 0:
            wantedDirection = CompassDirection.NorthEast
        if x > 0 and y == 0:
            wantedDirection = CompassDirection.East
        if x > 0 and y < 0:
            wantedDirection = CompassDirection.SouthEast
        if x == 0 and y < 0:
            wantedDirection = CompassDirection.South
        if x < 0 and y < 0:
            wantedDirection = CompassDirection.SouthWest
        if x < 0 and y == 0:
            wantedDirection = CompassDirection.West
        if x < 0 and y > 0:
            wantedDirection = CompassDirection.NorthWest
        if x == 0 and y > 0:
            wantedDirection = CompassDirection.North

    # please add your code here
    heatGenerated = 4
    playerId = "ship:spagettiraketti:main"
    playerCoordinates = get_entity_coordinates(playerId, game_state.game_map)
    if 25-game_state.game_map[playerCoordinates.y][playerCoordinates.x].data.heat < heatGenerated:
        return Command(action=ActionType.Move, payload=MoveActionData(1))
    elif direction == wantedDirection:#oikee suunta
        return Command(action=ActionType.Shoot, payload=ShootActionData(4,1))
    else:
        return Command(action=ActionType.Turn, payload=TurnActionData(get_partial_turn(wantedDirection)))
    return None
