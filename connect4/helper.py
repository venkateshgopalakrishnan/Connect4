import json

from fastapi import Response
from slack_sdk.errors import SlackApiError

from connect4.config import logger


def build_response(msg, code, headers=None):
    """
    It takes a message, a status code, and a dictionary of headers, and returns a response object
    
    :param msg: The message to be returned to the client
    :param code: The HTTP status code
    :param headers: A dictionary of headers to be sent with the response
    :return: A response object with the content of the message, the status code, and the headers.
    """
    if not headers:
        headers = {'Content-Type': 'application/json'}
    return Response(content=json.dumps(msg), status_code=code, headers=headers)


def empty_response(code, headers=None):
    """
    It returns an empty response with the given status code and headers
    
    :param code: The HTTP status code of the response
    :param headers: This is a dictionary of headers to be sent with the response
    :return: A Response object with the status code and headers.
    """
    if not headers:
        headers = {'Content-Type': 'application/json'}
    return Response(status_code=code, headers=headers)


def build_board_matrix(board_dimensions: tuple[int, int] = None):
    """
    It creates a matrix of zeros with the dimensions of the board
    
    :param board_dimensions: tuple[int, int] = None
    :type board_dimensions: tuple[int, int]
    :return: A list of lists.
    """
    if not board_dimensions:
        board_dimensions = (6, 7)
    return [[0] * board_dimensions[0]] * board_dimensions[1]


def build_new_game_message(player1_id: str, player2_id: str, board_dimensions: tuple[int, int]):
    """
    It takes in the player IDs and the board dimensions, and returns a tuple of metadata and blocks
    
    :param player1_id: str, player2_id: str, board_dimensions: tuple[int, int]
    :type player1_id: str
    :param player2_id: str, board_dimensions: tuple[int, int]
    :type player2_id: str
    :param board_dimensions: tuple[int, int]
    :type board_dimensions: tuple[int, int]
    :return: A tuple of two objects. The first object is a dictionary and the second object is a list of
    dictionaries.
    """
    rows, cols = board_dimensions
    player_emoji = {1: ":large_blue_circle:", -1: ":large_yellow_circle:"}
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
                "text": f"*<@{player1_id}> --> {player_emoji.get(1)} vs <@{player2_id}> --> {player_emoji.get(-1)}*"
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
    """
    It takes in the blocks of the message, the block indexer, the row and column of the move, the
    player, and the dimensions of the board, and returns the blocks of the message with the move updated
    
    :param blocks: the blocks of the message
    :param block_indexer: a dictionary that maps the row number to the index of the block in the blocks
    list
    :param row: the row of the board that you want to modify
    :param col: the column of the board you want to modify
    :param player: 1 or -1
    :param board_dimensions: a tuple of the dimensions of the board (e.g. (6, 7))
    :return: A list of dictionaries.
    """
    player_emoji = {1: ":large_blue_circle:", -1: ":large_yellow_circle:"}
    new_text: str = blocks[block_indexer.get(str(board_dimensions[0] - 1 - row))].get('elements')[col].get('text')
    new_text = new_text.replace(':o:', player_emoji.get(player))
    blocks[block_indexer.get(str(board_dimensions[0] - 1 - row))].get('elements')[col].update({'text': new_text})
    return blocks


def modify_game_board_win_positions(blocks, block_indexer, win_positions, player, board_dimensions):
    """
    It takes in the blocks, block_indexer, win_positions, player, and board_dimensions, and returns the
    blocks with the win positions updated
    
    :param blocks: The blocks of the message that you want to modify
    :param block_indexer: a dictionary that maps the row number to the block index in the blocks list
    :param win_positions: a list of tuples of the winning positions
    :param player: the player who won the game
    :param board_dimensions: a tuple of the dimensions of the board (e.g. (6, 7) for a 6x7 board)
    :return: A list of blocks
    """
    player_emoji = {1: ":large_blue_circle:", -1: ":large_yellow_circle:"}
    player_win_emoji = {1: ":blue_heart:", -1: ":yellow_heart:"}
    for col, row in win_positions:
        new_text: str = blocks[block_indexer.get(str(board_dimensions[0] - 1 - row))].get('elements')[col].get('text')
        print(new_text)
        new_text = new_text.replace(player_emoji.get(player), player_win_emoji.get(player))
        blocks[block_indexer.get(str(board_dimensions[0] - 1 - row))].get('elements')[col].update({'text': new_text})
    return blocks


def get_play_again_button_block() -> dict:
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
    """
    It opens a modal in Slack
    
    :param path: the path to the json file that contains the modal view
    :param trigger_id: The trigger ID is a unique identifier for the modal. It's generated by Slack when
    a user clicks a button or link that opens a modal
    :param slack_client: The slack client object that you created in the previous step
    :return: A dictionary with a status code of 200.
    """
    with open(path) as json_file:
        view = json.load(json_file)
        try:
            slack_client.views_open(trigger_id=trigger_id, view=view)
        except SlackApiError as e:
            logger.error(f"An error occurred while opening slack modal: {e}")
    # return empty_response(200)
