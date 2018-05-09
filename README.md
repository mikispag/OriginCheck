# OriginCheck
Python script to check how web servers and web apps react to unexpected extra Origin headers in requests.

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
