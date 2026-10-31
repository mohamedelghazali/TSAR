// TSAR reference implementation: React Native secure patterns.
// Dependencies: react-native-keychain, react-native-encrypted-storage, zod
import * as Keychain from 'react-native-keychain';
import EncryptedStorage from 'react-native-encrypted-storage';
import { z } from 'zod';

export async function storeToken(service: string, token: string): Promise<void> {
  await Keychain.setGenericPassword('token', token, {
    service,
    accessible: Keychain.ACCESSIBLE.WHEN_UNLOCKED_THIS_DEVICE_ONLY,
    storage: Keychain.STORAGE_TYPE.AES_GCM_NO_AUTH,
  });
}

export async function readToken(service: string): Promise<string | null> {
  const creds = await Keychain.getGenericPassword({ service });
  return creds ? creds.password : null;
}

export async function clearToken(service: string): Promise<void> {
  await Keychain.resetGenericPassword({ service });
}

export async function storePref(key: string, value: unknown): Promise<void> {
  await EncryptedStorage.setItem(key, JSON.stringify(value));
}

export async function readPref<T>(key: string, schema: z.ZodType<T>): Promise<T | null> {
  const raw = await EncryptedStorage.getItem(key);
  if (!raw) return null;
  return schema.parse(JSON.parse(raw));
}

const InputSchema = z.object({
  action: z.enum(['read', 'list', 'search']),
  resourceId: z.string().uuid(),
});

export type Input = z.infer<typeof InputSchema>;

export function validateInput(raw: unknown): Input {
  return InputSchema.parse(raw);
}

export async function apiCall(
  baseUrl: string,
  path: string,
  body: unknown,
): Promise<unknown> {
  const token = await readToken('api');
  if (!token) throw new Error('unauthenticated');
  const url = new URL(path, baseUrl);
  if (url.host !== new URL(baseUrl).host) throw new Error('cross-origin blocked');
  const res = await fetch(url.toString(), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`api error ${res.status}`);
  return res.json();
}

export function hasBiometric(): Promise<boolean> {
  return Keychain.getSupportedBiometryType().then((t) => t !== null);
}
