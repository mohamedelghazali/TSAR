# Blockchain Security Rules

Scope: smart contracts, wallets, on-chain integrations.

## Files
- `solidity.md` — EVM smart contracts.
- `solana.md` — Solana programs.
- `wallet-integration.md` — client-side wallet flows.

## Mandatory Toolchain
- Foundry (EVM) or Anchor (Solana).
- Slither, Mythril (EVM).
- Echidna/Foundry fuzz, Anchor bankrun (Solana).
- Audited libraries: OpenZeppelin, Solana Program Library.

## Forbidden Practices
- Unbounded loops in state-changing functions.
- `tx.origin` for authorization.
- `delegatecall` to user-controlled addresses.
- Blind signing in wallets.
- On-chain randomness without VRF or commit-reveal.

## Test Requirements
- 100% branch coverage on critical paths.
- Fuzz tests >= 10,000 runs.
- Invariant tests on economic properties.
- Fork tests against mainnet state.
