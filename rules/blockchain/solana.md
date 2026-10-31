# Solana Program Security Baseline

## Account Validation
- Every account is untrusted until validated: owner, signer, writable, discriminator.
- Use Anchor's `#[account(...)]` constraints; never skip validation.
- Verify PDAs with `find_program_address` and the expected seeds.
- Reject accounts owned by unexpected programs.

## Signer Checks
- `is_signer` required for authority fields.
- Sysvar and program accounts are never signers unless explicitly required.

## Arithmetic
- Use checked arithmetic: `checked_add`, `checked_sub`, `checked_mul`.
- No `as` casts between integer sizes without bounds checks.
- Consider `uint` wraparound in release builds (`overflow-checks = true`).

## CPI (Cross-Program Invocation)
- Validate target program ID against an allow-list.
- Never pass user-controlled accounts to CPI without validation.
- Reentrancy: assume CPI can call back; guard state mutations.

## Token Handling
- Use `anchor_spl::token`; do not manipulate token accounts manually.
- Verify mint authority and freeze authority.
- Check decimals before amount math.

## Closing Accounts
- Zero data before closing to prevent revival attacks.
- Close rent to the correct recipient.

## Compute Budget
- Set explicit compute units; reject transactions exceeding the cap.
- Avoid unbounded loops; Solana has a hard compute limit per instruction.

## Testing Requirements
- `anchor test` with bankrun for all instruction paths.
- Property tests with `proptest`.
- Fuzz account inputs.

## Forbidden
- `unsafe` Rust in production without audit.
- `unwrap()` or `expect()` on user-controlled data.
- Manual deserialization without discriminator checks.
- Unbounded vectors in account data.
