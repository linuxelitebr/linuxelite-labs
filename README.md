# linuxelite-labs

Reproducible PoCs for [Linux Elite](https://linuxelite.com.br) posts. One subdirectory per topic. The rule is simple: if a post claims something, the code that proves it lives here. No "trust me".

## Labs

| Lab | Post | What it proves |
| --- | --- | --- |
| [`cache-control/`](cache-control/) | [Cache-Control na prática](https://linuxelite.com.br/blog/cache-control-s-maxage/) | s-maxage beating max-age in a shared cache, live with Varnish |
| [`http-status/`](http-status/) | [401 vs 403](https://linuxelite.com.br/blog/401-vs-403/) | each status code with the header the RFC requires (401's WWW-Authenticate, 405's Allow) |

Each lab has its own README with the steps.
