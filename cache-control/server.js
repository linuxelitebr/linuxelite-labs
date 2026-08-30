// Origin server to demonstrate Cache-Control. Plain Node, zero dependencies.
// Each endpoint emits a different Cache-Control header and a body with a timestamp,
// so that behind a shared cache (Varnish) you can tell what was served from cache and
// what came fresh from the origin.
//
//   node server.js
//   curl -sI http://localhost:8080/mixed
//
// There is no error handling on purpose: the point here is the header, not the server.

const http = require('http');

const PORT = process.env.PORT || 8080;
let counter = 0;

// endpoint -> the Cache-Control header it emits
const ROUTES = {
  '/static': 'public, max-age=3600, s-maxage=7200, immutable',
  '/api':    'private, no-cache',
  '/secret': 'no-store',
  '/mixed':  'public, max-age=3600, s-maxage=7200, must-revalidate',
  '/swr':    'public, max-age=60, stale-while-revalidate=600',
};

const server = http.createServer((req, res) => {
  const path = req.url.split('?')[0];

  if (path === '/' || path === '') {
    const list = Object.entries(ROUTES)
      .map(([p, cc]) => `${p.padEnd(9)} -> ${cc}`)
      .join('\n');
    res.writeHead(200, { 'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'no-store' });
    res.end(`cache-control lab\n\nendpoints:\n${list}\n\ntry: curl -sI http://localhost:${PORT}/mixed\n`);
    return;
  }

  const cc = ROUTES[path];
  if (!cc) {
    res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'no-store' });
    res.end('404\n');
    return;
  }

  counter += 1;
  const body = `endpoint: ${path}\nCache-Control: ${cc}\ngenerated-by-origin: ${new Date().toISOString()}\nrequest-number: ${counter}\n`;
  res.writeHead(200, { 'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': cc });
  res.end(body);
});

server.listen(PORT, () => {
  console.log(`origin up at http://localhost:${PORT}`);
  console.log(`endpoints: ${Object.keys(ROUTES).join(', ')}`);
});
