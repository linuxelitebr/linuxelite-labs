#!/usr/bin/env python3
"""Vulnerable login: the SQL is built by concatenating user input.

This is the anti-pattern. Feed it  ' OR 1=1 --  as the username and it walks
right in as the first row (the admin), no password needed. The fix lives in
safe_login.py.

    python3 vulnerable_login.py <username> <password>
"""
import sqlite3
import sys


def make_db():
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    con.executemany(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        [("admin", "s3cr3t-admin-pw"), ("alice", "secret")],
    )
    con.commit()
    return con


def login(con, username, password):
    # THE BUG: user input goes straight into the query string.
    sql = "SELECT id, username FROM users WHERE username = '%s' AND password = '%s'" % (username, password)
    print("  query:", sql)
    try:
        return con.execute(sql).fetchone()
    except sqlite3.Error as exc:
        print("  SQL error:", exc)
        return None


def main():
    if len(sys.argv) != 3:
        print("usage: python3 vulnerable_login.py <username> <password>")
        sys.exit(2)
    row = login(make_db(), sys.argv[1], sys.argv[2])
    if row:
        print("  LOGGED IN as id=%s username=%s" % (row[0], row[1]))
    else:
        print("  login rejected")


if __name__ == "__main__":
    main()
