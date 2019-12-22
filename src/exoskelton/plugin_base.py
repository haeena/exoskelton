import abc
import re
import unicodedata
from typing import Any, Callable, Dict, List, Optional, Sequence, Union

from mypy_extensions import Arg, KwArg
from slack import WebClient as SlackClient

from exoskelton.slack_argparser import SlackArgumentParser
from exoskelton.slack_event_context import SlackEventContextMessage


class PluginBase(metaclass=abc.ABCMeta):
    re_link = re.compile(r"\<([^<>|]+)\|([^<>|]+)\>")
    re_user_id = re.compile(r"\<@([^<>|]+)\>")
    re_channel_id = re.compile(r"\<#([^<>|]+)\|?([^<>|]*)\>")

    def __init__(self, keyword: str) -> None:
        self.keyword = keyword

    def add_slack_client(self, slack_client: SlackClient) -> None:
        self.slack_client = slack_client

        team_info = self.slack_client.team_info()
        if team_info["ok"]:
            self.slack_team_domain = team_info.data["team"]["domain"]
            self.slack_team_info = team_info
        else:
            raise Exception("Failed to call get team_info API")

    @abc.abstractmethod
    def add_parser(self, subparsers: Any) -> None:
        """
        example:
            command_parser = subparsers.add_parser('command', help="command for this plugin")
            command_parser.set_defaults(handler=self.help_factory(command_parser))
            command_subparsers = command_parser.add_subparsers(dest='sub_command')

            command_A_parser = command_subparsers.add_parsers('sub_command_A', help="help for command_A")
            command_A_parser.add_argument('option 1 for command_A')
            command_A_parser.add_argument('option 2 for command_A')

            command_B_parser = command_subparsers.add_parsers('sub_command_B', help="help for command_B")
            command_B_parser.add_argument('option 1 for command_B')
            command_B_parser.add_argument('option 2 for command_B')
            ...
        """
        pass

    def help_factory(
        self, parser: SlackArgumentParser, **kwarg: Any
    ) -> Callable[[Arg(SlackEventContextMessage, "context"), KwArg(Any)], None]:
        def help_func(context: SlackEventContextMessage, **kwarg: Any) -> None:
            text = ""
            if "message" in kwarg:
                text += kwarg["message"]
                text += "\n"
            text += parser.format_help()
            context.reply_ephemeral(text=text)

        return help_func

    def parse_link_in_slack_text(
        self, link_text: str
    ) -> Sequence[Optional[str]]:
        result = self.re_link.search(link_text)
        if not result:
            return None, None
        return result.groups()[0:2]

    def parse_user_id_in_slack_text(self, link_text: str) -> Optional[str]:
        result = self.re_user_id.search(link_text)
        if not result:
            return None
        return result.groups()[0]

    def parse_channel_id_in_slack_text(self, link_text: str) -> Optional[str]:
        result = self.re_channel_id.search(link_text)
        if not result:
            return None
        return result.groups()[0]

    def get_east_asian_width_count(self, text: str) -> int:
        count = 0
        for c in text:
            if unicodedata.east_asian_width(c) in "FWA":
                count += 2
            else:
                count += 1
        return count

    def text_display_len(self, text: str) -> int:
        text = self.re_link.sub(r"\g<2>", text)
        text = self.re_user_id.sub(r"@\g<1>", text)
        text = self.re_channel_id.sub(r"#\g<2>", text)
        return self.get_east_asian_width_count(text)

    def text_padded(self, text: str, width: int) -> str:
        display_len = self.text_display_len(text)

        padding = 0
        if display_len < width:
            padding = width - display_len

        return text + " " * padding

    def format_table(
        self,
        items: List[Union[Dict[str, str], List[str]]],
        header: Optional[List[str]] = None,
        first_item_is_header: bool = False,  # for items: List[str]
    ) -> List[str]:

        rows: List[List[str]]
        if isinstance(items[0], dict):
            header = (
                items[0].keys() if header is None else header  # type: ignore
            )
            rows = [
                [item[key] for key in header] for item in items  # type: ignore
            ]

        elif isinstance(items, list):
            if header is None and first_item_is_header:
                header = items.pop(0)  # type: ignore
            rows = items  # type: ignore

        else:
            raise ValueError("invalid type for items")

        if header is None:
            widths = [
                max(map(self.text_display_len, column)) for column in zip(*rows)
            ]
        else:
            widths = [
                max(map(self.text_display_len, column))
                for column in zip(*([header] + rows))
            ]

        # TODO: separate lines by max post length
        lines = []
        if header is not None:
            header_line = " | ".join(
                [
                    f"{self.text_padded(column, widths[column_index])}"
                    for column_index, column in enumerate(header)
                ]
            )
            lines.append(header_line)
            lines.append("-" * len(header_line))

        for row in rows:
            row_line = " | ".join(
                [
                    f"{self.text_padded(column, widths[column_index])}"
                    for column_index, column in enumerate(row)
                ]
            )
            lines.append(row_line)

        text = "\n".join(lines)

        return ["```\n" + text + "\n```"]
