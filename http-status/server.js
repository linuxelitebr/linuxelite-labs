// HTTP status-code lab: each endpoint returns the RFC-correct status WITH the header the RFC
// requires. Plain Node, zero dependencies. The point is the status line and the headers, so
// read them with curl -i (or curl -sD -).
//
//   node server.js
//   curl -sD - -o /dev/null http://localhost:8080/needs-auth
//
// Bodies use application/problem+json (RFC 9457): the JSON "status" matches the real HTTP status,
// so generic HTTP software that ignores the body still behaves correctly.

const http = require('http');
const PORT = process.env.PORT || 8080;

function send(res, status, headers, title, detail) {
  const body = JSON.stringify({ type: 'about:blank', title, status, detail });
  res.writeHead(status, Object.assign({}, headers, { 'Content-Type': 'application/problem+json' }));
  res.end(body + '\n');
}

const server = http.createServer((req, res) => {
  const path = req.url.split('?')[0];

  switch (path) {
    case '/':
      res.writeHead(200, { 'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'no-store' });
      return res.end(
        'http-status lab\n\n' +
        '/needs-auth   -> 401 + WWW-Authenticate\n' +
        '/forbidden    -> 403\n' +
        '/hidden       -> 404 (hides a forbidden resource)\n' +
        '/only-get     -> 405 + Allow on non-GET\n' +
        '/via-proxy    -> 407 + Proxy-Authenticate\n' +
        '/bad-request  -> 400\n' +
        '/ok           -> 200\n\n' +
        'try: curl -sD - -o /dev/null http://localhost:' + PORT + '/needs-auth\n');

    case '/needs-auth':
      // No valid credential -> 401. The RFC MUST: a WWW-Authenticate challenge.
      return send(res, 401, { 'WWW-Authenticate': 'Bearer' },
        'Authentication required', 'No valid credential. Send a bearer token.');

    case '/forbidden':
      // Understood, refused. No WWW-Authenticate. Retrying the same credential will not help.
      return send(res, 403, {},
        'Forbidden', 'Understood, but refused. Retrying with the same credential will not help.');

    case '/hidden':
      // A forbidden resource whose existence is sensitive -> indistinguishable 404 (RFC 9110 15.5.4 MAY).
      return send(res, 404, {},
        'Not Found', 'Existence hidden on the authorization boundary.');

    case '/only-get':
      if (req.method !== 'GET') {
        // Resource exists but does not support this method -> 405 + Allow MUST.
        return send(res, 405, { 'Allow': 'GET, OPTIONS' },
          'Method Not Allowed', 'This resource only supports GET.');
      }
      res.writeHead(200, { 'Content-Type': 'text/plain; charset=utf-8' });
      return res.end('ok, this is a GET-only resource (try: curl -X POST)\n');

    case '/via-proxy':
      // 407 comes from a proxy in the path, never from an origin's own access control.
      return send(res, 407, { 'Proxy-Authenticate': 'Basic realm="lab-proxy"' },
        'Proxy Authentication Required', 'A proxy in the path demands authentication.');

    case '/bad-request':
      // Malformed syntax/framing/routing. NOT a bucket for auth failures.
      return send(res, 400, {},
        'Bad Request', 'Malformed request. Not a bucket for auth failures.');

    case '/ok':
      res.writeHead(200, { 'Content-Type': 'text/plain; charset=utf-8' });
      return res.end('ok\n');

    default:
      return send(res, 404, {}, 'Not Found', 'No such endpoint.');
  }
});

server.listen(PORT, () => console.log(`http-status lab up at http://localhost:${PORT}`));
