// TSAR reference implementation: Go secure patterns.
// Dependencies: golang.org/x/crypto/argon2, github.com/golang-jwt/jwt/v5
package secure

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/hmac"
	"crypto/rand"
	"crypto/sha256"
	"crypto/subtle"
	"errors"
	"time"

	"golang.org/x/crypto/argon2"
)

const (
	argonTime    = 3
	argonMemory  = 64 * 1024
	argonThreads = 4
	argonKeyLen  = 32
)

func HashPassword(password string, salt []byte) []byte {
	if len(password) < 12 {
		panic("password too short")
	}
	if len(salt) < 16 {
		panic("salt must be 16+ bytes")
	}
	return argon2.IDKey([]byte(password), salt, argonTime, argonMemory, argonThreads, argonKeyLen)
}

func VerifyPassword(password string, salt, stored []byte) bool {
	computed := HashPassword(password, salt)
	return subtle.ConstantTimeCompare(computed, stored) == 1
}

func RandomBytes(n int) []byte {
	b := make([]byte, n)
	if _, err := rand.Read(b); err != nil {
		panic(err)
	}
	return b
}

type AEADBox struct {
	key []byte
}

func NewAEADBox(key []byte) (*AEADBox, error) {
	if len(key) != 32 {
		return nil, errors.New("key must be 32 bytes")
	}
	return &AEADBox{key: key}, nil
}

func (b *AEADBox) Encrypt(plaintext, aad []byte) ([]byte, error) {
	block, err := aes.NewCipher(b.key)
	if err != nil {
		return nil, err
	}
	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return nil, err
	}
	nonce := RandomBytes(gcm.NonceSize())
	out := gcm.Seal(nil, nonce, plaintext, aad)
	return append(append([]byte{1}, nonce...), out...), nil
}

func (b *AEADBox) Decrypt(envelope, aad []byte) ([]byte, error) {
	if len(envelope) < 13 || envelope[0] != 1 {
		return nil, errors.New("bad envelope")
	}
	block, err := aes.NewCipher(b.key)
	if err != nil {
		return nil, err
	}
	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return nil, err
	}
	nonce := envelope[1 : 1+gcm.NonceSize()]
	ct := envelope[1+gcm.NonceSize():]
	return gcm.Open(nil, nonce, ct, aad)
}

func ConstantTimeEqual(a, b []byte) bool {
	return hmac.Equal(a, b)
}

func HashID(id string) string {
	sum := sha256.Sum256([]byte(id))
	return string(sum[:8])
}

type TokenClaims struct {
	Sub string `json:"sub"`
	Exp int64  `json:"exp"`
}

func NewToken(userID string, ttl time.Duration) TokenClaims {
	return TokenClaims{Sub: userID, Exp: time.Now().Add(ttl).Unix()}
}
