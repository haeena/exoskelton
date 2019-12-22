import json
import shlex
import sys
from typing import Any

from flask import Flask, Response, make_response, request
from slack import WebClient as SlackClient
from slackeventsapi import SlackEventAdapter

from exoskelton.plugin_loader import PluginLoader
from exoskelton.slack_argparser import SlackArgumentParserException
from exoskelton.slack_event_context import SlackEventContextFactory


with open("slack_credential.json") as f:
    slack_tokens = json.load(f)

slack_bot_token = slack_tokens["slack_bot_token"]
# slack_oauth_access_token = slack_tokens["slack_oauth_access_token"]
slack_signing_secret = slack_tokens["slack_signing_secret"]

slack_bot_client = SlackClient(slack_bot_token)

pl = PluginLoader(slack_bot_client, "exoskelton")
parser = pl.create_parser()
context_factory = SlackEventContextFactory(slack_bot_client)

app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(
    slack_signing_secret, "/exoskelton/events", app
)


@app.route("/exoskelton/interactive", methods=["POST"])
def handle_interactive_post() -> Response:
    request_body = json.loads(request.form["payload"])

    if request_body["token"] != slack_signing_secret:
        return make_response("", 400)

    # callback_id = request_body["callback_id"]
    return make_response("", 200)


@slack_events_adapter.on("message")
def handle_message(event_data: Any) -> None:

    # ignore bot messages
    if not event_data["event"].get("subtype") is None:
        return

    # ignore retry message
    if "X-Slack-Retry-Num" in request.headers:
        return

    context = context_factory.create(event_data=event_data)
    if context is None:
        # TODO: logging
        print("Failed to parse event_data")
        return

    # TODO: configurable keyword
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
    app.run(host="0.0.0.0", port=3000)
