# http-status lab

Reproducible PoC for the post [401 vs 403: qual status HTTP retornar](https://linuxelite.com.br/blog/401-vs-403/) (PT-BR).

Status codes make sense once the status line and the header are on screen. This origin returns each code with the header the RFC actually requires, so you can read them with `curl -i`.

## Run it

Plain Node, zero dependencies:

```bash
node server.js
curl -sD - -o /dev/null http://localhost:8080/needs-auth
```

Output:

```text
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer
Content-Type: application/problem+json
```

`demo.sh` hits every scenario:

```bash
./demo.sh
```

## The endpoints

| Endpoint | Status | The header that matters |
| --- | --- | --- |
| `/needs-auth` | 401 Unauthorized | `WWW-Authenticate: Bearer` (RFC 9110 makes it a MUST) |
| `/forbidden` | 403 Forbidden | none (403 carries no WWW-Authenticate) |
| `/hidden` | 404 Not Found | none (a forbidden resource whose existence is hidden) |
| `/only-get` (POST it) | 405 Method Not Allowed | `Allow: GET, OPTIONS` (a MUST) |
| `/via-proxy` | 407 Proxy Authentication Required | `Proxy-Authenticate` (from a proxy, never an origin) |
| `/bad-request` | 400 Bad Request | none (malformed request, not an auth bucket) |

## The rules, with the source

Straight from RFC 9110:

- 401 means the request lacks a valid authentication credential, and the server MUST send a `WWW-Authenticate` challenge. A token that expired is not valid, so it is 401, not 403. (15.5.2, 11.6.1)
- 403 means the server understood and refuses. It does not require an authenticated client, and retrying with the same credential will not help. (15.5.4)
- To hide a forbidden resource's existence, an origin MAY answer 404 instead of 403. 404 hides, 403 confirms. (15.5.4, 15.5.5)
- Wrong method is 405 with an `Allow` header, not 403. (15.5.6)
- Every body is `application/problem+json` (RFC 9457): the JSON `status` matches the real HTTP status, so a client that ignores the body still behaves correctly. Never a 200 with an error body.

## Sources

- [RFC 9110 - HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html)
- [RFC 9457 - Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc9457.html)
- [MDN - 401 Unauthorized](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/401)
- [MDN - 403 Forbidden](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/403)
