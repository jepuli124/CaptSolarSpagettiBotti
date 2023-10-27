import json
from unittest.mock import Mock, patch

import pytest

from apiwrapper.websocket_wrapper import Client, handle_auth_ack, ClientState, handle_game_start, ClientContext, \
    handle_game_tick


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

    def should_call_team_ai_process_tick_on_game_tick_and_return_created_action(self):
        client = Client(ClientState.InGame)
        with patch("src.team_ai.process_tick") as mock_tick_handler:
            pass

    @pytest.mark.parametrize("state", [ClientState.Unauthorized, ClientState.Idle, ClientState.Unconnected])
    def should_raise_exception_on_game_tick_if_state_is_not_in_game(self, state: ClientState):
        client = Client(state)

        with pytest.raises(AssertionError) as actual_exception:
            handle_game_tick(client, Mock(), Mock())

        assert str(actual_exception.value) == (f"Game ticks can only be handled while in in-game state! State right "
                                               f"now is: {state}")
