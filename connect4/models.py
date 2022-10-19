from typing import Optional

from pydantic import BaseModel


class CommandPayload(BaseModel):
    """
    Class that returns a validated Command payload dictionary
    :rtype: dict
    """
    text: str
    token: str
    channel_id: str
    channel_name: Optional[str]
    user_id: str
    user_name: Optional[str]
    team_id: str
    team_domain: str
    command: str
    response_url: str
    trigger_id: str


class InteractionPayload(BaseModel):
    """
    Class that returns a validated Interaction payload dictionary
    :rtype: dict
    """
    actions: Optional[list]
    channel: Optional[dict]
    message: Optional[dict]
    response_url: Optional[str]
    response_urls: Optional[list]
    team: dict
    token: str
    trigger_id: str
    type: str
    user: dict
    view: dict

# class EventPayload(BaseModel):
#     event: dict
#     team_id: str
#     token: str
