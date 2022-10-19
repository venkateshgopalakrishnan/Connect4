from abc import ABC, abstractmethod

from slack_sdk.web import WebClient

from connect4.helper import build_response, empty_response, open_modal
from connect4.messages import help_message


class CommandStrategy(ABC):
    @abstractmethod
    def process_command(self, req_data: dict, slack_client: WebClient):
        pass


class CommandContext:
    def __init__(self, command_strategy: CommandStrategy) -> None:
        self._command_strategy = command_strategy

    @property
    def command_strategy(self) -> CommandStrategy:
        return self._command_strategy

    @command_strategy.setter
    def command_strategy(self, command_strategy: CommandStrategy) -> None:
        self._command_strategy = command_strategy

    def execute(self, req_data: dict, slack_client: WebClient) -> None:
        self._command_strategy.process_command(req_data, slack_client)


class HelpCommandStrategy(CommandStrategy):
    def process_command(self, req_data: dict, slack_client: WebClient):
        return build_response(help_message(), 200)


class GameStartModalCommandStrategy(CommandStrategy):
    def process_command(self, req_data: dict, slack_client: WebClient):
        open_modal("./views/game_start_modal.json", req_data.get('trigger_id'), slack_client)
        return empty_response(200)


class FeedbackModalCommandStrategy(CommandStrategy):
    def process_command(self, req_data: dict, slack_client: WebClient):
        open_modal("./views/feedback_request.json", req_data.get('trigger_id'), slack_client)
        return empty_response(200)
