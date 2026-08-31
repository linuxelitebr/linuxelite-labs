<?php
// Vulnerable login: the query is built by concatenating user input.
// The classic PHP/PDO anti-pattern. Run:
//   php vulnerable_login.php "' OR 1=1 --" ""
$pdo = new PDO('sqlite::memory:');
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_SILENT);
$pdo->exec("CREATE TABLE usuarios (id INTEGER PRIMARY KEY, usuario TEXT, senha TEXT)");
$pdo->exec("INSERT INTO usuarios (usuario, senha) VALUES ('admin', 's3nh4-do-admin'), ('alice', 'secret')");

$usuario = $argv[1] ?? '';
$senha   = $argv[2] ?? '';

// THE BUG: user input goes straight into the query string.
$sql = "SELECT id, usuario FROM usuarios WHERE usuario = '$usuario' AND senha = '$senha'";
echo "  query: $sql\n";

$stmt = $pdo->query($sql);
$row = $stmt ? $stmt->fetch(PDO::FETCH_ASSOC) : false;
echo $row
    ? "  LOGGED IN as id={$row['id']} usuario={$row['usuario']}\n"
    : "  login rejected\n";
