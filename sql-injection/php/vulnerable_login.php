<?php
// Vulnerable login: the query is built by concatenating user input.
// The classic PHP/PDO anti-pattern. Run:
//   php vulnerable_login.php "' OR 1=1 --" ""
$pdo = new PDO('sqlite::memory:');
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_SILENT);
$pdo->exec("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)");
$pdo->exec("INSERT INTO users (username, password) VALUES ('admin', 's3cr3t-admin-pw'), ('alice', 'secret')");

$username = $argv[1] ?? '';
$password = $argv[2] ?? '';

// THE BUG: user input goes straight into the query string.
$sql = "SELECT id, username FROM users WHERE username = '$username' AND password = '$password'";
echo "  query: $sql\n";

$stmt = $pdo->query($sql);
$row = $stmt ? $stmt->fetch(PDO::FETCH_ASSOC) : false;
echo $row
    ? "  LOGGED IN as id={$row['id']} username={$row['username']}\n"
    : "  login rejected\n";
