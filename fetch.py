import praw
from praw.models import MoreComments
from jinja2 import Environment, FileSystemLoader
import os
import glob
import re
import datetime

SUB = "WritingPrompts"
IGNORE_USERS = [
    "AutoModerator"
]

env = Environment(loader=FileSystemLoader("templates"))
reddit = praw.Reddit(
    client_id=os.environ["REDDIT_CLIENT_ID"],
    client_secret=os.environ["REDDIT_APP_SECRET"],
    user_agent=os.environ["REDDIT_USER_AGENT"]
)


def get_filename(filename):
    for c in r"'[]/\;,><&*:%=+@!#^()|?^":
        filename = filename.replace(c, "")
    return filename


def get_posts(sidebar):
    table_regex = re.compile(r"Weekly Schedule(?:.|\n)+(?:\|Feature(?:.|\n)+-\|)((?:.|\n)+)\nRules")
    res = table_regex.search(sidebar)
    table = res.group(1).strip().split("\n")

    feature_regex = re.compile(r"\[(.*?)\]\((.*?)\)\|")
    latest_regex = re.compile(r"\|.*?\[(.*?)\]\((.*?redd\.it.*?)\)")
    posts = []

    for row in table:
        feature = feature_regex.findall(row)
        latest = latest_regex.findall(row)
        if len(feature) and len(latest):
            post_id = latest[0][1].rstrip(" /").split("/")[-1]
            submission = reddit.submission(id=post_id)
            submission.comment_sort = "old"
            if not submission.title.startswith("[OT]"):
                comments = [
                    c for c in submission.comments.list()
                    if c.parent_id.startswith("t3") and c.author not in IGNORE_USERS
                ]

                posts.append({
                    "feature": feature[0][0].replace("*", ""),
                    "submission": submission,
                    "comments": comments
                })

    return posts


def write_posts(posts):
    for f in glob.glob("docs/_posts/*"):
        print(f"Removing {f}")
        os.remove(f)

    template = env.get_template("page.md")
    for post in posts:
        rendered = template.render(
            submission=post["submission"],
            comments=post["comments"]
        )

        date = datetime.datetime.fromtimestamp(post["submission"].created_utc)
        filename = f"{date:%Y-%m-%d}-{post['feature']}.md"
        with open(f"docs/_posts/{filename}", "w") as out:
            print(f"Writing {filename}")
            out.write(rendered)


def write_footer():
    with open("docs/_includes/footer.html", "w") as out:
        print("Writing footer.html")
        template = env.get_template("footer.html")
        rendered = template.render(
            updated=datetime.datetime.now().strftime("%B %-d, %Y %-I:%M %p")
        )
        out.write(rendered)


def main():
    wp = reddit.subreddit(SUB)
    posts = get_posts(wp.description)
    if len(posts):
        write_posts(posts)
        write_footer()


if __name__ == "__main__":
    main()
