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

import MySQLdb as mysql
import sys
import os
import shutil
import glob
import time
import re
import codecs
import optparse
import pkg_resources
from datetime import datetime, timedelta
from mako.template import Template
from mako.lookup import TemplateLookup
from mako.runtime import Context
#libs = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__))))
#sys.path.append(libs)
#from utils import *

import hookiidb

# Globals
debug = False
force = False
today = False
db = None
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
        
        node.content["parent_author"] = parent.content.get("comment_author", None)
        node.content["level"] = parent.content.get("level", 0) + 1
        
        parent.children.append(node)
        comments[c["comment_id"]] = node
    
    return tree

def render_articles(tree):
    for post in tree.children:
        iterator = iter(post)
        article = next(iterator)
        article["comments"] = iterator
        render_template("archivearticle.mako", article, "%s.html" % post.content["post_name"])
        
def render_index(tree):
    ctx_index = {
        "title": "Index Archive",
        "total_articles": len(tree.children),
        "articles": (node.content for node in reversed(tree.children))
    }
    render_template("archiveindex.mako", ctx_index, "today.html" if today else "index.html")

def hookiifier(user, passw, database, today):
    db = hookiidb.HookiiDB(user, passw, database)

    yesterday = datetime.now() - timedelta(days=1)
    datetoday = yesterday.strftime("%Y-%m-%d") if today else None
    posts = db.get_posts(datetoday)
    comments = db.get_comments(datetoday)
    
    tree = build_tree(posts, comments)
    render_articles(tree)
    render_index(tree)

#------------------------------------------------------------
# Database primitives
def dbconnect(database, user, passw) :
    global db

    try:
        db = mysql.connect(host="localhost", # your host, usually localhost
                           user=user,        # your username
                           passwd=passw,     # your password
                           db=database,      # name of the data base
                           charset="utf8",
                           use_unicode=True)
    except:
        print >> sys.stderr, "Error open db"
        sys.exit()


#------------------------------------------------------------
# Articles and Post primitives
def getarticle() :
    global db

    cur = db.cursor()

    if today :
        #datetoday = time.strftime('%Y-%m-%d')
        #from datetime import datetime
        #datetoday = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        #datetoday = datetime.strptime(str(datetoday), '%Y-%m-%d %H:%M:%S')
        from datetime import datetime, timedelta
        yesterday = datetime.now() - timedelta(days=1)
        datetoday = yesterday.strftime('%Y-%m-%d')
        sql = "select id, post_date, post_author, post_title, post_content, comment_count, post_name, comment_status from avwp_posts where post_date > '%s' order by post_date desc " % datetoday

    elif debug :
        # Debug query
        sql = "select id, post_date, post_author, post_title, post_content, comment_count, post_name, comment_status from avwp_posts order by post_date desc limit 0, 300"
    else :
        # Production query (just swap them)
        sql = "select id, post_date, post_author, post_title, post_content, comment_count, post_name, comment_status from avwp_posts order by post_date desc"

    try:
        cur.execute(sql)
    except:
        print >> sys.stderr, "Error query: ", sql
        return

    # print all the articles
    articles = []
    for (pid, pdate, pauthor, ptitle, pcontent, pcount, pname, pstatus) in cur.fetchall() :
        if pcount == 0 :
            continue
        articles.append({
            "pname": pname,
            "ptitle": ptitle,
            "pdate": pdate,
            "pcount": pcount
        })
        if "closed" in pstatus :
            print >> sys.stderr, "comments for %s are closed... skipping" % ptitle
            if force != True :
                continue

        # Print article
        comments = []
        getcomments(comments, pid, 0, 0, pname)
        ctx_article = {
            "title": ptitle,
            "gentime": time.strftime("%c"),
            "pname": pname,
            "ptitle": ptitle,
            "pdate": pdate,
            "pcontent": pcontent,
            "pcount": pcount,
            "comments": comments
        }
        render_template("archivearticle.mako", ctx_article, "%s.html" % pname)

    ctx_index = {
        "title": "Index Archive",
        "gentime": time.strftime("%c"),
        "total_articles": len(articles),
        "articles": articles
    }
    
    render_template("archiveindex.mako", ctx_index, "today.html" if today else "index.html")


def getcomments(comments, post, cid, indent, pname) :
    global db

    indent += 1

    cur = db.cursor()
    try:
        if (cid == 0) :
            sql = "select comment_id, comment_date, comment_author, comment_content, comment_parent, comment_author, comment_agent from avwp_comments where comment_post_ID=%s and comment_parent=%s order by comment_date desc" % (post, cid)
        else :
            sql = "select a.comment_id, a.comment_date, a.comment_author, a.comment_content, a.comment_parent, b.comment_author, a.comment_agent from avwp_comments a, avwp_comments b where a.comment_post_id=%s and a.comment_parent=%s and b.comment_id=%s order by comment_date desc" % (post, cid, cid)
        cur.execute(sql)
    except:
        print "Error ", sql
        return

    for (cid, cdate, cauthor, ccontent, cparent, cpauthor, cagent) in cur.fetchall() :
        try:
            _, disqid = cagent.split(":")
        except ValueError:
            disqid = "0"
            
        comments.append({
            "margin": 20 * indent,
            "cpauthor": cpauthor,
            "cauthor": cauthor,
            "disqid": disqid,
            "cdate": cdate,
            "ccontent": ccontent
        })
        getcomments(comments, post, cid, indent, pname)


def debug_query() :
    global db

    cur = db.cursor()
    try:
        sql = "select comment_id, comment_date, comment_author, comment_content, comment_parent, comment_author, comment_agent from avwp_comments where comment_author like 'Erni%'"
        cur.execute(sql)
    except:
        print "Error ", sql
        return

    for (cid, cdate, cauthor, ccontent, cparent, cpauthor, cagent) in cur.fetchall() :
        print cauthor.encode('utf-8')
        break ;

#------------------------------------------------------------
# File and printing utilities

def createfile(file) :
    import os.path
    global directory

    if not os.path.exists(directory):
       os.makedirs(directory)

    file = os.path.join(directory, file)

    findex = codecs.open(file, encoding='utf-8', mode='w')
    return findex

def renameindexfile(oldname, newname):
    import os.path
    global directory

    if not os.path.exists(directory):
       os.makedirs(directory)

    oldname = os.path.join(directory, oldname)
    newname = os.path.join(directory, newname)

    try:
        os.rename(oldname, newname)
    except:
        print >> sys.stderr, "Cannot rename"

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

    ## Connection
    #dbconnect(options.database, options.user, options.password)

    #if debug :
        #print Version
        ##debug_query()
        ##sys.exit()

    ## Process articles and from them comments
    #getarticle()
    
    hookiifier(options.user, options.password, options.database, today)

if __name__ == '__main__':
    main()
