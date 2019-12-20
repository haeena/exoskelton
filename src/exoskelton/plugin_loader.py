import importlib
import inspect
import pkgutil
from typing import Any, Callable, Dict, List

from mypy_extensions import Arg, KwArg
from slack import WebClient as SlackClient

import exoskelton.plugins
from exoskelton.plugin_base import PluginBase
from exoskelton.slack_argparser import SlackArgumentParser


class PluginLoader:

    plugins_to_load: List[str] = ["exoskelton.plugins.hello.hello"]

    def __init__(self, slack_client: SlackClient, prog: str) -> None:
        self.prog = prog
        self.slack_client = slack_client
        self.plugins: Dict[str, PluginBase] = {}
        self.load_plugins()

    def load_plugins(self) -> None:
        plugin_class = {
            module_name + "." + class_name: obj
            for finder, module_name, ispkg in pkgutil.walk_packages(
                exoskelton.plugins.__path__, exoskelton.plugins.__name__ + "."  # type: ignore
            )
            for class_name, obj in inspect.getmembers(
                importlib.import_module(module_name)
            )
            if module_name + "." + class_name in self.plugins_to_load
            and inspect.isclass(obj)
            and issubclass(obj, PluginBase)
        }

        for name, class_ref in plugin_class.items():
            instance = class_ref()
            instance.add_slack_client(self.slack_client)
            self.plugins[name] = instance

    def help_factory(
        self, parser: SlackArgumentParser, **kwarg: Any
    ) -> Callable[[Arg(str, "user"), Arg(str, "channel"), KwArg(Any)], None]:
        def help(user: str, channel: str, **kwarg: Any) -> None:
            text = parser.format_help()
            self.slack_client.chat_postEphemeral(
                user=user, channel=channel, text=text
            )

        return help

    def create_parser(self) -> SlackArgumentParser:
        parser = SlackArgumentParser(prog=self.prog)
        parser.set_defaults(handler=self.help_factory(parser))
        subparsers = parser.add_subparsers(dest="command")
        for _name, instance in self.plugins.items():
            instance.add_parser(subparsers)

        self.parser = parser
        return self.parser