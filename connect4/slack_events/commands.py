from abc import ABC, abstractmethod

from slack_sdk.web import WebClient
from fastapi import FastAPI, Response

from connect4.helper import empty_response, open_modal
from connect4.messages import help_message


# > This class is an abstract class that defines the interface for all command strategies
class CommandStrategy(ABC):
    @abstractmethod
    def process_command(self, req_data: dict, slack_client: WebClient):
        pass


# It's a class that holds the current state of the command line
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
        return self._command_strategy.process_command(req_data, slack_client)


# This class is a command strategy that is used to handle the help command
class HelpCommandStrategy(CommandStrategy):
    def process_command(self, req_data: dict, slack_client: WebClient):
        return Response(help_message(), 200)


# This class is a command strategy that is used to execute the command to open the game start modal.
class GameStartModalCommandStrategy(CommandStrategy):
    def process_command(self, req_data: dict, slack_client: WebClient):
        open_modal("connect4/views/game_start_modal.json", req_data.get('trigger_id'), slack_client)
        return empty_response(200)


# This class is a command strategy that handles the feedback modal
class FeedbackModalCommandStrategy(CommandStrategy):
    def process_command(self, req_data: dict, slack_client: WebClient):
        open_modal("connect4/views/feedback_request.json", req_data.get('trigger_id'), slack_client)
        return empty_response(200)
