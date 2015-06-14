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
libs = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(libs)
from utils import *

# Globals
debug = False
force = False
today = False
db = None
directory = "/tmp/originals"

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

    if today :
        findex = createfile("today.workinprogress.html")
    else:
        findex = createfile("index.workinprogress.html")

    print_index_head(findex)

    # print all the articles
    for (pid, pdate, pauthor, ptitle, pcontent, pcount, pname, pstatus) in cur.fetchall() :
        if pcount == 0 :
            continue
        print_article_into_index(findex, ptitle, pdate, pcount, pname)
        if "closed" in pstatus :
            print >> sys.stderr, "comments for %s are closed... skipping" % ptitle
            if force != True :
                continue

        # Print article
        farticle = createfile('%s.html' % pname)
        print_article(farticle, ptitle, pdate, pcontent, pcount, pname)
        getcomments(farticle, pid, 0, 0, pname)
        print_article_close(farticle)

    print_index_close(findex)
    if today :
        renameindexfile("today.workinprogress.html", "today.html")
    else :
        renameindexfile("index.workinprogress.html", "index.html")


def getcomments(f, post, cid, indent, pname) :
    global db

    indent += 1
    post = int(post)
    cid = int(cid)

    cur = db.cursor()
    try:
        if (cid == 0) :
            sql = "select comment_id, comment_date, comment_author, comment_content, comment_parent, comment_author, comment_agent from avwp_comments where comment_post_ID=%d and comment_parent=%d order by comment_date desc" % (post, cid)
        else :
            sql = "select a.comment_id, a.comment_date, a.comment_author, a.comment_content, a.comment_parent, b.comment_author, a.comment_agent from avwp_comments a, avwp_comments b where a.comment_post_id=%d and a.comment_parent=%d and b.comment_id=%d order by comment_date desc" % (post, cid, cid)
        cur.execute(sql)
    except:
        print "Error ", sql
        return

    for (cid, cdate, cauthor, ccontent, cparent, cpauthor, cagent) in cur.fetchall() :
        print_comment(f, indent, cdate, cauthor, ccontent, cpauthor, cagent, pname )
        getcomments(f, post, cid, indent, pname)


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


def print_head(f, title) :
    print >> f, u'''<html>
<head>
<title>%s</title>
 <meta name="generator" content="hookiifier">
 <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
 <meta name="robots" content="index, follow">
 <meta name="keywords" content="commenti, liberi, lettori, automoderazione, commenti giornali online, community, mhookii">
 <meta name="description" content="%s">
 <style>
    body { font-family: Georgia, serif; font-size: 1.0rem; color: #444; }
    p { font-family: Georgia, serif; font-size: 1.0rem; color: #444; }
    h1 { font-family: Georgia, serif; color: #336699; }
    h2 { font-family: Georgia, serif; color: #336699; }
    h3 { font-family: Georgia, serif; color: #336699; }
    a { font-family: Georgia, serif; color: #336699; text-decoration: None; }
    .col1 { width: 500px; display: inline-block; }
    .col2 { width: 200px; display: inline-block; }
    .col3 { width: 100px; text-align: right; display: inline-block; }
    #article { width: 650px; text-align: justify }
    #header { background-color: #336699; color: white; font-size: 1.5rem; text-align: left; line-height: 3em; }
    #footer { background-color: #336699; color: white; font-size: 0.7rem; text-align: left; line-height: 3em; }
    @media (min-width:320px) { /* smartphones, iPhone, portrait 480x320 phones */ }
    @media (min-width:481px) { /* portrait e-readers (Nook/Kindle), smaller tablets @ 600 or @ 640 wide. */ }
    @media (min-width:641px) { /* portrait tablets, portrait iPad, landscape e-readers, landscape 800x480 or 854x480 phones */ }
    @media (min-width:961px) { /* tablet, landscape iPad, lo-res laptops ands desktops */ }
    @media (min-width:1025px) { /* big landscape tablets, laptops, and desktops */ }
    @media (min-width:1281px) { /* hi-res laptops and desktops */ }
</style>
 </style>
</head>
<body>
<div id="header">
<h1><a href='http://www.hookii.it/' style='text-decoration: none; color: white;'>Hookii</a>
<a href='http://www.hookii.it/archived' style='text-decoration: none; color: white;'> Archive </a>
<font size='4' style='color: white'><i>Yes, we post!</font></i></a></h1>
</div>
''' % (title, title)

def print_article(f, ptitle, pdate, pcontent, pcount, pname):
        print_head(f, ptitle)
        print >> f, "<div id='article'>"
        print >> f, "<h2 style='margin-bottom:0.1em'><a href='http://www.hookii.it/%s'>" % pname, ptitle , "</a></h2>"
        print >> f, "<p style='margin-top:0.1em'><font size='2'>Articolo comparso il " , pdate
        print >> f, "su <a href='http://www.hookii.it/%s/'>hookii</a>.</font><br />" % pname
        #pcontent = embed_image(pcontent)
        pcontent = embed_youtube(pcontent)
        #pcontent = embed_all(pcontent)
        pcontent = "<br />".join(pcontent.split("\n"))
        print >> f, "<p>", pcontent , "</p>"
        print >> f, "Vai all'articolo <a href='http://www.hookii.it/%s'>" % pname, pname , "</a> per commentare</p>"
        print >> f, '</div>'
        print >> f, '<hr>'
        #--------------------------------------
        if pcount > 1 : com = "commenti"
        elif pcount == 1 : com = "commento"
        else : com = "No comments"
        print >> f, "<h2>" , pcount , com , "</h2>"

def print_index_head(f) :
    print_head(f, "Index Archive")
    print >> f, "<span class='col1'>Articolo</span>"
    print >> f, "<span class='col2'>Pubblicato il</span>"
    print >> f, "<span class='col3'>Commenti</span>"
    print >> f, "<br />"

print_article_into_index_counter = 0
def print_article_into_index(f, ptitle, pdate, pcount, pname):
    global print_article_into_index_counter

    print_article_into_index_counter += 1

    article = "<a href='"+ pname + ".html'>" + ptitle + "</a>"
    print >> f, "<span class='col1'>%s</span>" % article
    print >> f, "<span class='col2'>%s</span>" % pdate
    print >> f, "<span class='col3'><b>%s</b></span>" % pcount
    print >> f, "<br />"


def print_index_close(f) :
    global print_article_into_index_counter

    print >> f, "<span class='col1'><b>%d Total articles archived </b></span>" % print_article_into_index_counter
    print >> f, "<span class='col2'></span>"
    print >> f, "<span class='col3'></span>"
    print >> f, "<br />"
    print_footer(f)

def print_article_close(f) :
    print_footer(f)

def print_footer(f) :
    now = time.strftime("%c")
    ## date and time representation
    print >> f, '<div id="footer">'
    print >> f, "<a href='http://www.hookii.it/' style='color: white;'>Hookii</a>"
    print >> f, 'Dookii productions &copy; 2014 - Generated on ' + time.strftime("%c")
    print >> f, '</div>'
    print >> f, '</body></html>'
    f.close()


def print_comment(f, indent, cdate, cauthor, ccontent, cpauthor, cagent, pname) :

    try: 
       disqus,disqid = cagent.split(':')
    except:
       disqid = '0'
 
    w = indent * 20
    print >> f, '<div style="margin-left:%dpx; margin-right:-%dx; width:600px;">' % (w, w)
    #timestamp = datetimestr_to_timestamp(repr(cdate))
    #nickname = normalized_nickname(cauthor)
    #url_tag =  "<a href='http://www.hookii.it/%s#%s%d'>" % (pname, "" if nickname is None else nickname, timestamp)
    url_tag =  "<a href='http://www.hookii.it/%s/#comment-%s'>" % (pname, disqid)
    if (cauthor == cpauthor) :
       print >> f, "<h3>", url_tag, cauthor, "- <font size='2'>", cdate, "</font></a></h3>"
    else :
       print >> f, "<h3>", url_tag, cauthor, "@ %s" % cpauthor, "- <font size='2'>", cdate, "</font></a></h3>"

    #ccontent = embed_image(ccontent)
    ccontent = embed_all(ccontent)
    ccontent = "<br />".join(ccontent.split("\n"))
    print >> f, "<p>", ccontent, "</p> "
    print >> f, "<hr>"
    print >> f, "</div>"

pattern_url = ""
pattern_youtube = ""
pattern_image = ""

def embed_init() :
    global pattern_url
    global pattern_youtube
    global pattern_image

    pattern = r"""(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>\[\]]+|\(([^\s()<>\[\]]+|(\([^\s()<>\[\]]+\)))*\))+(?:\(([^\s()<>\[\]]+|(\([^\s()<>\[\]]+\)))*\)|[^\s`!(){};:'".,<>?\[\]]))"""
    pattern_url = re.compile(pattern, re.MULTILINE)
    pattern = '(https?:\/\/.*\.(?:png|jpg|gif|jpeg))'
    pattern_image = re.compile(pattern, re.MULTILINE)
    pattern = '(http.{0,1}://www.youtube.com/)watch\?.*v=(...........)'
    pattern_youtube = re.compile(pattern, re.MULTILINE)

def embed_url(originalstring) :
    replacement_string='<a href="\\1">\\1</a>'
    string = pattern_url.sub(replacement_string, originalstring)

    return string

def embed_image(originalstring) :
    replacement_string='<img src="\\1" width="420">'
    string = pattern_image.sub(replacement_string, originalstring)

    return string

def embed_youtube(originalstring) :
    replacement_string='<embed width="420" height="315" src="\\1v/\\2">'
    string = pattern_youtube.sub(replacement_string, originalstring)
    return string

def embed_all(originalstring) :
    replacement_string='<embed width="420" height="315" src="\\1v/\\2">'
    string = pattern_youtube.sub(replacement_string, originalstring)
    if string == originalstring :
        replacement_string='<img src="\\1" width="420">'
        string = pattern_image.sub(replacement_string, originalstring)
        #if string == originalstring :
        #    replacement_string='<a href="\\1">\\1</a>'
        #    string = pattern_url.sub(replacement_string, originalstring)

    return string


#------------------------------------------------------------
# Main finally
if __name__ == '__main__':

    import optparse
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

