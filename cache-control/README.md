# cache-control lab

Reproducible PoC for the post [Cache-Control na prática: max-age, s-maxage e como controlar cache de verdade](https://linuxelite.com.br/blog/cache-control-s-maxage/) (PT-BR).

You don't learn caching by reading, you learn it with the header on screen. This spins up an origin that emits each directive and, if you want, a Varnish in front so you can watch a shared cache obey `s-maxage` for real, not because it "should".

## Just the origin (no Docker)

Plain Node, zero dependencies:

```bash
node server.js
curl -sI http://localhost:8080/mixed
```

Output:

```text
HTTP/1.1 200 OK
Cache-Control: public, max-age=3600, s-maxage=7200, must-revalidate
Content-Type: text/plain; charset=utf-8
```

`demo.sh` hits every endpoint:

```bash
./demo.sh
```

## With the shared cache (Varnish)

This is the part that actually proves it. Bring up the origin and Varnish:

```bash
docker compose up
```

Hit Varnish (port 8081) twice and watch `X-Cache` and `Age`:

```bash
./demo.sh http://localhost:8081
```

On the second call `/mixed` comes back `X-Cache: HIT` with `Age` climbing: Varnish kept it. And it kept it for **7200s**, because as a shared cache it reads `s-maxage`, not `max-age=3600`. A browser, given the same header, would use 3600s. One header, two TTLs, the way the post explains.

## The endpoints

| Endpoint | Cache-Control | What to watch |
| --- | --- | --- |
| `/static` | `public, max-age=3600, s-maxage=7200, immutable` | versioned asset, no revalidation on reload |
| `/api` | `private, no-cache` | browser stores and revalidates every time; the CDN won't store it |
| `/secret` | `no-store` | nobody stores anything |
| `/mixed` | `public, max-age=3600, s-maxage=7200, must-revalidate` | the header from the title: the CDN holds it twice as long |
| `/swr` | `public, max-age=60, stale-while-revalidate=600` | serves stale while it revalidates underneath |

## The facts, with the source

None of this is hand-waving. The claims come straight from the RFC:

- `no-cache` CAN store; it just revalidates before reuse. `no-store` is the one that blocks. (RFC 9111, 5.2.2.4 and 5.2.2.5)
- `s-maxage` only applies to shared caches and, there, overrides `max-age`. The browser ignores it. (RFC 9111, 5.2.2.10 and 4.2.1)
- `private`/`public` are about WHERE it can be stored, not about secrecy. (RFC 9111, 5.2.2.7 and 5.2.2.9)
- `immutable` only holds while fresh; a force reload still revalidates. (RFC 8246)
- `stale-while-revalidate` does not extend freshness. (RFC 5861)

## Sources

- [RFC 9111 - HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111.html)
- [RFC 8246 - HTTP Immutable Responses](https://www.rfc-editor.org/rfc/rfc8246.html)
- [RFC 5861 - Cache-Control Extensions for Stale Content](https://www.rfc-editor.org/rfc/rfc5861.html)
- [MDN - Cache-Control](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control)
