<?php
// Safe login: a prepared statement. The driver binds the values as data,
// so the injection is looked up as a literal username and found nowhere. Run:
//   php safe_login.php "' OR 1=1 --" ""
$pdo = new PDO('sqlite::memory:');
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_SILENT);
$pdo->exec("CREATE TABLE usuarios (id INTEGER PRIMARY KEY, usuario TEXT, senha TEXT)");
$pdo->exec("INSERT INTO usuarios (usuario, senha) VALUES ('admin', 's3nh4-do-admin'), ('alice', 'secret')");

$usuario = $argv[1] ?? '';
$senha   = $argv[2] ?? '';

// THE FIX: placeholders. execute() binds the values as data, never as SQL.
$stmt = $pdo->prepare('SELECT id, usuario FROM usuarios WHERE usuario = ? AND senha = ?');
$stmt->execute([$usuario, $senha]);
$row = $stmt->fetch(PDO::FETCH_ASSOC);

echo "  query:  SELECT id, usuario FROM usuarios WHERE usuario = ? AND senha = ?\n";
echo "  params: [" . var_export($usuario, true) . ", " . var_export($senha, true) . "]\n";
echo $row
    ? "  LOGGED IN as id={$row['id']} usuario={$row['usuario']}\n"
    : "  login rejected\n";
