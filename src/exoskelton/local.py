import json
import shlex
import sys
from pprint import pprint
from typing import Any, Callable

from slack import WebClient as SlackClient

from exoskelton.plugin_loader import PluginLoader
from exoskelton.slack_argparser import SlackArgumentParserException
from exoskelton.slack_event_context import SlackEventContextFactory


class SlackDummyClient:
    mock_method = ["chat_postMessage", "chat_postEphemeral"]

    def __init__(self, *args: Any, **kwarg: Any):
        self.slack_client = SlackClient(*args, **kwarg)

    def __getattr__(self, key: str) -> Callable[..., str]:
        if key in self.mock_method:

            def dummy_function(*args: Any, **kwarg: Any) -> str:
                print(key)
                pprint(args)
                pprint(kwarg)
                return json.loads(
                    """
                    {
                        "ok": true,
                        "channel": "C1H9RESGL",
                        "ts": "1503435956.000247",
                        "message": {
                            "text": "Here's a message for you",
                            "username": "ecto1",
                            "bot_id": "B19LU7CSY",
                            "attachments": [
                                {
                                    "text": "This is an attachment",
                                    "id": 1,
                                    "fallback": "This is an attachment's fallback"
                                }
                            ],
                            "type": "message",
                            "subtype": "bot_message",
                            "ts": "1503435956.000247"
                        }
                    }"""
                )

            return dummy_function
        else:
            return getattr(self.slack_client, key)


with open("slack_credential.json") as f:
    slack_tokens = json.load(f)

slack_bot_token = slack_tokens["slack_bot_token"]
slack_dummy_client = SlackDummyClient(slack_bot_token)

pl = PluginLoader(slack_dummy_client, "exoskelton")
parser = pl.create_parser()
context_factory = SlackEventContextFactory(slack_dummy_client)


def handle_message(text: str) -> None:
    event_data = {
        "token": "one-long-verification-token",
        "team_id": "TXXXXXXXX",
        "api_app_id": "AXXXXXXXXX",
        "event": {
            "type": "message",
            "text": text,
            "channel": "dummy_channel",
            "user": "UXXXXXXX1",
            "ts": "1549692377.007700",
        },
        "type": "event_callback",
        "authed_users": ["UXXXXXXX1"],
        "event_id": "Ev08MFMKH6",
        "event_time": 1234567890,
    }

    context = context_factory.create(event_data=event_data)
    if context is None:
        # TODO: logging
        print("Failed to parse event_data")
        return

    if context.text.startswith(parser.prog):
        command_str = shlex.split(context.text)[1:]
        try:
            args = parser.parse_args(command_str)
            args.context = context
            args.handler(**vars(args))
        except SlackArgumentParserException as e:
            # TODO: logging
            context.reply_ephemeral(str(e))
        except Exception:
            # TODO: logging
            err = sys.exc_info()
            context.reply_ephemeral(f"Failure on executing command: {err}")


if __name__ == "__main__":
    while True:
        text = input("> ")
        handle_message(text)
