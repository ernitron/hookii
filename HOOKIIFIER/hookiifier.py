#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Here how it works
# Opens articles
# for each article prints its comments
# write an index.htlm with all articles
# Erni Tron was here 2014 (c)
# Hookii Dookii productions 2014
# DATE: Mon Nov 24 15:48:21 CET 2014

from __future__ import print_function
import os
import shutil
import glob
import io
import argparse
import pkg_resources
import logging
from datetime import datetime, timedelta

from mako.lookup import TemplateLookup
from mako.runtime import Context

try:
    from HOOKIIFIER import hookiidb
except ImportError:
    import hookiidb


__version__ = pkg_resources.get_distribution("HOOKIIFIER").version


class HookiiTree:
    def __init__(self, content=None):
        self.content = content
        self.children = []

    def __iter__(self):
        yield self.content
        for child in reversed(self.children):
            for child_content in child:
                yield child_content


class HookiiRenderer:
    def __init__(self, output_directory):
        self.logger = logging.getLogger(__name__)
        self.lookup = TemplateLookup(directories=[
            pkg_resources.resource_filename(__name__, "templates")])
        self.outdir = output_directory

    def _render_template(self, template_filename, context, output_filename):
        outfile = os.path.join(self.outdir, output_filename)
        with io.open(outfile, "w", encoding="utf-8") as f:
            ctx = Context(f, **context)
            t = self.lookup.get_template(template_filename)
            t.render_context(ctx)
            self.logger.debug("Rendered %s to %s", template_filename, outfile)

    def render_posts(self, tree):
        # for each post subtree
        for node_post in tree.children:
            iterator = iter(node_post)
            # first object is the post itself
            post = next(iterator)
            ctx_post = {
                "title": post["post_title"],
                "post": post,
                # the remaining objects are comments
                "comments": iterator
            }
            filename = "%s.html" % post["post_name"]
            self._render_template("post.mako", ctx_post, filename)

    def render_index(self, tree, today=False):
        ctx_index = {
            "title": "Index Archive",
            "total_posts": len(tree.children),
            "posts": (node.content for node in reversed(tree.children))
        }
        filename = "today.html" if today else "index.html"
        self._render_template("index.mako", ctx_index, filename)


def build_tree(postlist, commentlist):
    logger = logging.getLogger(__name__)
    logger.info("postlist length    = %d", len(postlist))
    logger.info("commentlist length = %d", len(commentlist))
    # post dictionary {postid: post}
    posts = {}
    # comment dictionary {commentid: comment}
    comments = {}
    # main tree
    tree = HookiiTree()

    for p in postlist:
        # set additional values
        p["level"] = 0

        logger.debug("post %d", p["id"])
        # insert post into tree and dict
        node = HookiiTree(p)
        tree.children.append(node)
        posts[p["id"]] = node

    for c in commentlist:
        # retrieve parent (comment or post)
        if c["comment_parent"] == 0:
            parent = posts.get(c["comment_post_ID"])
        else:
            parent = comments.get(c["comment_parent"])
        if parent is None:
            logger.debug("Comment %s has no existing parent", c["comment_id"])
            continue

        # set additional values for the comment
        parent_author = parent.content.get("comment_author")
        if parent_author is not None:
            c["parent_author"] = parent_author

        c["level"] = parent.content["level"] + 1

        try:
            _, c["comment_disqusid"] = c["comment_agent"].split(":")
        except ValueError:
            c["comment_disqusid"] = "0"
            logger.info("Can't extract disqusid from comment agent '%s' of comment %d", c["comment_agent"], c["comment_id"])

        logger.debug("comment %s of post %d", c["comment_id"], c["comment_post_ID"])
        # insert comment into tree and dict
        node = HookiiTree(c)
        parent.children.append(node)
        comments[c["comment_id"]] = node

    logger.info("Post nodes = %d (%d posts not added to the tree)", len(posts), len(postlist) - len(posts))
    logger.info("Comment nodes= %d (%d comments not added to the tree)", len(comments),len(commentlist) - len(comments))

    return tree


def hookiifier(args):
    logger = logging.getLogger(__name__)
    db = hookiidb.HookiiDB(args.user, args.password, args.database)
    renderer = HookiiRenderer(args.directory)
    lastrun = read_last_run(args.last_run_file)

    if args.today:
        logger.info("Hookiifier section TODAY")
        # calculate time span
        yesterday = datetime.now() - timedelta(days=1)
        yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        logger.info("Time range = (%s, %s]", yesterday, datetime.now())

        # get posts and comments from db
        posts = db.get_posts(yesterday,
                             only_published=True,
                             only_with_comments=True,
                             only_open=not args.force)
        comments = db.get_comments(yesterday)

        # build tree and render posts and index
        tree = build_tree(posts, comments)
        renderer.render_posts(tree)
        renderer.render_index(tree, args.today)

    elif lastrun is not None and datetime.now() - lastrun < timedelta(days=30):
        logger.info("Hookiifier section LASTRUN")
        # timestamp to save in last-run file
        timestamp = datetime.now()

        # get posts with at least one new comment, and all their comments
        posts = db.get_posts_with_new_comments(lastrun,
                             only_published=True,
                             only_open=True)
        comments = db.get_comments_of_posts_with_new_comments(lastrun)

        # build tree and render posts
        tree = build_tree(posts, comments)
        renderer.render_posts(tree)

        # get all posts to render index
        posts = db.get_posts(only_published=True,
                             only_with_comments=True,
                             only_open=not args.force)
        # additional tree to accumulate (only) posts
        posttree = HookiiTree()
        posttree.children = [HookiiTree(p) for p in posts]

        # render index
        renderer.render_index(posttree)

        # save timestamp
        write_last_run(timestamp, args.last_run_file)

    else:
        logger.info("Hookiifier section ALL")
        # calculate initial time span
        delta = timedelta(days=args.deltat)
        timestamp = datetime.now()
        datemax = timestamp
        datemin = datemax - delta

        # additional tree to accumulate (only) posts
        posttree = HookiiTree()

        # get minimum post date from db
        min_post_date = db.min_post_date(only_published=True,
                                         only_with_comments=True)
        logger.info("Minimum post date = %s", min_post_date)

        while datemax >= min_post_date:
            logger.info("Time range (%s, %s]", datemin, datemax)

            # get posts and comments from db
            posts = db.get_posts(datemin, datemax,
                                 only_published=True,
                                 only_with_comments=True,
                                 only_open=not args.force)
            comments = db.get_comments(datemin, datemax)

            # build tree and render posts and index
            tree = build_tree(posts, comments)
            renderer.render_posts(tree)

            # keep post data to render the complete index
            posttree.children += [HookiiTree(n.content) for n in reversed(tree.children)]

            # update time span
            datemin, datemax = (datemax - delta * 2, datemin)

        # render complete index
        posttree.children.reverse()
        renderer.render_index(posttree)

        write_last_run(timestamp, args.last_run_file)

#------------------------------------------------------------
# File and printing utilities
def write_last_run(timestamp, filepath):
    logger = logging.getLogger(__name__)
    try:
        with open(filepath, 'w') as f:
            f.write(timestamp.strftime("%Y-%m-%d %H:%M:%S"))
    except IOError as e:
        logger.warning(e)

def read_last_run(filepath):
    logger = logging.getLogger(__name__)
    if not os.path.isfile(filepath):
        return None
    try:
        with open(filepath, 'r') as f:
            string = f.read().strip()
            return datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
    except (IOError, ValueError) as e:
        logger.warning(e)
        return None

#------------------------------------------------------------
# Main finally
def main():
    parser = argparse.ArgumentParser(description="Hookii archiver.")
    parser.add_argument("--database", default="wordpress", help="database name")
    parser.add_argument("--user", default="admin", help="database user")
    parser.add_argument("--password", "--pass", required=True, help="database password")
    parser.add_argument("--directory", default="/tmp/archived", help="output directory")
    parser.add_argument("--last-run-file", default="/tmp/hookiifier-last-run", help="file with timestamp of last run")
    parser.add_argument("--deltat", default=30, type=int, help="chunk size for db querying, in days")
    parser.add_argument("--force", action="store_true", help="also render closed posts")
    parser.add_argument("--today", action="store_true", help="render only posts from last day")
    parser.add_argument("--loglevel", default="WARNING", choices=["CRITICAL","ERROR","WARNING","INFO","DEBUG","NOTSET"], type=str.upper)
    parser.add_argument("--version", action="version", version=__version__)

    args = parser.parse_args()

    # configure logger
    numeric_level = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % args.loglevel)
    logging.basicConfig(level=numeric_level, format="%(levelname)s:%(name)s:%(funcName)s(): %(message)s")
    logger = logging.getLogger(__name__)

    logger.debug(args)

    # create output directory if not existent
    try:
        os.makedirs(args.directory)
    except OSError:
        if not os.path.isdir(args.directory):
            raise

    # copy static files
    source_dir = pkg_resources.resource_filename(__name__, 'static')
    for filename in glob.iglob(os.path.join(source_dir, '*')):
        try:
            shutil.copy(filename, args.directory)
            logger.debug("copied static file %s to %s", filename, args.directory)
        except shutil.Error as e:
            logger.error('Error copying static file: %s' % e)
        except IOError as e:
            logger.error('Error copying static file: %s' % e.strerror)

    # archive!
    hookiifier(args)

if __name__ == '__main__':
    main()
