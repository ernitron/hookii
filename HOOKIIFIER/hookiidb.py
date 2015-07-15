#!/usr/bin/python

from __future__ import print_function
import sys
import logging

import MySQLdb as mysql
import MySQLdb.cursors


class HookiiDB:
    db = None

    def __init__(self, user, password, database):
        self.logger = logging.getLogger(__name__)
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
        except mysql.Error as e:
            self.logger.critical("MySQL Error [%d]: %s", e.args[0], e.args[1])
            sys.exit()

    def __del__(self):
        if self.db is not None:
            self.db.close()

    def _executeQuery(self, query, args=None):
        self.logger.debug("query = %s", query)
        self.logger.debug("args = %s", args)
        with self.db as cur:
            try:
                cur.execute(query, args)
                return cur.fetchall()
            except mysql.DatabaseError as e:
                self.logger.critical("MySQL Error [%d]: %s", e.args[0], e.args[1])
                sys.exit()
            finally:
                cur.close()

    def get_posts(self,
                  post_date_min=None,
                  post_date_max=None,
                  only_published=False,
                  only_with_comments=False,
                  only_open=False):
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

        if only_published:
            filters.append("post_status = 'publish'")

        if only_with_comments:
            filters.append("comment_count > 0")

        if only_open:
            filters.append("comment_status = 'open'")

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

    def exists_older_post(self, date):
        query = """
            SELECT EXISTS (
                SELECT 1
                FROM avwp_posts
                WHERE post_date <= %s
            ) AS exists_older_post;
        """
        r = self._executeQuery(query, (date,))
        for re in r:
            return re.get("exists_older_post", 0)

    def min_post_date(self, only_published=False, only_with_comments=False):
        query = """
            SELECT MIN(post_date) AS min_post_date
            FROM avwp_posts
            %s
        """

        filters = []

        if only_published:
            filters.append("post_status = 'publish'")

        if only_with_comments:
            filters.append("comment_count > 0")

        clause = "WHERE " + " AND ".join(filters) if len(filters) > 0 else ""

        r = self._executeQuery(query % clause)
        for re in r:
            return re.get("min_post_date", None)

    def get_posts_with_new_comments(self,
                                    comment_date_min,
                                    only_published=False,
                                    only_open=False):
        query = """
            SELECT p.id,
                p.post_date,
                p.post_author,
                p.post_title,
                p.post_content,
                p.comment_count,
                p.post_name,
                p.comment_status
            FROM avwp_posts AS p
            %s
            ORDER BY p.post_date ASC
        """

        filters = []

        if only_published:
            filters.append("p.post_status = 'publish'")

        if only_open:
            filters.append("p.comment_status = 'open'")

        clause = """INNER JOIN (
                        SELECT DISTINCT(comment_post_ID)
                        FROM avwp_comments
                        WHERE comment_date > %(comment_date_min)s
                    ) AS cp
                    ON p.id = cp.comment_post_ID
                    WHERE """ + " AND ".join(filters) if len(filters) > 0 else ""

        args = {
            "comment_date_min": comment_date_min
        }

        return self._executeQuery(query % clause, args)

    def get_comments_of_posts_with_new_comments(self, comment_date_min):
        query = """
            SELECT c.comment_id,
                c.comment_date,
                c.comment_author,
                c.comment_content,
                c.comment_parent,
                c.comment_agent,
                c.comment_post_ID
            FROM avwp_comments AS c
            INNER JOIN (
                SELECT DISTINCT(comment_post_ID)
                FROM avwp_comments
                WHERE comment_date > %(comment_date_min)s
            ) AS cp
            ON c.comment_post_ID = cp.comment_post_ID
            ORDER BY c.comment_date ASC
        """

        args = {
            "comment_date_min": comment_date_min
        }

        return self._executeQuery(query, args)
