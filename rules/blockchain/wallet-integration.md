# Wallet Integration Security

## Client Side
- Never request private keys or seed phrases.
- Use WalletConnect v2 or native browser extension APIs.
- Verify chain ID before signing.
- Display human-readable transaction details; never sign opaque bytes.
- Warn on unknown contracts and infinite approvals.

## Transaction Signing
- EIP-712 typed data for structured signing; never sign raw hex for off-chain auth.
- Include `nonce`, `chainId`, `deadline` in signed payloads.
- Reject signatures older than the declared deadline.

## Approval Hygiene
- Default to exact-amount approvals; infinite approvals require explicit opt-in.
- Provide revoke UI; link to revoke.cash or equivalent.

## Session Keys (AA / Smart Wallets)
- Scoped permissions: allowed contracts, allowed functions, spend limits, expiry.
- Rotate session keys; revoke on logout.

## Phishing Defense
- Contract allow-list for known dApps.
- Domain binding via EIP-4361 (Sign-In with Ethereum).
- Show origin and requested permissions before signing.

## Forbidden
- Blind signing.
- Signing without chain ID.
- Storing seed phrases in any form on the client.
- Auto-approving token allowances.
