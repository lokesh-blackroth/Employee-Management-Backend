# Redis Cache Design and Baseline Measurements

**Project:** Employee Management Backend
**Date:** 12 October 2026
**Owner:** Lokesh Raj
**Epic:** Redis Performance Optimization, Celery Reliability & Job Monitoring

## 1. Objective

Measure the existing department-summary cache performance and document
the cache key, TTL, invalidation strategy, and freshness expectations.

## 2. Selected Endpoint

GET /api/v1/reports/department-summary/

The endpoint returns department summary data and is a suitable candidate
for caching because the report may be requested repeatedly.

## 3. Cache Design

- Cache backend: Django RedisCache (`django_redis.cache.RedisCache`)
- Cache key: department_summary:v1
- Key prefix: employee_management
- TTL: 300 seconds (5 minutes)
- Cache hit: Return cached summary data.
- Cache miss: Calculate the summary from the database and cache the result.
- Invalidation: Delete the cached summary after relevant employee or
  department changes.
- Redis failure: Attempt to calculate the summary directly from the database.

## 4. Baseline Benchmark

Initial function-level benchmark: 10 iterations per scenario.

| Metric | Cache bypassed | Cache enabled (warm) |
|---|---:|---:|
| Median execution time | 2.108 ms | 0.930 ms |
| Average execution time | 6.691 ms | 1.008 ms |
| Median SQL queries | 1 | 0 |
| SQL queries per run | 1 each | 0 each |

Observed median execution-time reduction: approximately 55.9%.

The cached and uncached results were identical.
Redis cache read/write verification passed.

## 5. Measurement Limitations

These are function-level measurements, not full HTTP response times.
The test used a small sample of 10 iterations. Results may vary with
database state, machine load, and cache/network latency.

An endpoint-level benchmark is still required to measure HTTP response
time and authenticated API behavior.

## 6. Freshness Expectations

- A successful invalidation should make the next request calculate fresh data.
- If invalidation is missed, the cached value expires after the configured TTL.
- Cache failures should not cause an unhandled exception in the selected read path.

## 7. Next Steps

1. Measure endpoint-level response times.
2. Verify cache expiry and invalidation behavior.
3. Test Redis outage fallback.
4. Record final results and regression evidence.

## HTTP Performance Benchmark — 12 October 2026

### Test setup
- Endpoint: GET /api/v1/reports/department-summary/
- Authentication: JWT
- Cache: Redis
- Method: 10 paired requests; clear the department-summary cache before each pair, then issue a cache-miss request followed by a warm-cache request.
- Timing: HTTP request elapsed time, excluding the separate cache-clearing command.

### Results

| Metric | Result |
|---|---:|
| Cache-miss median | 80.31 ms |
| Warm-cache median | 68.21 ms |
| Median latency reduction | 15.06% |
| Successful cache-miss requests | 10/10 |
| Successful cache-hit requests | 10/10 |

Median latency reduction was calculated as:
((80.31 - 68.21) / 80.31) * 100 = 15.06%.

### Interpretation and limitations
The paired test showed lower median HTTP latency for warm-cache requests. The result is preliminary because the sample is small and local machine load, network overhead, and request variability can affect timings. Repeat the benchmark for more confidence before making production performance claims.


## Cache Reliability Tests — 12 October 2026

### Cache invalidation
- Inserted a temporary test value under `department_summary:v1`.
- Verified the value existed before invalidation.
- Called `invalidate_department_summary_cache()`.
- Verified the value was absent afterward (`None`).
- Result: PASS.

### Redis failure fallback
- Simulated a cache-read exception using Python `unittest.mock`.
- Verified the service logged the cache failure and returned department data directly from the reporting function.
- Result: PASS.
- Returned result: list containing 7 department summaries.
- Limitation: This was a simulated cache exception, not an actual Redis server outage.

