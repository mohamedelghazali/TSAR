import { readFileSync, existsSync } from 'fs';
import path from 'path';
import yaml from 'yaml';

type Manifest = {
  version: string;
  last_updated: string;
  active_files: Record<string, string[]>;
};

function loadManifest(): Manifest | null {
  const p = path.resolve(process.cwd(), '..', '..', 'manifest.yaml');
  if (!existsSync(p)) return null;
  return yaml.parse(readFileSync(p, 'utf-8')) as Manifest;
}

function countFiles(group: Record<string, string[]>): number {
  return Object.values(group).reduce((sum, files) => sum + files.length, 0);
}

function missingFiles(manifest: Manifest): string[] {
  const root = path.resolve(process.cwd(), '..', '..');
  const missing: string[] = [];
  for (const files of Object.values(manifest.active_files)) {
    for (const rel of files) {
      if (!existsSync(path.join(root, rel))) missing.push(rel);
    }
  }
  return missing;
}

export default function Home() {
  const manifest = loadManifest();
  if (!manifest) {
    return (
      <main style={{ padding: 24, fontFamily: 'system-ui, sans-serif' }}>
        <h1>TSAR Dashboard</h1>
        <p>manifest.yaml not found. Run from the TSAR repository root.</p>
      </main>
    );
  }
  const missing = missingFiles(manifest);
  const total = countFiles(manifest.active_files);

  return (
    <main style={{ padding: 24, fontFamily: 'system-ui, sans-serif' }}>
      <h1>TSAR Dashboard</h1>
      <section style={{ marginTop: 24 }}>
        <h2>Manifest</h2>
        <p><strong>Version:</strong> {manifest.version}</p>
        <p><strong>Last updated:</strong> {manifest.last_updated}</p>
        <p><strong>Active files:</strong> {total}</p>
      </section>
      <section style={{ marginTop: 24 }}>
        <h2>Coverage by Domain</h2>
        <table cellPadding={6} style={{ borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#eee' }}>
              <th align="left">Domain</th>
              <th align="right">Files</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(manifest.active_files).map(([domain, files]) => (
              <tr key={domain}>
                <td>{domain}</td>
                <td align="right">{files.length}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
      <section style={{ marginTop: 24 }}>
        <h2>Missing Files</h2>
        {missing.length === 0 ? (
          <p style={{ color: 'green' }}>All active files present.</p>
        ) : (
          <ul style={{ color: 'red' }}>
            {missing.map((f) => <li key={f}>{f}</li>)}
          </ul>
        )}
      </section>
      <section style={{ marginTop: 24, color: '#666', fontSize: 12 }}>
        <p>Run scanners via <code>tsar scan . --format sarif</code> and upload results to your SIEM.</p>
      </section>
    </main>
  );
}
