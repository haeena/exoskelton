import json
import shlex
import sys
from pprint import pprint

from flask import Flask, Response, make_response, request
from slack import WebClient as SlackClient
from slackeventsapi import SlackEventAdapter

from exoskelton.plugin_loader import PluginLoader
from exoskelton.slack_argparser import SlackArgumentParserException


class SlackDummyClient:
    post_methods = ["chat_postMessage", "chat_postEphemeral"]

    def __init__(self, *args, **kwarg):  # type: ignore
        self.slack_client = SlackClient(*args, **kwarg)

    def __getattr__(self, key):  # type: ignore
        if key in SlackDummyClient.post_methods:

            def dummy_function(*args, **kwarg):  # type: ignore
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


def depretty_quotes(text: str) -> str:
    return (
        text.replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2018", "'")
        .replace("\u2019", "'")
    )


def handle_message(text: str) -> None:
    channel = "dummy_channel"
    user = "U00SV0WTH"
    ts = "1549692377.007700"

    if text.startswith("exoskelton"):
        text = depretty_quotes(text)
        command_str = shlex.split(text)[1:]
        try:
            args = parser.parse_args(command_str)
            args.channel = channel
            args.user = user
            args.ts = ts
            args.handler(**vars(args))
        except SlackArgumentParserException as e:
            slack_dummy_client.chat_postEphemeral(
                user=user, channel=channel, text=e.message
            )
        except Exception:
            err = sys.exc_info()
            print(err)


if __name__ == "__main__":
    while True:
        text = input("> ")
        handle_message(text)
