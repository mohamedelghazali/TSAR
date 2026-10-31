// TSAR reference implementation: Swift/iOS secure patterns.
// Dependencies: CryptoKit (Apple), Argon2Swift (or libsodium via SwiftPM)
import Foundation
import CryptoKit
import Security
enum SecureApp {
    enum SecureError: Error { case weakPassword; case keychainFailure(OSStatus); case cryptoFailure; case badEnvelope }
    static func hashPassword(_ password: String) throws -> String {
        guard password.count >= 12 else { throw SecureError.weakPassword }
        // Use Argon2id via a vetted library (Argon2Swift) in production.
        // Placeholder uses PBKDF2 only as a compile-time stub; do not ship as-is.
        let salt = randomBytes(16); var derived = [UInt8](repeating: 0, count: 32)
        let status = password.data(using: .utf8)!.withUnsafeBytes { pwPtr in
            CCKeyDerivationPBKDF(CCPBKDFAlgorithm(kCCPBKDF2), pwPtr.bindMemory(to: Int8.self).baseAddress!,
                password.utf8.count, salt, salt.count, CCPseudoRandomAlgorithm(kCCPRFHmacAlgSHA256),
                600_000, &derived, derived.count)
        }
        guard status == kCCSuccess else { throw SecureError.cryptoFailure }
        return Data(salt).base64EncodedString() + ":" + Data(derived).base64EncodedString()
    }
    static func randomBytes(_ count: Int) -> Data {
        var data = Data(count: count)
        _ = data.withUnsafeMutableBytes { SecRandomCopyBytes(kSecRandomDefault, count, $0.baseAddress!) }
        return data
    }
    static func constantTimeEqual(_ a: Data, _ b: Data) -> Bool {
        guard a.count == b.count else { return false }
        return a.withUnsafeBytes { ap in b.withUnsafeBytes { bp in timingSafeEqual(ap, bp) } }
    }
    private static func timingSafeEqual(_ a: UnsafeRawBufferPointer, _ b: UnsafeRawBufferPointer) -> Bool {
        var diff: UInt8 = 0
        for i in 0..<a.count { diff |= a[i] ^ b[i] }
        return diff == 0
    }
    static func aeadEncrypt(_ key: SymmetricKey, plaintext: Data, aad: Data) throws -> Data {
        let sealed = try AES.GCM.seal(plaintext, using: key, authenticating: aad)
        guard let combined = sealed.combined else { throw SecureError.cryptoFailure }
        return Data([1]) + combined
    }
    static func aeadDecrypt(_ key: SymmetricKey, envelope: Data, aad: Data) throws -> Data {
        guard envelope.first == 1, envelope.count > 1 else { throw SecureError.badEnvelope }
        let box = try AES.GCM.SealedBox(combined: envelope.dropFirst())
        return try AES.GCM.open(box, using: key, authenticating: aad)
    }
    static func storeInKeychain(account: String, secret: Data) throws {
        let query: [String: Any] = [kSecClass as String: kSecClassGenericPassword, kSecAttrAccount as String: account,
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly, kSecValueData as String: secret]
        SecItemDelete(query as CFDictionary)
        let status = SecItemAdd(query as CFDictionary, nil)
        guard status == errSecSuccess else { throw SecureError.keychainFailure(status) }
    }
    static func enclaveKey() throws -> SecKey {
        var error: Unmanaged<CFError>?
        guard let access = SecAccessControlCreateWithFlags(nil, kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
            [.privateKeyUsage, .biometryCurrentSet], &error) else { throw SecureError.cryptoFailure }
        let attrs: [String: Any] = [kSecAttrKeyType as String: kSecAttrKeyTypeECSECPrimeRandom,
            kSecAttrKeySizeInBits as String: 256, kSecAttrTokenID as String: kSecAttrTokenIDSecureEnclave,
            kSecPrivateKeyAttrs as String: [kSecAttrIsPermanent as String: true, kSecAttrAccessControl as String: access]]
        guard let key = SecKeyCreateRandomKey(attrs as CFDictionary, &error) else { throw SecureError.cryptoFailure }
        return key
    }
}