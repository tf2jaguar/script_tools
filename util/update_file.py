#!/usr/bin/python3
import pathlib
import re

root_path = pathlib.Path(__file__).parent.parent.resolve()


def replace_chunk(content, marker, chunk, inline=False):
    r = re.compile(
        r"<!-- {} starts -->.*<!-- {} ends -->".format(marker, marker),
        re.DOTALL,
    )
    if not inline:
        chunk = "\n{}\n".format(chunk)
    chunk = "<!-- {} starts -->{}<!-- {} ends -->".format(marker, chunk, marker)
    return r.sub(chunk, content)


def update_hs_turnover(file, msg):
    readme_file = root_path / file

    md = ''.join(['## ', msg])
    print('write hs_turnover md:\n', md)
    rewritten = replace_chunk(readme_file.open().read(), "github_hs_turnover", md)
    readme_file.open("w").write(rewritten)
