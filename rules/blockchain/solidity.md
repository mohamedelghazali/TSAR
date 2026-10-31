# Solidity Security Baseline

## Compiler and Toolchain
- Solidity >= 0.8.20; no `pragma` ranges in production.
- Enable optimizer with `runs` tuned per contract; document the value.
- Build with Foundry or Hardhat; pin compiler version in config.
- Run Slither, Mythril, and Echidna in CI.

## Reentrancy
- Checks-Effects-Interactions order mandatory.
- Use `nonReentrant` from OpenZeppelin on every external-call-bearing function.
- Never use `transfer` or `send` for value transfer; use `call{value:}("")`.
- Guard against cross-function and cross-contract reentrancy.

## Access Control
- Use OpenZeppelin `AccessControl` or `Ownable2Step`.
- No `tx.origin` for authorization; use `msg.sender`.
- Renounce or time-lock admin roles before mainnet.
- Two-step transfers for critical ownership.

## Arithmetic
- Solidity >= 0.8 has checked arithmetic by default; never use `unchecked` unless audited.
- Fixed-point math via audited libraries (PRBMath, ABDKMath64x64).

## Randomness
- On-chain randomness is predictable. Use Chainlink VRF or commit-reveal.
- Never use `block.timestamp`, `blockhash`, or `block.difficulty` for randomness.

## Upgradability
- Use UUPS or Transparent proxy with audited implementation.
- Storage layout: append-only; never reorder or remove variables.
- Initialize with `_disableInitializers()` in implementation constructor.
- Upgrade requires timelock + multi-sig.

## Oracles
- Chainlink or TWAP with manipulation resistance.
- Validate price freshness and bounds.
- Fail closed on oracle failure.

## External Calls
- Limit gas forwarded; use low-level `call` with explicit gas.
- Verify return values.
- Never delegatecall to untrusted addresses.

## Front-Running and MEV
- Commit-reveal for sensitive actions.
- Slippage bounds on swaps.
- Deadline parameters on time-sensitive operations.

## Forbidden
- `selfdestruct` in any new contract.
- `delegatecall` to user-controlled address.
- Loop over dynamic arrays with unbounded length in state-changing functions.
- `assembly` without explicit memory safety audit.
- Floating pragma (`pragma solidity ^0.8.0;`).

## Testing Requirements
- 100% branch coverage on critical paths.
- Fuzz tests (Echidna/Foundry) with >= 10,000 runs.
- Invariant tests on economic properties.
- Fork tests against mainnet state.
