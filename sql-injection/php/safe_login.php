<?php
// Safe login: a prepared statement. The driver binds the values as data,
// so the injection is looked up as a literal username and found nowhere. Run:
//   php safe_login.php "' OR 1=1 --" ""
$pdo = new PDO('sqlite::memory:');
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_SILENT);
$pdo->exec("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)");
$pdo->exec("INSERT INTO users (username, password) VALUES ('admin', 's3cr3t-admin-pw'), ('alice', 'secret')");

$username = $argv[1] ?? '';
$password = $argv[2] ?? '';

// THE FIX: placeholders. execute() binds the values as data, never as SQL.
$stmt = $pdo->prepare('SELECT id, username FROM users WHERE username = ? AND password = ?');
$stmt->execute([$username, $password]);
$row = $stmt->fetch(PDO::FETCH_ASSOC);

echo "  query:  SELECT id, username FROM users WHERE username = ? AND password = ?\n";
echo "  params: [" . var_export($username, true) . ", " . var_export($password, true) . "]\n";
echo $row
    ? "  LOGGED IN as id={$row['id']} username={$row['username']}\n"
    : "  login rejected\n";
