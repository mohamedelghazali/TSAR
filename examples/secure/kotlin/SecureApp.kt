// TSAR reference implementation: Kotlin/Android secure patterns.
// Dependencies: androidx.security:security-crypto, com.password4j:password4j
package com.tsar.examples
import android.content.Context
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import com.password4j.Password
import java.security.MessageDigest
import java.security.SecureRandom
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec
object SecureApp {
    private val rng = SecureRandom()
    fun hashPassword(password: String): String {
        require(password.length >= 12) { "password must be at least 12 characters" }
        return Password.hash(password).addRandomSalt(16).withArgon2().result
    }
    fun verifyPassword(password: String, stored: String): Boolean = Password.check(password, stored).withArgon2()
    fun constantTimeEquals(a: ByteArray, b: ByteArray): Boolean = MessageDigest.isEqual(a, b)
    fun randomToken(bytes: Int = 32): String {
        val buf = ByteArray(bytes); rng.nextBytes(buf)
        return android.util.Base64.encodeToString(buf, android.util.Base64.URL_SAFE or android.util.Base64.NO_PADDING)
    }
    fun encryptedPrefs(context: Context): android.content.SharedPreferences {
        val master = MasterKey.Builder(context).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build()
        return EncryptedSharedPreferences.create(context, "tsar_secure_prefs", master,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM)
    }
    fun generateAesKey(): SecretKey = KeyGenerator.getInstance("AES").apply { init(256, rng) }.generateKey()
    fun aeadEncrypt(key: SecretKey, plaintext: ByteArray, aad: ByteArray): ByteArray {
        val nonce = ByteArray(12).also { rng.nextBytes(it) }
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, key, GCMParameterSpec(128, nonce)); cipher.updateAAD(aad)
        return byteArrayOf(1) + nonce + cipher.doFinal(plaintext)
    }
    fun aeadDecrypt(key: SecretKey, envelope: ByteArray, aad: ByteArray): ByteArray {
        require(envelope.size > 13 && envelope[0] == 1.toByte()) { "bad envelope" }
        val nonce = envelope.copyOfRange(1, 13); val ct = envelope.copyOfRange(13, envelope.size)
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.DECRYPT_MODE, key, GCMParameterSpec(128, nonce)); cipher.updateAAD(aad)
        return cipher.doFinal(ct)
    }
}