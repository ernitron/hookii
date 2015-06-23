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
import time
import re
import codecs
import optparse
import pkg_resources
from mako.template import Template
from mako.lookup import TemplateLookup
from mako.runtime import Context
#libs = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__))))
#sys.path.append(libs)
#from utils import *

# Globals
debug = False
force = False
today = False
db = None
directory = "/tmp/originals"
templatelookup = TemplateLookup(directories=[pkg_resources.resource_filename(__name__, "templates")])

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
            "pcontent": pcontent.split("\n"),
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
        comments.append({
            "margin": 20 * indent,
            "cpauthor": cpauthor,
            "cauthor": cauthor,
            "disqid": cagent,
            "cdate": cdate,
            "ccontent": embed_all(ccontent)
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

def render_template(template, context, outfile):
    with createfile(outfile) as f:
        ctx = Context(f, **context)
        t = templatelookup.get_template(template)
        t.render_context(ctx)
        f.close()


pattern_url = ""
pattern_youtube = ""
pattern_image = ""

def embed_init() :
    global pattern_url
    global pattern_youtube
    global pattern_image

    #pattern = r"""(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>\[\]]+|\(([^\s()<>\[\]]+|(\([^\s()<>\[\]]+\)))*\))+(?:\(([^\s()<>\[\]]+|(\([^\s()<>\[\]]+\)))*\)|[^\s`!(){};:'".,<>?\[\]]))"""
    pattern = '''((https?:\/\/)([\da-z\.-]+)\.([a-z\.]{2,6})([\/\?=#&%;\w \.-]*)*\/?)'''
    pattern_url = re.compile(pattern, re.MULTILINE)

    pattern = '(https?:\/\/.*\.(?:png|jpg|gif|jpeg|JPG|JPEG|GIF|PNG)(?:\?\S+)?)'
    pattern_image = re.compile(pattern, re.MULTILINE)

    pattern = '(https?://www.youtube.com/)watch\?.*v=(...........)'
    pattern_youtube = re.compile(pattern, re.MULTILINE)


def embed_url(originalstring) :
    replacement_string='<a href="\\1">\\1</a>'
    string = pattern_url.sub(replacement_string, originalstring)

    return string

def embed_image(originalstring) :
    replacement_string='<img src="\\1" class="w3-image">'
    string = pattern_image.sub(replacement_string, originalstring)

    return string

def embed_youtube(originalstring) :
    replacement_string='<embed width="420" height="315px" src="\\1v/\\2">'
    string = pattern_youtube.sub(replacement_string, originalstring)
    return string

def embed_all(originalstring) :
    replacement_string='<embed width="420" height="315px" src="\\1v/\\2">'
    string = pattern_youtube.sub(replacement_string, originalstring)
    if string == originalstring :
        replacement_string='<img src="\\1" width="420px">'
        string = pattern_image.sub(replacement_string, originalstring)
        if string == originalstring :
            replacement_string='<a href="\\1" target="_blank">\\1</a>'
            string = pattern_url.sub(replacement_string, originalstring)

    return string


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

    cssfile = os.path.join(directory, 'html5.css')
    if os.path.isfile(cssfile) == False:
       print "Stylesheet file not found ", cssfile, " Please install"
       sys.exit()
        

    # Start patterns for substitutions
    embed_init()

    # Connection
    dbconnect(options.database, options.user, options.password)

    if debug :
        print Version
        #debug_query()
        #sys.exit()

    # Process articles and from them comments
    getarticle()

if __name__ == '__main__':
    main()
