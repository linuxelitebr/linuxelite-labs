#!/usr/bin/env python3
"""Safe login: a parameterized query. The driver treats the input as data,
never as SQL.

Feed it the same  ' OR 1=1 --  and it looks for a user literally named
" ' OR 1=1 -- ", finds nobody, and rejects the login.

    python3 safe_login.py <username> <password>
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
    # THE FIX: placeholders. The values are bound as data, not parsed as SQL.
    sql = "SELECT id, username FROM users WHERE username = ? AND password = ?"
    print("  query: ", sql)
    print("  params:", (username, password))
    return con.execute(sql, (username, password)).fetchone()


def main():
    if len(sys.argv) != 3:
        print("usage: python3 safe_login.py <username> <password>")
        sys.exit(2)
    row = login(make_db(), sys.argv[1], sys.argv[2])
    if row:
        print("  LOGGED IN as id=%s username=%s" % (row[0], row[1]))
    else:
        print("  login rejected")


if __name__ == "__main__":
    main()
