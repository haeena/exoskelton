from typing import Any, Dict, List, Optional, Union

from slack import WebClient as SlackClient
from slack.errors import SlackApiError


def depretty_quotes(text: str) -> str:
    return (
        text.replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2018", "'")
        .replace("\u2019", "'")
    )


class SlackEventContextFactory:
    def __init__(self, slack_client: SlackClient):
        self.slack_client = slack_client

    def create(
        self, event_data: Any
    ) -> Union[None, "SlackEventContextMessage"]:
        event_type: str = event_data["event"]["type"]

        if event_type == "message":
            return SlackEventContextMessage(self.slack_client, event_data)
        return None


class SlackEventContextBase:
    def __init__(self, slack_client: SlackClient, event_data: Any):
        self.slack_client = slack_client
        self.team_id: str = event_data["team_id"]
        self.authed_users: List[str] = event_data["authed_users"]


class SlackEventContextMessage(SlackEventContextBase):
    def __init__(self, slack_client: SlackClient, event_data: Any):
        super().__init__(slack_client, event_data)

        event: Dict[str, str] = event_data["event"]
        self.user: str = event["user"]
        self.original_text: str = event["text"]
        self.text: str = depretty_quotes(self.original_text)
        self.channel: str = event["channel"]
        self.ts: str = event["ts"]

        self.last_reply_ts: Optional[str] = None

    def reply(self, text: str) -> Any:
        try:
            result = self.slack_client.chat_postMessage(
                channel=self.channel, text=text
            )
        except SlackApiError as e:
            # TODO: logging
            raise e

        self._handle_post_result(result)

    def reply_ephemeral(self, text: str) -> None:
        try:
            result = self.slack_client.chat_postEphemeral(
                user=self.user, channel=self.channel, text=text
            )
        except SlackApiError as e:
            # TODO: logging
            raise e

        self._handle_post_result(result)

    def update_last_reply(self, text: str) -> None:
        if self.last_reply_ts is None:
            # TODO: stop using bare exception
            raise Exception("Not making reply on this context yet")
        try:
            result = self.slack_client.chat_update(
                channel=self.channel, ts=self.last_reply_ts, text=text
            )
        except SlackApiError as e:
            # TODO: logging
            raise e

        self._handle_post_result(result)

    def reaction(self, name: str) -> None:
        try:
            self.slack_client.reactions_add(
                channel=self.channel, timestamp=self.ts, name=name
            )
        except SlackApiError as e:
            # TODO: logging
            raise e

    def _handle_post_result(self, result: Any) -> None:
        self.last_reply_ts = result["ts"]
