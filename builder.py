#!/usr/bin/env python3
# To launch doctests: python3.7 -m doctest builder.py
import datetime
import os
import shutil
import subprocess

from pprint import pprint

import time

from distutils.dir_util import copy_tree
import locale
from os.path import isfile

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
    return f"<div id='article_menu'>\n{build_menu_inner(html, 1)}\n</div>"


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


def get_file_creation_modification_date(f):
    """
    Get the date of the creation and latest modification of a file, according to git.
    Output: a tuple of of dates in the Python datetime format.
    """
    git_process = subprocess.run(f"git log --date=iso --diff-filter=A -- {f}".split(" "), stdout=subprocess.PIPE)
    stdout = git_process.stdout.decode('utf-8')
    lines = stdout.split("\n")
    dates_raw = [x for x in lines if x.startswith("Date:")]
    # "Date:   2019-05-01 20:26:47 +0200" -> "2019-05-01 20:26:47 +0200"
    dates_str = [x[x.find(':') + 1:].strip() for x in dates_raw]
    if len(dates_str) == 0:  # The file is not commited yet
        dates_str = "2099-05-01 20:26:47 +0200", "2099-05-01 20:26:47 +0200"
    dates = [datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S %z") for x in dates_str]
    print(dates)
    return dates[0], dates[-1]


def date_to_str(d):
    return d.strftime('%d/%m/%Y')


def markdown_to_html(md_path):
    html_pandoc_path = os.path.join("target", md_path[4:-3] + "_pandoc.html")
    subprocess.run(["pandoc", md_path, "-o", html_pandoc_path])
    html = get_file_content(html_pandoc_path)
    os.remove(html_pandoc_path)
    return html


def main():
    import ruamel.yaml as yaml
    import jinja2

    if os.path.exists("target"):
        shutil.rmtree("target")
    os.mkdir("target")

    articles = []
    # os.mkdir("target")
    j2_env = jinja2.Environment(loader=jinja2.FileSystemLoader("."), trim_blocks=True)
    j2_env.globals["generationDate"] = time.strftime('%A %d/%m/%Y %H:%M:%S')

    for root, dirs, files in os.walk("src/"):
        for file in files:
            if file.endswith(".yaml"):
                article_yaml_path = os.path.join(root, file)
                article_md_path = os.path.join(root, file[:-5] + ".md")
                assert isfile(article_md_path), f"{article_yaml_path} found without its .md! ({article_md_path})"
                print(article_yaml_path)

                creation_date, modification_date = get_file_creation_modification_date(article_md_path)

                with open(article_yaml_path, 'r', encoding='utf8') as stream:
                    # content = stream.read()
                    # print(content)
                    article_yaml = yaml.safe_load(stream)
                    assert 'title' in article_yaml, f"{article_yaml_path} does not contain a title."
                    assert 'description' in article_yaml, f"{article_yaml_path} does not contain a description."

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

                menu_as_html = build_menu(content_as_html)

                print(f"Creating {article_html_path}")
                with open(article_html_path, 'w', encoding='utf8') as stream:
                    stream.write(j2_env.get_template('template/article.j2.html').render(
                        title=article_yaml['title'],
                        creation_date_str=date_to_str(creation_date),
                        modification_date_str=date_to_str(modification_date),
                        description=article_yaml['description'],
                        content=content_as_html,
                        rawLink=article_md_path,
                        menu_as_html=menu_as_html
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
    articles.sort(key=lambda a: a['creation_date'], reverse=True)

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
