// TSAR reference implementation: Flutter secure patterns.
// Dependencies: flutter_secure_storage, cryptography, http, uri
import 'dart:convert';
import 'dart:typed_data';

import 'package:cryptography/cryptography.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

const _storage = FlutterSecureStorage(
  aOptions: AndroidOptions(encryptedSharedPreferences: true),
  iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock_this_device),
);

class SecureStore {
  static Future<void> write(String key, String value) =>
      _storage.write(key: key, value: value);

  static Future<String?> read(String key) => _storage.read(key: key);

  static Future<void> delete(String key) => _storage.delete(key: key);
}

class AeadBox {
  final SecretKey _key;

  AeadBox(Uint8List keyBytes)
      : _key = SecretKey(keyBytes),
        assert(keyBytes.length == 32, 'key must be 32 bytes');

  Future<Uint8List> encrypt(Uint8List plaintext, Uint8List aad) async {
    final algo = AesGcm.with256bits();
    final nonce = algo.newNonce();
    final box = await algo.encrypt(plaintext, secretKey: _key, nonce: nonce, aad: aad);
    final out = BytesBuilder();
    out.addByte(1);
    out.add(nonce);
    out.add(box.cipherText);
    out.add(box.mac.bytes);
    return out.toBytes();
  }

  Future<Uint8List> decrypt(Uint8List envelope, Uint8List aad) async {
    if (envelope.isEmpty || envelope[0] != 1) {
      throw ArgumentError('bad envelope');
    }
    final algo = AesGcm.with256bits();
    final nonceLen = algo.nonceLength;
    final macLen = algo.macAlgorithm.macLength;
    final nonce = envelope.sublist(1, 1 + nonceLen);
    final ct = envelope.sublist(1 + nonceLen, envelope.length - macLen);
    final mac = Mac(envelope.sublist(envelope.length - macLen));
    final box = SecretBox(ct, nonce: nonce, mac: mac);
    final clear = await algo.decrypt(box, secretKey: _key, aad: aad);
    return Uint8List.fromList(clear);
  }
}

Future<Map<String, dynamic>> apiPost(
  Uri baseUrl,
  String path,
  Map<String, dynamic> body,
) async {
  final token = await SecureStore.read('api_token');
  if (token == null) throw StateError('unauthenticated');
  final uri = baseUrl.replace(path: path);
  if (uri.host != baseUrl.host) throw StateError('cross-origin blocked');
  final res = await http.post(
    uri,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    },
    body: jsonEncode(body),
  );
  if (res.statusCode != 200) throw StateError('api ${res.statusCode}');
  return jsonDecode(res.body) as Map<String, dynamic>;
}

final _allowedActions = {'read', 'list', 'search'};

bool authorize(String action, String userSub, String ownerId, Set<String> roles) {
  if (!_allowedActions.contains(action)) return false;
  if (userSub == ownerId) return true;
  return roles.contains('admin');
}
