import re
import textwrap as _textwrap
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from typing import Any, List, Optional


class PreserveWhiteSpaceWrapRawTextHelpFormatter(RawDescriptionHelpFormatter):
    """
    PreserveWhiteSpaceWrapRawTextHelpFormatter ensure help string nicely formatted on slack
    """

    def __init__(self, **kwarg: Any):
        super().__init__(width=1000, **kwarg)

    def __add_whitespace(self, idx: int, iWSpace: int, text: str) -> str:
        if idx == 0:
            return text
        return (" " * iWSpace) + text

    def _split_lines(self, text: str, width: int) -> List[str]:
        textRows: List[Any] = text.splitlines()
        for idx, line in enumerate(textRows):
            search = re.search(r"\s*[0-9\-]{0,}\.?\s*", line)
            if line.strip() == "":
                textRows[idx] = " "
            elif search:
                lWSpace = search.end()
                lines = [
                    self.__add_whitespace(i, lWSpace, x)
                    for i, x in enumerate(_textwrap.wrap(line, width))
                ]
                textRows[idx] = lines

        return [item for sublist in textRows for item in sublist]


class SlackArgumentParserException(Exception):
    pass


class SlackArgumentParser(ArgumentParser):
    """
    SlackArgumentParser is modified to keep process working after parse error
    """

    def __init__(self, **kwarg: Any):
        super().__init__(
            formatter_class=PreserveWhiteSpaceWrapRawTextHelpFormatter, **kwarg
        )

    def _print_message(self, message: str, file: Optional[Any] = None) -> None:
        if message:
            raise SlackArgumentParserException(message)

    def exit(  # type: ignore
        self, status: int = 0, message: Optional[str] = None
    ) -> None:
        if message:
            self._print_message(message)
