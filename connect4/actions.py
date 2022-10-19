from abc import ABC, abstractmethod

from slack_sdk.web import WebClient

from commands import CommandContext, GameStartModalCommandStrategy
from config import logger
from connect_four import ConnectFour
from helper import build_response, empty_response, modify_game_board_message, modify_game_board_win_positions, \
    get_play_again_button_block


class ActionStrategy(ABC):
    @abstractmethod
    def process_action(self, req_data: dict, slack_client: WebClient):
        pass


class ActionContext:
    def __init__(self, action_strategy: ActionStrategy) -> None:
        self._action_strategy = action_strategy

    @property
    def action_strategy(self) -> ActionStrategy:
        return self._action_strategy

    @action_strategy.setter
    def action_strategy(self, action_strategy: ActionStrategy) -> None:
        self._action_strategy = action_strategy

    def execute(self, req_data: dict, slack_client: WebClient) -> None:
        self._action_strategy.process_action(req_data, slack_client)


class UsersSelectActionStrategy(ActionStrategy):
    def process_action(self, req_data: dict, slack_client: WebClient):
        user_id = req_data.get('user').get('id')
        action = req_data.get('actions')[0]
        if user_id == action.get('selected_user'):
            return build_response(
                {"response_action": "errors", "errors": {"users_select": "You cannot play a game with yourself"}}, 200)
        else:
            return empty_response(200)


class PlayAgainActionStrategy(ActionStrategy):
    def process_action(self, req_data: dict, slack_client: WebClient):
        channel_id = req_data.get('channel').get('id')
        metadata_payload = req_data.get('message').get('metadata').get('event_payload')
        blocks: list = req_data.get('message').get('blocks')
        block_indexer = dict((block['block_id'], i) for i, block in enumerate(blocks))
        play_again_index = block_indexer.get('play_again', -1)
        blocks.pop(play_again_index)
        resp = slack_client.chat_update(channel=channel_id, ts=req_data.get('message').get('ts'),
                                        text=req_data.get('message').get('text'),
                                        metadata={'event_type': 'game_updated',
                                                  'event_payload': metadata_payload},
                                        blocks=blocks)
        logger.debug(f"Play again button removed - {resp}")
        return CommandContext(GameStartModalCommandStrategy()).execute(req_data, slack_client)


class PlayCurrentGameActionStrategy(ActionStrategy):
    def process_action(self, req_data: dict, slack_client: WebClient):
        logger.info(f"Message - {req_data.get('message')}")
        user_id = req_data.get('user').get('id')
        metadata_payload = req_data.get('message').get('metadata').get('event_payload')
        if user_id == metadata_payload.get('next_player') and metadata_payload.get('game_status') == 'ongoing':
            channel_id = req_data.get('channel').get('id')
            action = req_data.get('actions')[0]
            game_column = int(action.get('value'))
            blocks: list = req_data.get('message').get('blocks')
            block_indexer = dict((block['block_id'], i) for i, block in enumerate(blocks))
            player_value = metadata_payload.get(user_id)
            current_game = ConnectFour(player_value, game_column, metadata_payload.get('game_board'))
            if current_game.check_column_valid():
                changed_board, game_row = current_game.make_move()
                blocks = modify_game_board_message(blocks, block_indexer, game_row, game_column, player_value,
                                                   metadata_payload.get('board_dimensions'))
                for key, val in list(metadata_payload.items())[:2]:
                    if val == player_value * -1:
                        metadata_payload.update({'next_player': key, 'game_board': changed_board})
                        blocks[block_indexer.get('game_status')].get('text').update({'text': f"Next Turn - *<@{key}>*"})
                        break
                if win_positions := current_game.check_win():
                    blocks = modify_game_board_win_positions(blocks, block_indexer, win_positions, player_value,
                                                             metadata_payload.get('board_dimensions'))
                    metadata_payload.update({'game_status': 'completed'})
                    blocks[block_indexer.get('game_status')].get('text').update(
                        {'text': f":partying_face: *<@{user_id}>* won the game :confetti_ball:"})
                    blocks.append(get_play_again_button_block())
                elif current_game.check_game_over():
                    metadata_payload.update({'game_status': 'completed'})
                    blocks[block_indexer.get('game_status')].get('text').update(
                        {'text': f":woman-shrugging::skin-tone-2:   "
                                 f"*Nobody won the game*   :woman-shrugging::skin-tone-2: "})
                    blocks.append(get_play_again_button_block())
                resp = slack_client.chat_update(channel=channel_id, ts=req_data.get('message').get('ts'),
                                                text=req_data.get('message').get('text'),
                                                metadata={'event_type': 'game_updated',
                                                          'event_payload': metadata_payload}, blocks=blocks)
                logger.debug(resp)
        return empty_response(200)
