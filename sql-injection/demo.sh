#!/usr/bin/env bash
# Runs both logins with a normal credential and with the ' OR 1=1 -- payload,
# so you can watch one fall over and the other hold the line.
set -e
cd "$(dirname "$0")"

echo "=== Normal login (alice / secret) ==="
echo "-- vulnerable:"; python3 vulnerable_login.py "alice" "secret"
echo "-- safe:";       python3 safe_login.py "alice" "secret"
echo

echo "=== Attack 1: ' OR 1=1 -- in the username, empty password ==="
echo "-- vulnerable (walks in as admin):"; python3 vulnerable_login.py "' OR 1=1 --" ""
echo "-- safe (rejected):";                python3 safe_login.py "' OR 1=1 --" ""
echo

echo "=== Attack 2: admin' -- (comment out the password check) ==="
echo "-- vulnerable:"; python3 vulnerable_login.py "admin' --" ""
echo "-- safe:";       python3 safe_login.py "admin' --" ""
echo

echo "=== Sanity: right user, wrong password (both reject) ==="
echo "-- vulnerable:"; python3 vulnerable_login.py "alice" "wrong"
echo "-- safe:";       python3 safe_login.py "alice" "wrong"
