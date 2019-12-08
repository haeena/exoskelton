from exoskelton.plugin_base import PluginBase
from exoskelton.slack_argparser import SlackArgumentParser


class Hello(PluginBase):
    def __init__(self, keyword: str = "hello") -> None:
        super().__init__(keyword)

    def add_parser(self, subparsers: SlackArgumentParser) -> None:
        subparsers.set_defaults(handler=self.hello)

    def hello(self, user: str, channel: str) -> None:
        self.slack_client.chat_postEphemeral(
            user=user, channel=channel, text="hello"
        )
