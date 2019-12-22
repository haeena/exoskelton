import json
import shlex
import sys

from flask import Flask, make_response, request
from slack import WebClient as SlackClient
from slackeventsapi import SlackEventAdapter

from exoskelton.plugin_loader import PluginLoader
from exoskelton.slack_argparser import SlackArgumentParserException


with open("slack_credential.json") as f:
    slack_tokens = json.load(f)

slack_bot_token = slack_tokens["slack_bot_token"]
# slack_oauth_access_token = slack_tokens["slack_oauth_access_token"]
slack_signing_secret = slack_tokens["slack_signing_secret"]

slack_bot_client = SlackClient(slack_bot_token)

pl = PluginLoader(slack_bot_client, "exoskelton")
parser = pl.create_parser()

app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(
    slack_signing_secret, "/exoskelton/events", app
)


def depretty_quotes(text):  # type: ignore
    return (
        text.replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2018", "'")
        .replace("\u2019", "'")
    )


@app.route("/exoskelton/interactive", methods=["POST"])
def handle_interactive_post():  # type: ignore
    request_body = json.loads(request.form["payload"])

    if request_body["token"] != slack_signing_secret:
        return make_response("", 400)

    # callback_id = request_body["callback_id"]
    return make_response("", 200)


@slack_events_adapter.on("message")
def handle_message(event_data):  # type: ignore
    message = event_data["event"]
    text = message.get("text")
    channel = message["channel"]
    ts = message["ts"]

    # ignore bot messages
    if not message.get("subtype") is None:
        return
    user = message["user"]

    if "X-Slack-Retry-Num" in request.headers:
        return

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
            slack_bot_client.chat_postEphemeral(
                user=user, channel=channel, text=e
            )
        except Exception:
            err = sys.exc_info()
            print(err)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
