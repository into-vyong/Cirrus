# from markdown import Markdown
from io import StringIO
from os import walk
from pathlib import Path, PosixPath
from datetime import datetime
import json


# def unmark_element(element, stream=None):
#     if stream is None:
#         stream = StringIO()
#     if element.text:
#         stream.write(element.text)
#     for sub in element:
#         unmark_element(sub, stream)
#     if element.tail:
#         stream.write(element.tail)
#     return stream.getvalue()


# # patching Markdown
# Markdown.output_formats["plain"] = unmark_element
# __md = Markdown(output_format="plain", extensions=["pymdownx.tilde"])
# __md.stripTopLevelTags = False

from bs4 import BeautifulSoup
from markdown import Markdown
import re

markdown = Markdown(extensions=["pymdownx.tilde"])


def markdown_to_text(markdown_string):
    """ Converts a markdown string to plaintext """

    # md -> html -> text since BeautifulSoup can extract text cleanly
    html = markdown.convert(markdown_string)

    # remove code snippets
    html = re.sub(r"<pre>(.|\n)*?</pre>", " ", html)
    html = re.sub(r"<code>(.|\n)*?</code>", " ", html)

    # extract text
    soup = BeautifulSoup(html, "html.parser")
    text = "".join(soup.findAll(text=True))

    return text


def textify(md_text):
    # return __md.convert(md_text)
    return markdown_to_text(md_text)


blogs = []


def open_md(p: PosixPath):
    data = dict(
        title="",
        slug="",
        date="",
        tags=[],
        category="",
        content="",
        published=True,
    )
    with p.open() as f:
        lines = f.readlines()
    content_start_line, line_count = 0, 0
    pre_field = ""
    for i, line in enumerate(lines):
        if ":" in line:
            field, value = line.split(":", 1)
            if field != "tags" and field in data:
                data[field] = value.strip().strip("'").strip('"').strip("-")
            pre_field = field
        elif pre_field == "tags":
            data["tags"].append(line.strip().strip("-").strip())
        if line.startswith("---"):
            line_count += 1
        if line_count == 2:
            content_start_line = i
            break
    content = (
        textify("".join(lines[content_start_line:]))
        .replace("--", "")
        .replace("more", "")
        .replace("\n", "")
    )
    data["content"] = re.sub("```(.|\n)*?```", " ", content)
    data["url"] = f"/posts/{data.pop('slug')}/"
    d = datetime.fromisoformat(data["date"])
    data["date"] = int(d.timestamp())
    if data.pop("published") != "false":
        blogs.append(data)
    # print(data)


for path, _, files in walk("./content"):
    if path != "./content/posts":
        continue
    p = Path(path)
    for filename in files:
        if not filename.endswith(".md"):
            continue
        full_path = p.joinpath(filename)
        open_md(full_path)

with open("blogs.json", "w") as f:
    json.dump(blogs, f, ensure_ascii=False, indent=2)