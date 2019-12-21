from exoskelton.plugin_base import PluginBase


def test_fromat_table():
    # setup
    PluginBase.__abstractmethods__ = frozenset()
    p = PluginBase(keyword="test")
    header = ["First", "Second"]
    items = [["Everest", "K2"], ["ཇོ་མོ་གླང་མ", "K2"]]
    expected = [
        "\n".join(
            [
                "```",
                "First       | Second",
                "--------------------",
                "Everest     | K2    ",
                "ཇོ་མོ་གླང་མ | K2    ",
                "```",
            ]
        )
    ]

    # run
    result = p.format_table(items=items, header=header)

    # validation
    assert result == expected

    # tear down
