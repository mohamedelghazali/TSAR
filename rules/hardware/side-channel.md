# Side-Channel Resistance

## Timing
- Constant-time code for secret-dependent branches and memory access.
- Avoid secret-indexed table lookups.

## Power / EM
- Use hardware crypto accelerators for high-value keys.
- Masking and shuffling where software crypto is unavoidable.

## Cache
- Avoid secret-dependent cache access patterns.
- Consider cache-partitioning or constant-time algorithms for cross-tenant isolation.

## Testing
- Timing variance tests on secret-dependent operations.
- Statistical leakage tests (TVLA) for high-assurance targets.
