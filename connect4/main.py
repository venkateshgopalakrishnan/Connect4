import asyncio
import json
import logging

from fastapi import FastAPI, Request
from slack_sdk import WebClient

from connect4.slack_events.commands import CommandContext, HelpCommandStrategy, FeedbackModalCommandStrategy, \
    GameStartModalCommandStrategy
from connect4.config import API_PREFIX, LOG_LEVEL, SLACK_WEB_CLIENT_TOKEN
from connect4.helper import build_response, empty_response
from connect4.slack_events.interactions import InteractionContext, GameStartSubmissionInteractionStrategy, \
    BlockActionsInteractionStrategy

loop = asyncio.get_event_loop()
app = FastAPI()

logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s -%(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')


@app.get("/")
@app.get("/health")
def health():
    """
    It returns a JSON response with a status of "OK" and a 200 status code
    :return: A dictionary with a key of status and a value of OK.
    """
    return build_response({"status": "OK"}, 200)


@app.post(f"{API_PREFIX}/interactions")
async def interactions(req_payload: Request):
    """
    It takes the request payload, extracts the data from it, and then passes it to the appropriate
    strategy
    
    :param req_payload: Request - This is the request payload that Slack sends to your app
    :type req_payload: Request
    :return: The return value is a response object.
    """
    base_url = req_payload.base_url
    logging.debug(f"Base URL - {base_url}")
    req_data = await req_payload.form()
    req_data = json.loads(req_data['payload'])
    # if req_data['token'] != os.getenv(f"SLACK_VERIFICATION_TOKEN"):
    #     return empty_response(401)
    req_data['token'] = "Hidden from Logs"
    logging.debug(f"Interaction payload - {req_data}")
    # models.InteractionPayload(**req_data)
    slack_client = WebClient(SLACK_WEB_CLIENT_TOKEN)
    if req_data.get('type') == 'view_submission':
        view_submission_action = InteractionContext(GameStartSubmissionInteractionStrategy())
        view_submission_action.execute(req_data, slack_client)
    elif req_data.get('type') == 'block_actions':
        block_actions_interaction = InteractionContext(BlockActionsInteractionStrategy())
        block_actions_interaction.execute(req_data, slack_client)
    return empty_response(200)


@app.post(f"{API_PREFIX}/commands")
async def commands(req_payload: Request):
    """
    It receives a request payload, validates the request, and then executes the appropriate command
    strategy
    
    :param req_payload: Request - The request payload sent by Slack
    :type req_payload: Request
    :return: The return value is a dict with the following keys:
    """
    req_data = await req_payload.form()
    req_data = dict(req_data)
    # Check if Verification token received matches with
    # if req_data['token'] != os.getenv(f"SLACK_VERIFICATION_TOKEN"):
    #     return empty_response(401)
    # Hide verification token from logs
    req_data['token'] = "Hidden from Logs"
    logging.debug(f"Command payload - {req_data}")
    # Pydantic Model Validation
    # models.CommandPayload(**req_data)
    slack_client = WebClient(SLACK_WEB_CLIENT_TOKEN)
    if req_data['text'] == "help":
        return CommandContext(HelpCommandStrategy()).execute(req_data, slack_client)
    elif req_data['text'] == "feedback":
        return CommandContext(FeedbackModalCommandStrategy()).execute(req_data, slack_client)
    else:
        return CommandContext(GameStartModalCommandStrategy()).execute(req_data, slack_client)
    return empty_response(200)