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


def build_references(html):
    """
    Return the HTML, with references inserted where the [[references]] tag is
    """
    references = []
    p = None
    while True:
        p = html.find("][", p)
        if p == -1:
            break
        potential_url_end_pos = html.find("]", p + 2)
        if potential_url_end_pos > -1:
            potential_url = html[p + 2:potential_url_end_pos]
            title_start_pos = html[:p].rfind("[") + 1
            references.append((html[title_start_pos:p], potential_url))
        p += 1
    references_html = ""
    for cnt, reference in enumerate(references, start=1):
        references_html += f"<li id='reference-{cnt}'><a href='#reference-to-{cnt}'>{cnt}</a> - {reference[0]} : "
        if is_url(reference[1]):
            references_html += f"<a href='#{reference[1]}' target='_blank'>{reference[1]}</a></li>"
        else:
            references_html += f"{reference[1]}</li>"
        reference_str = f"[{reference[0]}][{reference[1]}]"
        assert reference_str.count(reference_str) == 1
        html = html.replace(reference_str,
                            f"<a id='reference-to-{cnt}' href='#reference-{cnt}'>{reference[0]}<sup>{cnt}</sup></a>")

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
                content_as_html = build_references(content_as_html)

                menu_as_html = build_menu(content_as_html)

                print(f"Creating {article_html_path}")
                with open(article_html_path, 'w', encoding='utf8') as stream:
                    stream.write(j2_env.get_template('template/article.j2.html').render(
                        title=article_yaml['title'],
                        creation_date=creation_date,
                        modification_date=modification_date,
                        description=article_yaml['description'],
                        content=content_as_html,
                        rawLink=article_md_path,
                        menu_as_html=menu_as_html,
                        writers=[contributors[c] for c in writers_ids],
                        reviewers=[contributors[c] for c in reviewers_ids]
                    ))

                articles.append({
                    "title": article_yaml['title'],
                    "content_as_html": content_as_html,
                    "description": article_yaml['description'],
                    "path": article_html_path[article_html_path.find("target/") + 7:],
                    "creation_date": creation_date,
                    "modification_date": modification_date
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
