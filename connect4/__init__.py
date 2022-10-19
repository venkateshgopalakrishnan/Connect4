import asyncio
import json
import logging

from fastapi import FastAPI, Request
from slack_sdk import WebClient

from connect4.commands import CommandContext, HelpCommandStrategy, FeedbackModalCommandStrategy, \
    GameStartModalCommandStrategy
from connect4.config import API_PREFIX, LOG_LEVEL, SLACK_WEB_CLIENT_TOKEN
from connect4.connect_four import ConnectFour
from connect4.helper import build_response, empty_response
from connect4.interactions import InteractionContext, GameStartSubmissionInteractionStrategy, \
    BlockActionsInteractionStrategy
from connect4.messages import admin_message, help_message

loop = asyncio.get_event_loop()
app = FastAPI()

logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s -%(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')


@app.get("/")
@app.get("/health")
def health():
    return build_response({"status": "OK"}, 200)


@app.post(f"{API_PREFIX}/interactions")
async def interactions(req_payload: Request):
    # def interactions(req_data: dict, slack_client):
    base_url = req_payload.base_url
    logging.info(f"Base URL - {base_url}")
    req_data = await req_payload.form()
    req_data = json.loads(req_data['payload'])
    # if req_data['token'] != os.getenv(f"SLACK_VERIFICATION_TOKEN"):
    #     return empty_response(401)
    req_data['token'] = "Hidden from Logs"
    logging.info(f"Interaction payload - {req_data}")
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
    # def commands(req_data: dict, slack_client):
    req_data = await req_payload.form()
    req_data = dict(req_data)
    # Check if Verification token received matches with
    # if req_data['token'] != os.getenv(f"SLACK_VERIFICATION_TOKEN"):
    #     return empty_response(401)
    # Hide verification token from logs
    req_data['token'] = "Hidden from Logs"
    logging.info(f"Command payload - {req_data}")
    # Pydantic Model Validation
    # models.CommandPayload(**req_data)
    slack_client = WebClient(SLACK_WEB_CLIENT_TOKEN)
    if req_data['text'] == "help":
        return CommandContext(HelpCommandStrategy()).execute(req_data, slack_client)
    elif req_data['text'] == "feedback":
        return CommandContext(FeedbackModalCommandStrategy()).execute(req_data, slack_client)
    else:
        return CommandContext(GameStartModalCommandStrategy()).execute(req_data, slack_client)

# if __name__ == "__main__":
#     client = SocketModeClient(app_token=SLACK_APP_TOKEN, web_client=WebClient(token=SLACK_WEB_CLIENT_TOKEN))


#     def process(client: SocketModeClient, req: SocketModeRequest):
#         if req.type == "interactive":
#             print(req.payload)
#             interactions(req.payload, client.web_client)
#             response = SocketModeResponse(envelope_id=req.envelope_id)
#             client.send_socket_mode_response(response)
#         elif req.type == "slash_commands":
#             print(req.payload)
#             commands(req.payload, client.web_client)
#             response = SocketModeResponse(envelope_id=req.envelope_id)
#             client.send_socket_mode_response(response)


#     client.socket_mode_request_listeners.append(process)
#     # Establish a WebSocket connection to the Socket Mode servers
#     client.connect()
#     # Just not to stop this process
#     from threading import Event

#     Event().wait()
