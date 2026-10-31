// TSAR reference: SPA with secure token handling and nonce CSP.
import React, { createContext, useContext, useEffect, useState } from 'react';

type User = { id: string; email: string; roles: string[] };

const AuthContext = createContext<{ user: User | null }>({ user: null });

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetch('/api/auth/me', {
      credentials: 'include',
      headers: { 'X-CSRF-Token': getCsrfToken() },
    })
      .then((r) => (r.ok ? r.json() : null))
      .then((u) => { if (!cancelled) setUser(u); })
      .catch(() => { if (!cancelled) setUser(null); });
    return () => { cancelled = true; };
  }, []);

  return <AuthContext.Provider value={{ user }}>{children}</AuthContext.Provider>;
}

function getCsrfToken(): string {
  const meta = document.querySelector('meta[name="csrf-token"]');
  return meta ? (meta as HTMLMetaElement).content : '';
}

export function useAuth() {
  return useContext(AuthContext);
}

export function RequireAuth({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  if (!user) return <div>Sign in required.</div>;
  return <>{children}</>;
}

export function sanitizeHtml(input: string): string {
  // Never rely on this alone; server must sanitize. Client-side is defense-in-depth.
  const div = document.createElement('div');
  div.textContent = input;
  return div.innerHTML;
}
