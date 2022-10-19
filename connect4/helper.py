import json

from fastapi import Response
from slack_sdk.errors import SlackApiError

from connect4.config import logger


def build_response(msg, code, headers=None):
    if not headers:
        headers = {'Content-Type': 'application/json'}
    return Response(content=json.dumps(msg), status_code=code, headers=headers)


def empty_response(code, headers=None):
    if not headers:
        headers = {'Content-Type': 'application/json'}
    return Response(status_code=code, headers=headers)


def build_board_matrix(board_dimensions: tuple[int, int] = None):
    if not board_dimensions:
        board_dimensions = (6, 7)
    return [[0] * board_dimensions[0]] * board_dimensions[1]


def build_new_game_message(player1_id: str, player2_id: str, board_dimensions: tuple[int, int]):
    rows, cols = board_dimensions
    metadata: dict = {
        "event_type": "game_started",
        "event_payload": {
            player1_id: 1,
            player2_id: -1,
            "next_player": player1_id,
            "board_dimensions": board_dimensions,
            "game_board": build_board_matrix(board_dimensions),
            "game_status": "ongoing",
        }
    }

    blocks: list[dict] = [
        {
            "block_id": "divider1",
            "type": "divider"
        },
        {
            "block_id": "header",
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "| \t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t *CONNECT 4* \t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t |",
                # "emoji": True
            }
        },
        {
            "block_id": "divider2",
            "type": "divider",
        },
        {
            "block_id": "_",
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*<@{player1_id}> vs <@{player2_id}>*"
            },
        },
        {
            "block_id": "game_status",
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Next Turn - *<@{player1_id}>*"
            },
        },
        # {
        #     "block_id": "divider3",
        #     "type": "divider",
        # },
        {
            "block_id": "game_columns",
            "type": "actions",
            "elements": [{"value": str(col), "action_id": str(col), "type": "button",
                          "text": {"type": "plain_text", "text": ":small_red_triangle_down:", "emoji": True}
                          } for col in range(cols)]
        },
        {
            "block_id": "divider3",
            "type": "divider"
        }
    ]

    board_blocks: list[dict] = [
        {"block_id": str(i), "type": "context",
         "elements": [
             {"type": "mrkdwn", "text": "*\t   :o:*"} if col == 0 else {"type": "mrkdwn", "text": "*\t\t  :o:*"} for col
             in range(cols)], } for i in range(rows)
    ]
    blocks.extend(board_blocks)
    blocks.append({"block_id": "divider4", "type": "divider"})
    return metadata, blocks


def modify_game_board_message(blocks, block_indexer, row, col, player, board_dimensions):
    player_emoji = {1: ":large_blue_circle:", -1: ":large_yellow_circle:"}
    new_text: str = blocks[block_indexer.get(str(board_dimensions[0] - 1 - row))].get('elements')[col].get('text')
    new_text = new_text.replace(':o:', player_emoji.get(player))
    blocks[block_indexer.get(str(board_dimensions[0] - 1 - row))].get('elements')[col].update({'text': new_text})
    return blocks


def modify_game_board_win_positions(blocks, block_indexer, win_positions, player, board_dimensions):
    player_emoji = {1: ":large_blue_circle:", -1: ":large_yellow_circle:"}
    player_win_emoji = {1: ":blue_heart:", -1: ":yellow_heart:"}
    for col, row in win_positions:
        new_text: str = blocks[block_indexer.get(str(board_dimensions[0] - 1 - row))].get('elements')[col].get('text')
        print(new_text)
        new_text = new_text.replace(player_emoji.get(player), player_win_emoji.get(player))
        blocks[block_indexer.get(str(board_dimensions[0] - 1 - row))].get('elements')[col].update({'text': new_text})
    return blocks


def get_play_again_button_block():
    return {
        "type": "actions",
        "block_id": "play_again",
        "elements": [
            {
                "type": "button",
                "style": "primary",
                "text": {
                    "type": "plain_text",
                    "text": "Play Again"
                },
                "value": "play_again",
                "action_id": "play_again"
            }
        ]
    }


def open_modal(path, trigger_id, slack_client):
    with open(path) as json_file:
        view = json.load(json_file)
        try:
            slack_client.views_open(trigger_id=trigger_id, view=view)
        except SlackApiError as e:
            logger.error(f"An error occurred while opening slack modal: {e}")
    return empty_response(200)
