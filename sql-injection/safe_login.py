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
    con.execute("CREATE TABLE usuarios (id INTEGER PRIMARY KEY, usuario TEXT, senha TEXT)")
    con.executemany(
        "INSERT INTO usuarios (usuario, senha) VALUES (?, ?)",
        [("admin", "s3nh4-do-admin"), ("alice", "secret")],
    )
    con.commit()
    return con


def login(con, usuario, senha):
    # THE FIX: placeholders. The values are bound as data, not parsed as SQL.
    sql = "SELECT id, usuario FROM usuarios WHERE usuario = ? AND senha = ?"
    print("  query: ", sql)
    print("  params:", (usuario, senha))
    return con.execute(sql, (usuario, senha)).fetchone()


def main():
    if len(sys.argv) != 3:
        print("usage: python3 safe_login.py <username> <password>")
        sys.exit(2)
    row = login(make_db(), sys.argv[1], sys.argv[2])
    if row:
        print("  LOGGED IN as id=%s usuario=%s" % (row[0], row[1]))
    else:
        print("  login rejected")


if __name__ == "__main__":
    main()
