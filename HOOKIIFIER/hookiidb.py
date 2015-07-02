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

    def get_posts(self, post_date_min=None, post_date_max=None):
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
            %s
            ORDER BY post_date ASC;
        """
        
        filters = []
            
        if post_date_min is not None:
            filters.append("post_date > %(post_date_min)s")

        if post_date_max is not None:
            filters.append("post_date <= %(post_date_max)s")

        clause = "WHERE " + " AND ".join(filters) if len(filters) > 0 else ""

        args = {
            "post_date_min": post_date_min,
            "post_date_max": post_date_max,
        }
        
        return self._executeQuery(query % clause, args)

    def get_comments(self, post_date_min=None, post_date_max=None):
        query = """
            SELECT comment_id,
                   comment_date,
                   comment_author,
                   comment_content,
                   comment_parent,
                   comment_agent,
                   comment_post_ID
            FROM avwp_comments
            %s
            ORDER BY comment_date ASC
        """
        
        filters = []
            
        if post_date_min is not None:
            filters.append("post_date > %(post_date_min)s")

        if post_date_max is not None:
            filters.append("post_date <= %(post_date_max)s")

        clause = """
            INNER JOIN avwp_posts AS p
            ON p.ID = comment_post_ID
            WHERE """ + " AND ".join(filters) if len(filters) > 0 else ""

        args = {
            "post_date_min": post_date_min,
            "post_date_max": post_date_max,
        }
        
        return self._executeQuery(query % clause, args)

    def exist_older_posts(self, date):
        query = """
            SELECT EXISTS (
                SELECT 1
                FROM avwp_comments
                WHERE comment_date <= %s
            ) AS older_posts;
        """
        r = self._executeQuery(query, (date,))
        for re in r:
            return re.get("older_posts", 0)
