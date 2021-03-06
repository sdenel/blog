#!/usr/bin/env python3
# To launch doctests: python3.7 -m doctest builder.py
import datetime
import locale
import os
import shutil
import subprocess
import time
from distutils.dir_util import copy_tree
from os.path import isfile
import string
from pprint import pprint

from urllib.parse import urlparse

locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')


def get_file_content(p):
    with open(p, 'r', encoding='utf8') as stream:
        return stream.read()


def extract_title_id_and_name(html):
    """
    >>> extract_title_id_and_name(" id='toto'>tata</...>.")
    ('toto', 'tata')
    >>> extract_title_id_and_name(' id="toto" ...>tata</....')
    ('toto', 'tata')
    >>> extract_title_id_and_name(' id="toto" ...>tata</....></fs/>fs</')
    ('toto', 'tata')
    """
    # TODO: A regex might be more clean here.
    # TODO: Is this function slow? If so, improve it.
    section_id = html \
        .split("id")[1] \
        .split("=")[1] \
        .lstrip("""'" """) \
        .split("'")[0].split('"')[0]
    section_name = html \
        .split(">")[1] \
        .split("<")[0]
    return section_id, section_name


def build_menu_inner(html, title_level):
    """
    Extract a menu from HTML
    TODO: extract HTML and export a structure instead (id it does improve something to readability/maintainability.)
    """
    if html.find(f"<h{title_level} ") == -1:
        return ""
    else:
        sections = html.split(f"<h{title_level} ")

        menu_html = ""
        for section in sections[1:]:
            (section_id, section_name) = extract_title_id_and_name(section)
            menu_html += f"<li><a href='#{section_id}'>" + \
                         section_name + \
                         build_menu_inner(section, title_level + 1) + \
                         "</a></li>\n"
        return "<ul>" + menu_html + "</ul>\n"


def build_menu(html):
    content = build_menu_inner(html, 2)
    if len(content) > 0:
        return f"<div id='article_menu'>\n{content}\n</div>"
    else:
        return ""


def is_url(url):
    return urlparse(url).scheme != ""


def int_to_roman(n):
    """
    Convert an integer to a Roman numeral.
    From https://www.oreilly.com/library/view/python-cookbook/0596001673/ch03s24.html
    """

    if not isinstance(n, type(1)):
        raise TypeError("expected integer, got %s" % type(n))
    if not 0 < n < 4000:
        raise ValueError("Argument must be between 1 and 3999")
    ints = (1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1)
    nums = ('M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I')
    result = []
    for i in range(len(ints)):
        count = int(n / ints[i])
        result.append(nums[i] * count)
        n -= ints[i] * count
    return ''.join(result)


def add_roman_to_main_titles(html):
    """
    >>> add_roman_to_main_titles('<h2 ...>a</h2><h2 ...>b</h2>')
    '<h2 ...>I. a</h2><h2 ...>II. b</h2>'
    """
    TAG = "<h2"
    html_splits = html.split(TAG)
    html2 = html_splits[0]
    for cnt, html_split in enumerate(html_splits[1:]):
        p = html_split.find(">")
        html_split = html_split[:p + 1] + f"{int_to_roman(cnt + 1)}. " + html_split[p + 1:]
        html2 += TAG + html_split
    return html2


def add_numbers_to_subtitles(html):
    """
    >>> add_numbers_to_subtitles('<h3 ...>a</h3><h3 ...>b</h3><h2>...</h2><h3>c</h3>')
    '<h3 ...>1. a</h3><h3 ...>2. b</h3><h2>...</h2><h3>1. c</h3>'
    """
    TAG = "<h3"
    TAG_UPPER = "<h2"
    html_splits = html.split(TAG)
    html2 = html_splits[0]
    cnt = 0
    for html_split in html_splits[1:]:
        p = html_split.find(">")
        html_split = html_split[:p + 1] + f"{str(cnt + 1)}. " + html_split[p + 1:]
        html2 += TAG + html_split
        cnt += 1
        if TAG_UPPER in html_split:
            cnt = 0
    return html2


def add_letter_to_subtitles(html):
    """
    >>> add_letter_to_subtitles('<h4 ...>a</h4><h4 ...>b</h4><h3 ...>toto</h3><h4 ...>x</h4>')
    '<h4 ...>a. a</h4><h4 ...>b. b</h4><h3 ...>toto</h3><h4 ...>a. x</h4>'
    """
    TAG = "<h4"
    TAG_UPPER = "<h3"
    html_splits = html.split(TAG)
    html2 = html_splits[0]
    cnt = 0
    for html_split in html_splits[1:]:
        p = html_split.find(">")
        html_split = html_split[:p + 1] + f"{string.ascii_lowercase[cnt]}. " + html_split[p + 1:]
        html2 += TAG + html_split
        cnt += 1
        if TAG_UPPER in html_split:
            cnt = 0
    return html2


def reduce_titles(html):
    """
    h1 -> h2, h2->h3, ...
    """
    assert html.find("<h6") == -1
    for i in reversed(range(1, 6)):
        assert html.count(f"<h{i} ") == html.count(f"</h{i}>")
        html = html.replace(f"<h{i} ", f"<h{i + 1} ")
        html = html.replace(f"</h{i}>", f"</h{i + 1}>")
    return html


def extract_references(html):
    """
    >>> extract_references("...[a][b][c]...")
    [{'raw': '[a][b][c]', 'text': 'a', 'link_name': 'b', 'link': 'c'}]
    >>> extract_references("...[e][f]...")
    [{'raw': '[e][f]', 'text': 'e', 'link_name': 'e', 'link': 'f'}]
    """
    references = []
    p = None
    while True:
        p = html.find("][", p)
        if p == -1:
            break
        data2_end_pos = html.find("]", p + 2)
        if data2_end_pos > -1:
            text_start_pos = html[:p].rfind("[") + 1
            text = html[text_start_pos:p]
            data2 = html[p + 2:data2_end_pos]
            if html[data2_end_pos + 1] == "[":
                link_name = data2
                pos_end = html.find("]", data2_end_pos + 2)
                link = html[data2_end_pos + 2:pos_end]
            else:
                link = data2
                link_name = text
                pos_end = data2_end_pos
            references.append(
                {
                    "raw": html[text_start_pos - 1:pos_end + 1],
                    "text": text,
                    "link_name": link_name,
                    "link": link
                }
            )
        p = pos_end + 1
    return references


def build_references(html):
    """
    Return the HTML, with references inserted where the [[references]] tag is
    """
    references = extract_references(html)
    references_html = ""
    for cnt, reference in enumerate(references, start=1):
        raw = reference['raw']
        link = reference['link']
        text = reference['text']
        link_name = reference['link_name']
        references_html += f"<li id='reference-{cnt}'><a href='#reference-to-{cnt}'>{cnt}</a> - {link_name} : "
        if is_url(reference['link']):
            references_html += f"<a href='#{link}' target='_blank'>{link}</a></li>"
        else:
            references_html += f"{link}</li>"
        reference_str = f"[{text}][{link}]"
        assert reference_str.count(reference_str) == 1
        html = html.replace(
            raw,
            f"{text}<a id='reference-to-{cnt}' href='#reference-{cnt}'><sup>{cnt}</sup></a>"
        )

    if len(references) > 0:
        assert html.count("[[references]]") == 1
    else:
        assert html.count("[[references]]") == 0
    html = html.replace("[[references]]", f"<ul>{references_html}</ul>")
    return html


def title_to_filename(t):
    """
    Transforms a title into a URL compliant filename
    """
    import unidecode
    t = t.replace(" ", "-").replace(":", "-").replace(",", "-").replace(".", "-").replace("'", "-").replace("?", "-")
    while t.find("--") > -1:
        t = t.replace("--", "-")
    t = t.strip(".-")
    t = unidecode.unidecode(t)
    return t.lower() + ".html"


class Date:
    def as_date(self):
        return self.as_datetime().strftime('%d/%m/%Y')

    def as_datetime(self):
        return datetime.datetime.strptime(self.date, "%Y-%m-%d %H:%M:%S %z")

    def __init__(self, date):
        self.date = date


def get_file_creation_modification_date(f):
    """
    Get the date of the creation and latest modification of a file, according to git.
    Output: a tuple of of dates in the Python datetime format.
    """
    cmd = f"git log --date=iso -- {f}"
    # print(cmd)
    git_process = subprocess.run(cmd.split(" "), stdout=subprocess.PIPE)
    stdout = git_process.stdout.decode('utf-8')
    lines = stdout.split("\n")
    # print(lines)
    dates_raw = [x for x in lines if x.startswith("Date:")]
    # "Date:   2019-05-01 20:26:47 +0200" -> "2019-05-01 20:26:47 +0200"
    dates_str = [x[x.find(':') + 1:].strip() for x in dates_raw]
    if len(dates_str) == 0:  # The file is not commited yet
        dates_str = "2099-05-01 20:26:47 +0200", "2099-05-01 20:26:47 +0200"
    print(dates_str)
    return Date(dates_str[-1]), Date(dates_str[0])


def markdown_to_html(md_path):
    html_pandoc_path = os.path.join("target", md_path[4:-3] + "_pandoc.html")
    subprocess.run(["pandoc", md_path, "-o", html_pandoc_path])
    html = get_file_content(html_pandoc_path)
    os.remove(html_pandoc_path)
    return html


def load_yaml(f):
    import ruamel.yaml as yaml
    with open(f, 'r', encoding='utf8') as stream:
        # content = stream.read()
        # print(content)
        return yaml.safe_load(stream)


def load_contributors():
    return load_yaml("contributors.yaml")


def main():
    import jinja2

    if os.path.exists("target"):
        shutil.rmtree("target")
    os.mkdir("target")

    contributors = load_contributors()
    articles = []
    # os.mkdir("target")
    j2_env = jinja2.Environment(loader=jinja2.FileSystemLoader("."), trim_blocks=True)
    j2_env.globals["generationDate"] = time.strftime('%A %d/%m/%Y %H:%M:%S')

    for root, dirs, files in os.walk("src/"):
        for file in files:
            if file.endswith(".yaml"):
                print(f"[file={file}]")
                article_yaml_path = os.path.join(root, file)
                article_md_path = os.path.join(root, file[:-5] + ".md")
                assert isfile(article_md_path), f"{article_yaml_path} found without its .md! ({article_md_path})"
                print(f"[article_yaml_path={article_yaml_path}]")

                creation_date, modification_date = get_file_creation_modification_date(article_md_path)

                article_yaml = load_yaml(article_yaml_path)
                # Handling mandatory keys
                for mandatory_key in ["title", "description", "writersIds"]:
                    assert mandatory_key in article_yaml, f"{article_yaml_path} does not contain a {mandatory_key} key."

                # Checking writers and reviewers are declared
                # TODO refactor this big ball of mud
                writers_ids = article_yaml['writersIds']
                if isinstance(writers_ids, str):
                    writers_ids = [writers_ids]
                for writer_id in writers_ids:
                    assert writer_id in list(contributors), writer_id
                reviewers_ids = article_yaml['reviewersIds'] if 'reviewersIds' in article_yaml else []
                for reviewer_id in reviewers_ids:
                    assert reviewer_id in list(contributors), reviewer_id

                pprint(article_yaml["title"])

                article_path = article_md_path[4:-3]
                article_html_path = os.path.join("target", article_md_path[4:-3] + ".html")

                #
                # Check that the file is named according to its content title, or throw.
                #
                title_as_filename = title_to_filename(article_yaml['title'])
                if not article_html_path.endswith(title_as_filename):
                    print(f"Please rename {article_html_path} to {title_as_filename}")
                    exit(1)

                content_as_html = markdown_to_html(article_md_path)
                content_as_html = reduce_titles(content_as_html)
                content_as_html = add_roman_to_main_titles(content_as_html)
                content_as_html = add_numbers_to_subtitles(content_as_html)
                content_as_html = add_letter_to_subtitles(content_as_html)
                content_as_html = build_references(content_as_html)

                menu_as_html = build_menu(content_as_html)

                illustration_path = ("illustrations/" + article_path + '.' + article_yaml['illustration']) \
                    if 'illustration' in article_yaml \
                    else "data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs="  # Blank image

                is_draft=article_yaml['draft'] if 'draft' in article_yaml else False
                print(f"Creating {article_html_path}")
                with open(article_html_path, 'w', encoding='utf8') as stream:
                    stream.write(j2_env.get_template('template/article.j2.html').render(
                        title=article_yaml['title'],
                        is_draft=is_draft,
                        creation_date=creation_date,
                        modification_date=modification_date,
                        description=article_yaml['description'],
                        content=content_as_html,
                        rawLink=article_md_path,
                        menu_as_html=menu_as_html,
                        writers=[contributors[c] for c in writers_ids],
                        reviewers=[contributors[c] for c in reviewers_ids],
                        illustration_path=illustration_path
                    ))

                articles.append({
                    "title": article_yaml['title'],
                    "is_draft": is_draft,
                    "content_as_html": content_as_html,
                    "description": article_yaml['description'],
                    "path": article_html_path[article_html_path.find("target/") + 7:],
                    "creation_date": creation_date,
                    "modification_date": modification_date,
                    "illustration_path": illustration_path
                })

    #
    # Creating index and sitemap
    #
    articles.sort(key=lambda a: a['creation_date'].as_datetime(), reverse=True)

    print(f"Creating index.html")
    with open("target/index.html", 'w', encoding='utf8') as stream:
        stream.write(j2_env.get_template('template/index.j2.html').render(
            articles=articles,
            title="Accueil"
        ))

    print(f"Creating dump.html")
    # Allows during dev to extract the content to the grammar checker of your choice
    print(os.environ)
    if "COMPILATION_MODE" in os.environ and os.environ["COMPILATION_MODE"] == "DEV":
        with open("target/dump.html", 'w', encoding='utf8') as stream:
            stream.write(j2_env.get_template('template/dump.j2.html').render(
                articles=articles
            ))

    print(f"Creating sitemap.xml")
    with open("target/sitemap.xml", 'w', encoding='utf8') as stream:
        stream.write(j2_env.get_template('template/sitemap.j2.xml').render(
            articles=articles,
        ))

    #
    # Add static content
    #
    copy_tree("static", "target")


if __name__ == "__main__":
    main()
