# TSAR Language Server

Exposes TSAR rules as live diagnostics in any LSP-compatible editor.

## Build
```bash
cd tools/tsar-lsp
npm install
npm run build
```

The release-gate workflow builds this package on pull requests that change the
LSP, policy, or full-verification inputs. The generated `out/` directory is
a build artifact and is not required to be committed.

## VS Code Integration
Create `.vscode/settings.json` in your project:

```json
{
  "tsar-lsp.enable": true
}
```

Create `.vscode/extensions/tsar-lsp/package.json` for a minimal extension, or use
`vscode-languageclient` to register the server.

## JetBrains Integration
Use the LSP API plugin and point it to `node out/server.js`.

## Neovim
```lua
require('lspconfig').tsar_lsp.setup({
  cmd = { 'node', '<path>/tools/tsar-lsp/out/server.js' },
  filetypes = { 'python', 'javascript', 'typescript', 'go', 'rust', 'java', 'kotlin', 'swift' },
})
```

## Rules
Rules are loaded from `rules.json`. Update it to add or remove checks. The
server re-reads the file at startup; restart the editor to reload.

## Release verification
The LSP compiler is also executed as part of the complete `verify-all.sh`
release gate; a missing or failed build blocks that gate.
