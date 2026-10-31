// TSAR reference implementation: Node.js secure patterns.
// Dependencies: argon2, @noble/ciphers, jose, zod

const crypto = require('node:crypto');
const argon2 = require('argon2');
const { xchacha20poly1305 } = require('@noble/ciphers/chacha');
const { SignJWT, jwtVerify } = require('jose');
const { z } = require('zod');

const ARGON2_OPTS = { type: argon2.argon2id, memoryCost: 65536, timeCost: 3, parallelism: 4 };

async function hashPassword(password) {
  if (password.length < 12) throw new Error('password too short');
  return argon2.hash(password, ARGON2_OPTS);
}

async function verifyPassword(password, stored) {
  try { return await argon2.verify(stored, password); }
  catch { return false; }
}

function constantTimeEqual(a, b) {
  const ab = Buffer.from(a);
  const bb = Buffer.from(b);
  if (ab.length !== bb.length) return false;
  return crypto.timingSafeEqual(ab, bb);
}

function generateToken(bytes = 32) {
  return crypto.randomBytes(bytes).toString('base64url');
}

class AEADBox {
  constructor(masterKey) {
    if (masterKey.length !== 32) throw new Error('master key must be 32 bytes');
    this.key = masterKey;
  }
  derive(purpose) {
    return Buffer.from(crypto.hkdfSync('sha256', this.key, Buffer.alloc(0), Buffer.from('tsar/aead/' + purpose), 32));
  }
  encrypt(plaintext, aad) {
    const key = this.derive('data');
    const nonce = crypto.randomBytes(24);
    const cipher = xchacha20poly1305(key, nonce, aad);
    const ct = cipher.encrypt(plaintext);
    return Buffer.concat([Buffer.from([1]), nonce, Buffer.from(ct)]);
  }
  decrypt(envelope, aad) {
    if (envelope[0] !== 1) throw new Error('unsupported envelope');
    const nonce = envelope.subarray(1, 25);
    const ct = envelope.subarray(25);
    const key = this.derive('data');
    return Buffer.from(xchacha20poly1305(key, nonce, aad).decrypt(ct));
  }
}

const JWT_SECRET = Buffer.from(process.env.TSAR_JWT_SECRET, 'base64');

async function issueToken(userId, ttlSeconds = 900) {
  return new SignJWT({ sub: userId })
    .setProtectedHeader({ alg: 'HS256', typ: 'JWT' })
    .setIssuedAt()
    .setExpirationTime(Math.floor(Date.now() / 1000) + ttlSeconds)
    .setJti(crypto.randomBytes(16).toString('base64url'))
    .sign(JWT_SECRET);
}

async function verifyToken(token) {
  const { payload } = await jwtVerify(token, JWT_SECRET, { algorithms: ['HS256'] });
  return payload;
}

const InputSchema = z.object({
  action: z.enum(['read', 'list', 'search']),
  resourceId: z.string().uuid(),
});

function validateInput(raw) {
  return InputSchema.parse(raw);
}

function authorize(payload, ownerId) {
  if (payload.sub === ownerId) return true;
  if ((payload.roles || []).includes('admin')) return true;
  return false;
}

module.exports = {
  hashPassword, verifyPassword, constantTimeEqual, generateToken,
  AEADBox, issueToken, verifyToken, validateInput, authorize,
};
