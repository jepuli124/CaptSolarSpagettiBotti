import json
from time import sleep
from unittest.mock import Mock, patch

import pytest

import team_ai
import apiwrapper.serialization
from apiwrapper.models import GameState, Cell, CellType, Command, MoveActionData
from apiwrapper.websocket_wrapper import Client, handle_auth_ack, ClientState, handle_game_start, ClientContext, \
    handle_game_tick, handle_game_end


# noinspection PyMethodMayBeStatic
class WebsocketFeatures:

    def should_set_client_state_to_idle_if_unauthorized_on_auth_ack(self):
        client = Client(ClientState.Unauthorized)

        handle_auth_ack(client, Mock(), Mock())

        assert client.state == ClientState.Idle

    @pytest.mark.parametrize("state", [ClientState.Idle, ClientState.InGame, ClientState.Unconnected])
    def should_do_nothing_on_auth_ack_if_state_is_not_unauthorized(self, state: ClientState):
        client = Client(state)

        handle_auth_ack(client, Mock(), Mock())

        assert client.state == state

    def should_set_state_to_in_game_on_game_start(self):
        client = Client(ClientState.Idle)
        handle_game_start(client, Mock(), Mock())

        assert client.state == ClientState.InGame

    def should_reset_context_on_game_start(self):
        context = ClientContext()
        client = Client(ClientState.Idle, context)

        handle_game_start(client, Mock(), Mock())

        assert client.context is not context

    def should_send_ack_to_websocket_on_game_start(self):
        client = Client(ClientState.Idle)
        websocket = Mock()

        handle_game_start(client, Mock(), websocket)

        websocket.send.assert_called_with(json.dumps({"eventType": "startAck", "data": {}}))

    @pytest.mark.parametrize("state", [ClientState.Unauthorized, ClientState.InGame, ClientState.Unconnected])
    def should_raise_exception_on_game_start_if_state_is_not_idle(self, state: ClientState):
        client = Client(state)

        with pytest.raises(AssertionError) as actual_exception:
            handle_game_start(client, Mock(), Mock())

        assert str(actual_exception.value) == f"Game can only be started in idle state! State right now is: {state}"

    @patch("apiwrapper.websocket_wrapper.serialize_command")
    @patch("apiwrapper.websocket_wrapper.deserialize_game_state")
    @patch("apiwrapper.websocket_wrapper.process_tick")
    def should_call_team_ai_process_tick_on_game_tick_and_return_created_action(self, mock_tick_handler,
                                                                                mock_state_deserialization,
                                                                                mock_command_serialization):
        client = Client(ClientState.InGame)
        websocket = Mock()
        move_command_dict = {
            "actionType": "move",
            "payload": {"distance": 3}
        }
        mock_state = GameState(1, [[Cell(CellType.Empty, {})]])
        mock_state_deserialization.return_value = mock_state
        mock_tick_handler.return_value = Command("move", MoveActionData(3))
        mock_command_serialization.return_value = move_command_dict
        handle_game_tick(client, Mock(), websocket)
        websocket.send.assert_called_with(json.dumps({"eventType": "gameAction", "data": move_command_dict}))

    @patch("apiwrapper.websocket_wrapper.serialize_command")
    @patch("apiwrapper.websocket_wrapper.deserialize_game_state")
    @patch("apiwrapper.websocket_wrapper.process_tick")
    def should_give_move_zero_distance_command_if_process_tick_function_does_not_return(self, mock_tick_handler,
                                                                                        mock_state_deserialization,
                                                                                        mock_command_serialization):
        client = Client(ClientState.InGame)
        websocket = Mock()
        move_command_dict = {
            "actionType": "move",
            "payload": {"distance": 0}
        }
        mock_state = GameState(1, [[Cell(CellType.Empty, {})]])
        mock_state_deserialization.return_value = mock_state
        mock_tick_handler.return_value = None
        mock_command_serialization.return_value = move_command_dict
        handle_game_tick(client, Mock(), websocket)
        mock_command_serialization.assert_called_with(Command("move", MoveActionData(0)))

    @patch("apiwrapper.websocket_wrapper.serialize_command")
    @patch("apiwrapper.websocket_wrapper.deserialize_game_state")
    @patch("apiwrapper.websocket_wrapper.process_tick")
    def should_timeout_game_tick_processing_after_config_timeout(self, mock_tick_handler, mock_state_deserialization,
                                                                 mock_command_serialization, monkeypatch):
        def delayed_processing(*_):
            sleep(0.2)
            return Command("move", MoveActionData(3))

        monkeypatch.setenv("tick_ms", "100")
        client = Client(ClientState.InGame)
        websocket = Mock()
        move_command_dict = {
            "actionType": "move",
            "payload": {"distance": 3}
        }
        mock_state = GameState(1, [[Cell(CellType.Empty, {})]])
        mock_state_deserialization.return_value = mock_state
        mock_tick_handler.side_effect = delayed_processing
        mock_command_serialization.return_value = move_command_dict
        handle_game_tick(client, Mock(), websocket)
        mock_command_serialization.assert_called_with(Command("move", MoveActionData(0)))

    @pytest.mark.parametrize("state", [ClientState.Unauthorized, ClientState.Idle, ClientState.Unconnected])
    def should_raise_exception_on_game_tick_if_state_is_not_in_game(self, state: ClientState):
        client = Client(state)

        with pytest.raises(AssertionError) as actual_exception:
            handle_game_tick(client, Mock(), Mock())

        assert str(actual_exception.value) == (f"Game ticks can only be handled while in in-game state! State right "
                                               f"now is: {state}")

    def should_set_state_to_in_game_on_game_end(self):
        client = Client(ClientState.InGame)
        handle_game_end(client, Mock(), Mock())

        assert client.state == ClientState.Idle

    def should_reset_context_on_game_end(self):
        context = ClientContext()
        client = Client(ClientState.InGame, context)

        handle_game_end(client, Mock(), Mock())

        assert client.context is not context

    def should_send_ack_to_websocket_on_game_end(self):
        client = Client(ClientState.InGame)
        websocket = Mock()

        handle_game_end(client, Mock(), websocket)

        websocket.send.assert_called_with(json.dumps({"eventType": "endAck", "data": {}}))

    @pytest.mark.parametrize("state", [ClientState.Unauthorized, ClientState.Idle, ClientState.Unconnected])
    def should_raise_exception_on_game_end_if_state_is_not_idle(self, state: ClientState):
        client = Client(state)

        with pytest.raises(AssertionError) as actual_exception:
            handle_game_end(client, Mock(), Mock())

        assert str(actual_exception.value) == f"Game can only be ended in in game state! State right now is: {state}"
