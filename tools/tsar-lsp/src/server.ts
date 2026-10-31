import {
  createConnection,
  TextDocuments,
  Diagnostic,
  DiagnosticSeverity,
  ProposedFeatures,
  TextDocumentSyncKind,
} from 'vscode-languageserver/node';
import { TextDocument } from 'vscode-languageserver-textdocument';
import * as fs from 'fs';
import * as path from 'path';

const connection = createConnection(ProposedFeatures.all);
const documents = new TextDocuments(TextDocument);

type Rule = { name: string; pattern: RegExp; severity: 'error' | 'warning'; message: string };

function loadRules(): Rule[] {
  const root = path.resolve(__dirname, '..', '..');
  const rulesFile = path.join(root, 'tools', 'tsar-lsp', 'rules.json');
  const raw = JSON.parse(fs.readFileSync(rulesFile, 'utf-8')) as { name: string; pattern: string; severity: 'error' | 'warning'; message: string }[];
  return raw.map((r) => ({
    name: r.name,
    pattern: new RegExp(r.pattern, 'g'),
    severity: r.severity,
    message: r.message,
  }));
}

const rules = loadRules();

function validate(text: string): Diagnostic[] {
  const diags: Diagnostic[] = [];
  const lines = text.split('\n');
  for (const rule of rules) {
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      rule.pattern.lastIndex = 0;
      let match: RegExpExecArray | null;
      while ((match = rule.pattern.exec(line)) !== null) {
        diags.push({
          severity: rule.severity === 'error' ? DiagnosticSeverity.Error : DiagnosticSeverity.Warning,
          range: {
            start: { line: i, character: match.index },
            end: { line: i, character: match.index + match[0].length },
          },
          message: `[TSAR ${rule.name}] ${rule.message}`,
          source: 'tsar',
        });
      }
    }
  }
  return diags;
}

connection.onInitialize(() => ({
  capabilities: {
    textDocumentSync: TextDocumentSyncKind.Incremental,
  },
}));

documents.onDidChangeContent((change) => {
  const diags = validate(change.document.getText());
  connection.sendDiagnostics({ uri: change.document.uri, diagnostics: diags });
});

documents.listen(connection);
connection.listen();
