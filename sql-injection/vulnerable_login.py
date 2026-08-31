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
    con.execute("CREATE TABLE usuarios (id INTEGER PRIMARY KEY, usuario TEXT, senha TEXT)")
    con.executemany(
        "INSERT INTO usuarios (usuario, senha) VALUES (?, ?)",
        [("admin", "s3nh4-do-admin"), ("alice", "secret")],
    )
    con.commit()
    return con


def login(con, usuario, senha):
    # THE BUG: user input goes straight into the query string.
    sql = "SELECT id, usuario FROM usuarios WHERE usuario = '%s' AND senha = '%s'" % (usuario, senha)
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
        print("  LOGGED IN as id=%s usuario=%s" % (row[0], row[1]))
    else:
        print("  login rejected")


if __name__ == "__main__":
    main()
