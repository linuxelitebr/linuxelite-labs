vcl 4.1;

# Minimal shared cache, just enough to show s-maxage winning over max-age.
# Varnish derives the TTL from Cache-Control in the order s-maxage > max-age > Expires,
# so /mixed (max-age=3600, s-maxage=7200) lives 7200s in the edge cache, while a browser
# would use 3600s. That is the whole point of the article, live.

backend origin {
    .host = "origin";
    .port = "8080";
}

sub vcl_deliver {
    if (obj.hits > 0) {
        set resp.http.X-Cache = "HIT";
    } else {
        set resp.http.X-Cache = "MISS";
    }
    set resp.http.X-Cache-Hits = obj.hits;
}
