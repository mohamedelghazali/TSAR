// TSAR reference implementation: Java secure patterns.
// Dependencies: org.bouncycastle:bcprov-jdk18on, com.password4j:password4j, com.auth0:java-jwt
package com.tsar.examples;

import javax.crypto.Cipher;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.*;
import com.password4j.Password;
import com.auth0.jwt.JWT;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.interfaces.DecodedJWT;

public final class SecureApp {
    private static final SecureRandom RNG = new SecureRandom();
    private static final int GCM_TAG_BITS = 128;
    private static final int GCM_NONCE_BYTES = 12;
    private SecureApp() {}
    public static String hashPassword(String password) {
        if (password == null || password.length() < 12) throw new IllegalArgumentException("password must be at least 12 characters");
        return Password.hash(password).addRandomSalt(16).withArgon2().getResult();
    }
    public static boolean verifyPassword(String password, String stored) { return Password.check(password, stored).withArgon2(); }
    public static boolean constantTimeEquals(byte[] a, byte[] b) { return MessageDigest.isEqual(a, b); }
    public static String randomToken() {
        byte[] buf = new byte[32]; RNG.nextBytes(buf);
        return Base64.getUrlEncoder().withoutPadding().encodeToString(buf);
    }
    public static byte[] aeadEncrypt(byte[] key, byte[] plaintext, byte[] aad) throws Exception {
        if (key.length != 32) throw new IllegalArgumentException("key must be 32 bytes");
        byte[] nonce = new byte[GCM_NONCE_BYTES]; RNG.nextBytes(nonce);
        Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
        SecretKey k = new SecretKeySpec(key, "AES");
        c.init(Cipher.ENCRYPT_MODE, k, new GCMParameterSpec(GCM_TAG_BITS, nonce));
        c.updateAAD(aad); byte[] ct = c.doFinal(plaintext);
        byte[] out = new byte[1 + nonce.length + ct.length]; out[0] = 1;
        System.arraycopy(nonce, 0, out, 1, nonce.length);
        System.arraycopy(ct, 0, out, 1 + nonce.length, ct.length); return out;
    }
    public static byte[] aeadDecrypt(byte[] key, byte[] envelope, byte[] aad) throws Exception {
        if (envelope.length < 1 + GCM_NONCE_BYTES || envelope[0] != 1) throw new IllegalArgumentException("bad envelope");
        Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
        SecretKey k = new SecretKeySpec(key, "AES");
        c.init(Cipher.DECRYPT_MODE, k, new GCMParameterSpec(GCM_TAG_BITS, envelope, 1, GCM_NONCE_BYTES));
        c.updateAAD(aad);
        return c.doFinal(envelope, 1 + GCM_NONCE_BYTES, envelope.length - 1 - GCM_NONCE_BYTES);
    }
    public static String issueToken(String userId, byte[] secret, int ttlSeconds) {
        Instant now = Instant.now();
        return JWT.create().withSubject(userId).withIssuedAt(Date.from(now))
            .withExpiresAt(Date.from(now.plus(ttlSeconds, ChronoUnit.SECONDS))).withJWTId(randomToken())
            .sign(Algorithm.HMAC256(secret));
    }
    public static DecodedJWT verifyToken(String token, byte[] secret) {
        return JWT.require(Algorithm.HMAC256(secret)).build().verify(token);
    }
    public static void audit(String event, String userId, String outcome) throws Exception {
        byte[] id = MessageDigest.getInstance("SHA-256").digest(userId.getBytes(StandardCharsets.UTF_8));
        String hashed = Base64.getEncoder().encodeToString(Arrays.copyOf(id, 8));
        System.out.println(Map.of("event", event, "user", hashed, "outcome", outcome, "ts", Instant.now().toString()));
    }
}