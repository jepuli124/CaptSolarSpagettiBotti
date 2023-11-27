import json
import multiprocessing
from enum import Enum
from logging import getLogger
from multiprocessing.pool import ThreadPool

from time import time

from websockets.sync.client import connect

from helpers import get_config
from apiwrapper.models import Command, MoveActionData, GameState
from apiwrapper.serialization import deserialize_game_state, serialize_command
from team_ai import process_tick


_TICK_FAILSAFE_TIME_MS = 20


_logger = getLogger("wrapper.websockets")
_team_ai_logger = getLogger("team_ai.timer")


class ClientState(Enum):
    Unconnected = 0,
    Unauthorized = 1,
    Idle = 2,
    InGame = 3


class ClientContext:
    """The persistent context of the current game.

    You can either add data to this class ad-hoc, or if you want or need static type checking you can edit this class
    to include fields for the data you want to store between ticks."""

    def __init__(self, tick_length_ms: int, turn_rate: int):
        self.tick_length_ms = tick_length_ms
        self.turn_rate = turn_rate


class Client:
    def __init__(self, state: ClientState = ClientState.Unconnected, context: ClientContext | None = None):
        self.state: ClientState = state
        self.context: ClientContext | None = context


def _send_websocket_message(websocket, raw_message: dict):
    message = json.dumps(raw_message)
    websocket.send(message)
    _logger.debug(f"Sent: {message}")


def handle_auth_ack(client, *_):
    if client.state == ClientState.Unauthorized:
        client.state = ClientState.Idle
        _logger.info("Authorization successful")


def handle_game_start(client, game_config, websocket):
    assert client.state == ClientState.Idle, (f"Game can only be started in idle state! State right now is: "
                                              f"{client.state}")
    client.context = ClientContext(game_config["tickLength"], game_config["turnRate"])
    client.state = ClientState.InGame
    _send_websocket_message(websocket, {"eventType": "startAck", "data": {}})


def handle_game_tick(client, raw_state, websocket):
    assert client.state == ClientState.InGame, (f"Game ticks can only be handled while in in-game state! State right "
                                                f"now is: {client.state}")
    state = deserialize_game_state(raw_state)
    action = _handle_tick_processing_timeout(client, state)
    # None is returned on timeout, should be converted to empty action -> move 0 steps
    if action is None:
        action = Command("move", MoveActionData(0))
    serialized_action = serialize_command(action)
    _send_websocket_message(websocket, {"eventType": "gameAction", "data": serialized_action})


def _handle_tick_processing_timeout(client: Client, state: GameState) -> Command | None:
    if client.context is None:
        raise ValueError("Context is None, but state is in game!")
    timeout_ms = client.context.tick_length_ms - _TICK_FAILSAFE_TIME_MS
    try:
        with ThreadPool() as pool:
            return pool.apply_async(_process_tick_wrapper, (client.context, state)).get(
                timeout=(timeout_ms / 1000))
    except multiprocessing.TimeoutError:
        # We catch and log instead of propagating so the wrapper layer still knows to send an empty event
        _logger.error(f"Team ai function timed out after {timeout_ms} milliseconds.")
        return None


def _process_tick_wrapper(context: ClientContext, state: GameState) -> Command | None:
    try:
        start_time = time()
        result = process_tick(context, state)
        _team_ai_logger.debug(f"tick processed in {((time() - start_time) * 1000):.2f} milliseconds")
    except Exception as exception:
        if get_config("wrapper_verbose_exceptions") and get_config("wrapper_verbose_exceptions") != "false":
            _logger.exception(f"Exception raised in team ai tick processing code: {exception}")
        else:
            _logger.error(f"Exception raised in team ai tick processing code: {exception}")
        return None
    return result


def handle_game_end(client, _, websocket):
    assert client.state == ClientState.InGame, (f"Game can only be ended in in game state! State right now is: "
                                                f"{client.state}")
    client.context = None
    client.state = ClientState.Idle
    _send_websocket_message(websocket, {"eventType": "endAck", "data": {}})


_EVENT_HANDLERS = {
    "authAck": handle_auth_ack,
    "startGame": handle_game_start,
    "gameTick": handle_game_tick,
    "endGame": handle_game_end
}


def connect_websocket(url: str, token: str, bot_name: str):  # pragma: no cover -- main loop - runs forever
    client = Client(ClientState.Unauthorized)
    full_token = f"{url}?token={token}&botName={bot_name}"
    _logger.debug(f"Connecting to web socket at {full_token}")
    with connect(full_token) as websocket:
        authorize_client(websocket, token, bot_name)
        while True:
            handle_loop(client, websocket)


def authorize_client(websocket, token: str, bot_name: str):
    _logger.info(f"Authorizing client with token '{token}' and name '{bot_name}'.")
    _send_websocket_message(websocket, {"eventType": "auth", "data": {"token": token, "botName": bot_name}})


def handle_loop(client: Client, websocket):
    message = receive_message(websocket)
    handler = _EVENT_HANDLERS.get(message["eventType"], None)
    if handler is not None:
        try_run_handler(client, message, websocket, handler)


def receive_message(websocket) -> dict:
    _logger.debug("Waiting for message...")
    raw_message = websocket.recv()
    _logger.debug(f"Received: {raw_message}")
    message = json.loads(raw_message)
    return message


def try_run_handler(client: Client, message: dict, websocket, handler):
    try:
        handler(client, message["data"], websocket)
    except Exception as exception:
        if get_config("wrapper_verbose_exceptions") and get_config("wrapper_verbose_exceptions") != "false":
            _logger.exception(f"Exception raised during websocket event handling! Exception: '{exception}'")
        else:
            _logger.error(f"Exception raised during websocket event handling! Exception: '{exception}'")
