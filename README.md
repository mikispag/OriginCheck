# OriginCheck
Python script to check how web servers and web apps react to unexpected extra `Origin` headers in requests.

# URL list
I retrieved a list of URLs, one per domain, from [The HTTP Archive](https://httparchive.org/), with the following BigQuery query:

```sql
SELECT
  MAX(url) AS url,
  DOMAIN(url) AS domain
FROM
  [httparchive:runs.latest_requests]
WHERE
  method = 'GET'
  AND status = 200
  AND type = 'html'
GROUP BY
  domain
```

# Results as of May 9, 2018

* 336476 stable (non-redirects, status code 200, constant response size across requests) URLs
* 327145 (97.22%) are `SAMEORIGIN_OK`
* 322902 (95.97%) are `CROSSORIGIN_OK`

Out of the ones that choked on a same-origin unexpected `Origin` header:

* 9191 returned a different response
* 140 returned a non-200 HTTP status:

|http_status_code|count|
|--|--|
|503|72|
|403|20|
|500|15|
|302|9|
|301|6|
|404|4|
|502|3|
|210|2|
|400|2|
|429|2|
|523|2|
|204|1|
|504|1|
|526|1|

Out of the ones that choked on a cross-origin unexpected `Origin` header:

* 4037 returned a different response
* 140 returned a non-200 HTTP status:

|http_status_code|count|
|--|--|
|403|113|
|503|36|
|302|14|
|429|11|
|500|9|
|210|5|
|502|5|
|400|3|
|204|2|
|301|2|
|404|1|
|410|1|
|415|1|
|520|1|
|521|1|
|525|1|
