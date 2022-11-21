import time

def feedback_message(user_feedback, name, workspace, avatar):
    return {
        "text": "Received feedback from a user",
        "attachments": [
            {
                "color": "#c6fff8",
                "text": f"{user_feedback}",
                "footer": f"Submitted by {name} on {workspace}",
                'footer_icon': avatar,
                "ts": time.time()
            }
        ]
    }


def help_message():
    return "Available commands for Connect4:\n" \
           "`/connect4 @opponent_name` - Play Connect4 with an opponent\n" \
           "`/connect4 help` - Display commands\n" \
           "`/connect4 feedback` - Give feedback about the bot to the developer\n"


def user_message():
    return {
        "text": "Connect4 Assistance",
        "attachments": [
            {
                "color": "#c6fff8",
                "text": "Your feedback has been submitted, thank you!",
                # 'thumb_url': '',
                "footer": "Check out `/connect4 help` for additional requests I can assist with.",
            }
        ]
    }
