import re
import textwrap as _textwrap
from argparse import ArgumentParser, RawDescriptionHelpFormatter


class PreserveWhiteSpaceWrapRawTextHelpFormatter(RawDescriptionHelpFormatter):
    def __init__(self, **kwarg):  # type: ignore
        super().__init__(width=1000, **kwarg)

    def __add_whitespace(self, idx, iWSpace, text):  # type: ignore
        if idx == 0:
            return text
        return (" " * iWSpace) + text

    def _split_lines(self, text, width):  # type: ignore
        textRows = text.splitlines()
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
    def __init__(self, message):  # type: ignore
        self.message = message


class SlackArgumentParser(ArgumentParser):
    """
    SlackArgumentParser is modified to keep process working after parse error
    """

    def __init__(self, **kwarg):  # type: ignore
        super().__init__(
            formatter_class=PreserveWhiteSpaceWrapRawTextHelpFormatter, **kwarg
        )

    def add_subparsers(self, **kwarg) -> "SlackArgumentParser":  # type: ignore
        return super().add_subparsers(**kwarg)  # type: ignore

    def _print_message(self, message, file=None) -> None:  # type: ignore
        if message:
            raise SlackArgumentParserException(message)

    def exit(self, status=0, message=None) -> None:  # type: ignore
        if message:
            self._print_message(message)
