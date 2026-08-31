# SQL injection: login bypass, and the actual fix

A tiny, dependency-free lab that shows the classic `' OR 1=1 --` authentication
bypass working against a concatenated query, and shrugged off by a parameterized
one. Same input, two outcomes. That is the whole point.

Companion to the article (PT-BR):
[SQL Injection na prática: como o `' OR 1=1` faz bypass de login](https://linuxelite.com.br/pt/blog/sql-injection-bypass-autenticacao/),
which also has an interactive dissector where you can type payloads and watch the
query change.

## What is here

```
vulnerable_login.py   # login that concatenates user input into the SQL (the bug)
safe_login.py         # same login with a parameterized query (the fix)
demo.sh               # runs both, with a normal login and with the payload
php/vulnerable_login.php
php/safe_login.php     # the classic PHP/PDO pair, same story
```

Both logins seed an in-memory SQLite database with two users (`admin`, `alice`)
and try to authenticate. No install, no server, no network.

## Run it

Python (standard library only, needs Python 3):

```bash
python3 vulnerable_login.py "' OR 1=1 --" ""
python3 safe_login.py       "' OR 1=1 --" ""
```

Or the whole story at once:

```bash
bash demo.sh
```

PHP (needs the `php` CLI with PDO SQLite, bundled in most PHP builds):

```bash
php php/vulnerable_login.php "' OR 1=1 --" ""
php php/safe_login.php       "' OR 1=1 --" ""
```

## What you will see

The vulnerable login builds this query:

```sql
SELECT id, usuario FROM usuarios WHERE usuario = '' OR 1=1 --' AND senha = ''
```

The `OR 1=1` makes the `WHERE` true for every row and the `--` comments out the
password check. It returns the whole table and logs you in as the first row, the
admin. Try `admin' --` too: it comments out the password check and logs you in as
that specific user.

The safe login runs `... WHERE usuario = ? AND senha = ?` and binds your input as
data. It looks for a user literally named `' OR 1=1 --`, finds nobody, and rejects
the login. Feed it a real password and it works; feed it a payload and it does not.

## The point

Prepared statements (parameterized queries) are the fix, and the first of OWASP's
primary defenses. The database is handed the query structure and the data
separately, so input can never change the query's meaning.

Manual escaping is not the fix. OWASP labels it "strongly discouraged": it is
charset-dependent and bypassable, and `mysqli_real_escape_string` is not a
substitute for a prepared statement. Least privilege, an ORM, and a WAF are layers
on top, not the correction.

## Sources

- [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [PortSwigger: SQL injection](https://portswigger.net/web-security/sql-injection)
- [PHP: PDO Prepared Statements](https://www.php.net/manual/en/pdo.prepared-statements.php)
- [Python: sqlite3](https://docs.python.org/3/library/sqlite3.html)
