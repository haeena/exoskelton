from typing import Any

from exoskelton.plugin_base import PluginBase
from exoskelton.slack_event_context import SlackEventContextMessage


class Hello(PluginBase):
    def __init__(self, keyword: str = "hello") -> None:
        super().__init__(keyword)

    def add_parser(self, subparsers: Any) -> None:
        command_parser = subparsers.add_parser(
            self.keyword, help=f"{self.keyword} related commands"
        )
        command_parser.set_defaults(handler=self.hello)

    def hello(self, context: SlackEventContextMessage, **kwarg: Any) -> None:
        context.reply(text="hello")
