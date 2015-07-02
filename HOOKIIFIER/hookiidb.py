#!/usr/bin/python

import sys

import MySQLdb as mysql
import MySQLdb.cursors


class HookiiDB:
    db = None

    def __init__(self, user, password, database):
        try:
            self.db = mysql.connect(
                host="localhost",
                user=user,
                passwd=password,
                db=database,
                charset="utf8",
                use_unicode=True,
                cursorclass=MySQLdb.cursors.DictCursor
            )
        except mysql.Error, e:
            print >> sys.stderr, "Error opening db", e
            sys.exit()

    def __del__(self):
        self.db.close()

    def _executeQuery(self, query, args=None):
        with self.db as cur:
            try:
                cur.execute(query, args)
                return cur.fetchall()
            except mysql.DatabaseError, e:
                print >> sys.stderr, "Error: ", e
                print >> sys.stderr, "\tquery: ", query
                return
            finally:
                cur.close()

    def get_posts(self):
        query = """
            SELECT id,
                   post_author,
                   post_date,
                   post_title,
                   post_content,
                   post_name,
                   comment_count,
                   comment_status
            FROM avwp_posts
            ORDER BY post_date ASC;
        """
        return self._executeQuery(query)

    def get_comments(self):
        query = """
            SELECT comment_id,
                   comment_date,
                   comment_author,
                   comment_content,
                   comment_parent,
                   comment_agent,
                   comment_post_ID
            FROM avwp_comments
            ORDER BY comment_date ASC
        """
        return self._executeQuery(query)
