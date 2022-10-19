from abc import ABC, abstractmethod

from slack_sdk.web import WebClient

from actions import ActionContext, UsersSelectActionStrategy, PlayAgainActionStrategy, \
    PlayCurrentGameActionStrategy
from config import logger
from helper import build_response, empty_response, build_new_game_message
from messages import feedback_message, user_message


class InteractionStrategy(ABC):
    @abstractmethod
    def process_interaction(self, req_data: dict, slack_client: WebClient):
        pass


class InteractionContext:
    def __init__(self, interaction_strategy: InteractionStrategy) -> None:
        self._interaction_strategy = interaction_strategy

    @property
    def interaction_strategy(self) -> InteractionStrategy:
        return self._interaction_strategy

    @interaction_strategy.setter
    def interaction_strategy(self, interaction_strategy: InteractionStrategy) -> None:
        self._interaction_strategy = interaction_strategy

    def execute(self, req_data: dict, slack_client: WebClient) -> None:
        self._interaction_strategy.process_interaction(req_data, slack_client)


class GameStartSubmissionInteractionStrategy(InteractionStrategy):
    def process_interaction(self, req_data: dict, slack_client: WebClient):
        user_id = req_data.get('user').get('id')
        # team_domain = req_data.get('team').get('domain')
        player_id = req_data.get('view').get('state').get('values').get('player_id').get('users-select-action').get(
            'selected_user')
        # TODO check if you have to remove this
        if user_id == player_id:
            return build_response({
                "response_action": "errors",
                "errors": {
                    "users_select": "You cannot play the game with yourself"
                }
            }, 200)
        metadata, blocks = build_new_game_message(user_id, player_id, (6, 7))
        resp = slack_client.conversations_open(users=[user_id, player_id])
        mpdm_channel_id = resp.get('channel').get('id')
        resp = slack_client.chat_postMessage(channel=mpdm_channel_id, text=f"<@{user_id}> vs <@{player_id}>",
                                             blocks=blocks, metadata=metadata, link_names=True)
        logger.info(resp)
        # admin_message = messages.admin_message(user_id, player_id, team_domain)
        # # TODO
        # resp = slack_client.chat_postMessage(channel='C03EZBE3FR7', text=admin_message['text'],
        #                                      attachments=admin_message['attachments'], link_names=True)
        # logger.debug(f'metrics sent - {resp}')
        return empty_response(200)


class FeedbackSubmissionInteractionStrategy(InteractionStrategy):
    def process_interaction(self, req_data: dict, slack_client: WebClient):
        user_id = req_data['user']['id']
        workspace = req_data['team']['domain']
        user_feedback = req_data['view']['state']['values']['bid-feedback']['aid-feedback']['value']
        user_profile = slack_client.users_profile_get(user=user_id)['profile']
        name, email, designation, avatar = user_profile['real_name'], user_profile['email'], user_profile['title'], \
                                           user_profile['image_24']
        feedback = feedback_message(user_feedback, name, workspace, avatar)
        # TODO - feedback channel
        resp = slack_client.chat_postMessage(channel="", text=feedback['text'], attachments=feedback["attachments"])
        logger.debug(f"Updated Feedback Metrics channel with status code {resp.status_code}")
        resp = slack_client.chat_postMessage(channel=user_id, text=user_message()['text'],
                                             attachments=user_message()["attachments"])
        logger.debug(f"Updated User's channel with status code {resp.status_code}")


class BlockActionsInteractionStrategy(InteractionStrategy):
    def process_interaction(self, req_data: dict, slack_client: WebClient):
        action = req_data.get('actions')[0]
        if action.get('type') == "users_select":
            return ActionContext(UsersSelectActionStrategy()).execute(req_data, slack_client)
        elif action.get('type') == "button":
            if action.get('action_id') == 'play_again':
                ActionContext(PlayAgainActionStrategy()).execute(req_data, slack_client)
            elif action.get('block_id') == 'game_columns':
                ActionContext(PlayCurrentGameActionStrategy()).execute(req_data, slack_client)
