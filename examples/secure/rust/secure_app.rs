// TSAR reference implementation: Rust secure patterns.
// Dependencies: aes-gcm, argon2, subtle, rand, chacha20poly1305

use aes_gcm::{aead::{Aead, KeyInit, Payload}, Aes256Gcm, Key, Nonce};
use argon2::{Argon2, PasswordHash, PasswordHasher, PasswordVerifier};
use argon2::password_hash::{rand_core::OsRng, SaltString};
use chacha20poly1305::XChaCha20Poly1305;
use rand::RngCore;
use subtle::ConstantTimeEq;

pub fn hash_password(password: &str) -> Result<String, argon2::password_hash::Error> {
    if password.len() < 12 {
        return Err(argon2::password_hash::Error::Password);
    }
    let salt = SaltString::generate(&mut OsRng);
    let argon = Argon2::default();
    Ok(argon.hash_password(password.as_bytes(), &salt)?.to_string())
}

pub fn verify_password(password: &str, stored: &str) -> bool {
    let parsed = match PasswordHash::new(stored) {
        Ok(p) => p,
        Err(_) => return false,
    };
    Argon2::default().verify_password(password.as_bytes(), &parsed).is_ok()
}

pub fn constant_time_eq(a: &[u8], b: &[u8]) -> bool {
    if a.len() != b.len() {
        return false;
    }
    a.ct_eq(b).into()
}

pub fn random_nonce_12() -> [u8; 12] {
    let mut n = [0u8; 12];
    OsRng.fill_bytes(&mut n);
    n
}

pub struct AeadBox {
    key: [u8; 32],
}

impl AeadBox {
    pub fn new(key: [u8; 32]) -> Self {
        Self { key }
    }

    pub fn encrypt(&self, plaintext: &[u8], aad: &[u8]) -> Vec<u8> {
        let cipher = Aes256Gcm::new(Key::<Aes256Gcm>::from_slice(&self.key));
        let nonce_bytes = random_nonce_12();
        let nonce = Nonce::from_slice(&nonce_bytes);
        let ct = cipher
            .encrypt(nonce, Payload { msg: plaintext, aad })
            .expect("encryption failed");
        let mut out = Vec::with_capacity(1 + 12 + ct.len());
        out.push(1u8);
        out.extend_from_slice(&nonce_bytes);
        out.extend_from_slice(&ct);
        out
    }

    pub fn decrypt(&self, envelope: &[u8], aad: &[u8]) -> Result<Vec<u8>, &'static str> {
        if envelope.len() < 13 || envelope[0] != 1 {
            return Err("bad envelope");
        }
        let cipher = Aes256Gcm::new(Key::<Aes256Gcm>::from_slice(&self.key));
        let nonce = Nonce::from_slice(&envelope[1..13]);
        cipher
            .decrypt(nonce, Payload { msg: &envelope[13..], aad })
            .map_err(|_| "decryption failed")
    }
}

pub fn encrypt_xchacha(key: &[u8; 32], plaintext: &[u8], aad: &[u8]) -> Vec<u8> {
    let cipher = XChaCha20Poly1305::new(key.into());
    let mut nonce_bytes = [0u8; 24];
    OsRng.fill_bytes(&mut nonce_bytes);
    let nonce = chacha20poly1305::XNonce::from_slice(&nonce_bytes);
    let ct = cipher
        .encrypt(nonce, chacha20poly1305::aead::Payload { msg: plaintext, aad })
        .expect("encryption failed");
    let mut out = Vec::with_capacity(24 + ct.len());
    out.extend_from_slice(&nonce_bytes);
    out.extend_from_slice(&ct);
    out
}
