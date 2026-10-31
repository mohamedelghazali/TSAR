# TSAR Anti-Pattern Examples (Do Not Use)

Each example is followed by the violation and the secure replacement.

## 1. SQL Injection (Python)
```python
# VIOLATION: A03 Injection
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# SECURE
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

## 2. Hardcoded Secret (Node.js)
```javascript
// VIOLATION: hardcoded credential
const JWT_SECRET = "super-secret-key-change-me";

// SECURE
const JWT_SECRET = Buffer.from(process.env.TSAR_JWT_SECRET, 'base64');
```

## 3. Weak Hashing (Java)
```java
// VIOLATION: CWE-916
String hash = DigestUtils.md5Hex(password);

// SECURE
String hash = argon2.hash(password);
```

## 4. ECB Mode (Python)
```python
# VIOLATION: ECB mode
cipher = Cipher(algorithms.AES(key), modes.ECB())

# SECURE
cipher = Cipher(algorithms.AES(key), modes.GCM(nonce))
```

## 5. Insecure Random (Python)
```python
# VIOLATION: predictable token
token = str(random.randint(100000, 999999))

# SECURE
token = secrets.token_urlsafe(32)
```

## 6. Timing Attack on Token (Go)
```go
// VIOLATION: early-exit comparison
if storedToken == providedToken { return true }

// SECURE
if subtle.ConstantTimeCompare([]byte(storedToken), []byte(providedToken)) == 1 { return true }
```

## 7. TLS Verification Disabled (Node.js)
```javascript
// VIOLATION: TLS bypass
https.get(url, { rejectUnauthorized: false }, ...)

// SECURE
https.get(url, ...)
```

## 8. Command Injection (Node.js)
```javascript
// VIOLATION: A03
exec(`convert ${userPath} out.png`);

// SECURE
execFile('convert', [userPath, 'out.png']);
```

## 9. Path Traversal (Python)
```python
# VIOLATION: A01
open(os.path.join(BASE, user_filename)).read()

# SECURE
safe = (Path(BASE) / user_filename).resolve()
if not str(safe).startswith(str(Path(BASE).resolve())):
    raise ValueError("invalid path")
open(safe).read()
```

## 10. SSRF (Node.js)
```javascript
// VIOLATION: A10
axios.get(req.body.url);

// SECURE
const ALLOWED = new Set(['api.trusted.example']);
const u = new URL(req.body.url);
if (!ALLOWED.has(u.hostname)) throw new Error('blocked');
axios.get(u.toString());
```

## 11. Prompt Injection (LLM)
```python
# VIOLATION: LLM01
prompt = f"{system_instructions}\n\nUser: {user_input}"

# SECURE
messages = [
    {"role": "system", "content": system_instructions},
    {"role": "user", "content": f"<untrusted>{user_input}</untrusted>"},
]
```

## 12. Hardcoded Agent Permissions
```yaml
# VIOLATION: LLM03 Excessive Agency
agent:
  tools: ["*"]
  credentials: "long-lived-prod-token"

# SECURE
agent:
  tools: ["db.read"]
  credentials: { source: "vault", ttl_seconds: 900 }
```

## 13. Weak Password Reset
```python
# VIOLATION: predictable reset token
reset_token = hashlib.md5(user.email.encode()).hexdigest()

# SECURE
reset_token = secrets.token_urlsafe(32)
store_in_db(reset_token, user_id, ttl_seconds=900)
```

## 14. Logging Sensitive Data
```python
# VIOLATION: A09
logger.info(f"login: {email} password={password} token={token}")

# SECURE
logger.info({"event": "login", "user": hashlib.sha256(email.encode()).hexdigest()[:16], "outcome": "ok"})
```

## 15. Mass Assignment (Node.js)
```javascript
// VIOLATION: A01
User.update(req.body);

// SECURE
const { name, email } = pick(req.body, ['name', 'email']);
User.update({ name, email });
```
