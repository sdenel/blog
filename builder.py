#!/usr/bin/env python3
import os
import shutil
import subprocess

from pprint import pprint

import time
import ruamel.yaml as yaml
import jinja2
import unidecode
from distutils.dir_util import copy_tree
import locale

locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

if os.path.exists("target"):
    shutil.rmtree("target")
os.mkdir("target")


def get_file_content(p):
    with open(p, 'r', encoding='utf8') as stream:
        return stream.read()


def title_to_filename(t):
    t = t.replace(" ", "-").replace(":", "-").replace(",", "-").replace(".", "-").replace("'", "-")
    while t.find("--") > -1:
        t = t.replace("--", "-")
    t = t.strip(".-")
    t = unidecode.unidecode(t)
    return t.lower() + ".html"


def main():
    articles = []
    # os.mkdir("target")
    j2_env = jinja2.Environment(loader=jinja2.FileSystemLoader("."), trim_blocks=True)
    j2_env.globals["generationDate"] = time.strftime('%A %d/%m/%Y %H:%M:%S')

    for root, dirs, files in os.walk("src/"):
        for file in files:
            if file.endswith(".yaml"):
                article_yaml_path = os.path.join(root, file)
                article_md_path = os.path.join(root, file[:-5] + ".md")
                assert os.path.isfile(
                    article_md_path), f"{article_yaml_path} found without its .md! ({article_md_path})"
                print(article_yaml_path)

                with open(article_yaml_path, 'r', encoding='utf8') as stream:
                    # content = stream.read()
                    # print(content)
                    article_yaml = yaml.safe_load(stream)
                    assert 'title' in article_yaml, f"{article_yaml_path} does not contain a title."
                    assert 'description' in article_yaml, f"{article_yaml_path} does not contain a description."

                pprint(article_yaml["title"])
                article_html_pandoc_path = os.path.join("target", article_md_path[4:-3] + "_pandoc.html")
                article_html_path = os.path.join("target", article_md_path[4:-3] + ".html")

                title_as_filename = title_to_filename(article_yaml['title'])
                if not article_html_path.endswith(title_as_filename):
                    print(f"Please rename {article_html_path} to {title_as_filename}")
                    exit(1)

                subprocess.run(
                    ["pandoc", article_md_path, "-o", article_html_pandoc_path])
                print(f"Creating {article_html_path}")
                with open(article_html_path, 'w', encoding='utf8') as stream:
                    stream.write(j2_env.get_template('template/article.j2.html').render(
                        title=article_yaml['title'],
                        description=article_yaml['description'],
                        content=get_file_content(article_html_pandoc_path),
                        rawLink=article_md_path
                    ))

                os.remove(article_html_pandoc_path)
                articles.append({
                    "title": article_yaml['title'],
                    "description": article_yaml['description'],
                    "path": article_html_path[article_html_path.find("target/") + 7:]
                })

    print(f"Creating index.html")
    with open("target/index.html", 'w', encoding='utf8') as stream:
        stream.write(j2_env.get_template('template/index.j2.html').render(
            articles=articles,
            title="Accueil"
        ))

    print(f"Creating sitemap.xml")
    with open("target/sitemap.xml", 'w', encoding='utf8') as stream:
        stream.write(j2_env.get_template('template/sitemap.j2.xml').render(
            articles=articles,
        ))

    copy_tree("static", "target")


if __name__ == "__main__":
    main()
