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

import os
import shutil
import glob
import codecs
import optparse
import pkg_resources
from datetime import datetime, timedelta

from mako.lookup import TemplateLookup
from mako.runtime import Context


import hookiidb

# Globals
debug = False
force = False
today = False
directory = "/tmp/originals"
templatelookup = TemplateLookup(directories=[pkg_resources.resource_filename(__name__, "templates")])


class HookiiTree:
    def __init__(self, content=None):
        self.content = content
        self.children = []

    def __iter__(self):
        yield self.content
        for child in self.children:
            for child_content in child:
                yield child_content


def build_tree(postlist, commentlist):
    posts = {}
    comments = {}
    tree = HookiiTree()

    for p in postlist:
        if p["comment_count"] == 0:
            continue
        if p["comment_status"] == "closed":
            continue

        p["level"] = 0
        p["title"] = p["post_title"]
        node = HookiiTree(p)

        tree.children.append(node)
        posts[p["id"]] = node

    for c in commentlist:
        try:
            _, c["comment_disqusid"] = c["comment_agent"].split(":")
        except ValueError:
            c["comment_disqusid"] = "0"
        node = HookiiTree(c)

        post = posts.get(c["comment_post_ID"])

        if post is None:
            print "No post (%d) for comment (%d)" % (c["comment_post_ID"], c["comment_id"])
            continue

        if c["comment_parent"] == 0:
            parent = post
        else:
            parent = comments.get(c["comment_parent"])
            if parent is None:
                print "No parent comment (%d) for comment (%d) in post (%d)" % (c["comment_parent"], c["comment_id"], c["comment_post_ID"])
                continue
            node.content["parent_author"] = parent.content["comment_author"]
        node.content["level"] = parent.content["level"] + 1

        parent.children.append(node)
        comments[c["comment_id"]] = node

    return tree


def render_posts(tree):
    for node_post in tree.children:
        iterator = iter(node_post)
        ctx_post = next(iterator)
        ctx_post["comments"] = iterator
        render_template("post.mako", ctx_post, "%s.html" % node_post.content["post_name"])


def render_index(tree):
    ctx_index = {
        "title": "Index Archive",
        "total_posts": len(tree.children),
        "posts": (node.content for node in reversed(tree.children))
    }
    render_template("index.mako", ctx_index, "today.html" if today else "index.html")


def hookiifier(user, passw, database, today):
    db = hookiidb.HookiiDB(user, passw, database)

    if today:
        yesterday = datetime.now() - timedelta(days=1)
        datetoday = yesterday.strftime("%Y-%m-%d")
        posts = db.get_posts(datetoday)
        comments = db.get_comments(datetoday)

        tree = build_tree(posts, comments)
        render_posts(tree)
        render_index(tree)
    else:
        datemax = datetime.now()
        delta = timedelta(days=30)
        datemin = datemax - delta
        posttree = HookiiTree()
        while db.exist_older_posts(datemax):
            posts = db.get_posts(datemin, datemax)
            comments = db.get_comments(datemin, datemax)
            tree = build_tree(posts, comments)
            render_posts(tree)
            posttree.children += [HookiiTree(postnode.content) for postnode in tree.children]
            datemin, datemax = (datemax - delta * 2, datemin)
        render_index(posttree)


#------------------------------------------------------------
# File and printing utilities

def createfile(file):
    import os.path
    global directory

    if not os.path.exists(directory):
        os.makedirs(directory)

    file = os.path.join(directory, file)

    findex = codecs.open(file, encoding='utf-8', mode='w')
    return findex


def copystaticfiles():
    if not os.path.exists(directory):
        os.makedirs(directory)

    source_dir = pkg_resources.resource_filename(__name__, 'static')
    for filename in glob.iglob(os.path.join(source_dir, '*')):
        try:
            shutil.copy(filename, directory)
        except shutil.Error as e:
            print('Error copying static file: %s' % e)
        except IOError as e:
            print('Error copying static file: %s' % e.strerror)


def render_template(template, context, outfile):
    with createfile(outfile) as f:
        ctx = Context(f, **context)
        t = templatelookup.get_template(template)
        t.render_context(ctx)
        f.close()



#------------------------------------------------------------
# Main finally
def main():
    global debug
    global force
    global today
    global directory

    Version = 0.9

    parser = optparse.OptionParser()
    parser.add_option('--database', action="store", dest="database", type="string", default="wordpress")
    parser.add_option('--directory', action="store", dest="directory", type="string", default="/tmp/archived")
    parser.add_option('--user', action="store", dest="user", type="string", default="admin")
    parser.add_option('--pass', action="store", dest="password", type="string", default="xxx")
    parser.add_option('--debug', action="store_true", dest="debug")
    parser.add_option('--force', action="store_true", dest="force")
    parser.add_option('--today', action="store_true", dest="today")

    # get args
    options, args = parser.parse_args()
    debug = options.debug
    force = options.force
    today = options.today
    directory = options.directory

    copystaticfiles()

    hookiifier(options.user, options.password, options.database, today)

if __name__ == '__main__':
    main()
