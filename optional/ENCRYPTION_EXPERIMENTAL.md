# UCL — Optional private-message envelope (experimental v0.18 security profile)

**Experimental optional profile packaged with UCL/1.0; it is NOT part of the frozen core 1.0 wire format and is NOT an independently audited security standard.**

## Purpose and scope

UCL is primarily an open, self-contained communication language. The eleven core symbols, four-layer body, declarations, history, acknowledgements, and optional proofs are unchanged by encryption. **Encryption is an optional outer transport envelope** around the entire original byte-for-byte UCL message; cleartext UCL remains the default and remains valid. Decryption yields the original unmodified UCL byte stream, which then undergoes ordinary independent UCL validation.

An encrypted message is intentionally unreadable without a separately distributed secret. Therefore **cryptographic access is an explicit exception to no-prior-context interpretation**, not to the requirement that the *decrypted content* be independently self-contained. No server, central conversation participant, or previous messages are required after the secret is provided. The language protocol does not manage delivery or recovery of passwords.

## Selected algorithms

- **Authenticated encryption:** AES-256-GCM with a *fresh uniformly random 96-bit nonce for every encryption using a given key*. Never repeat a nonce/key pair. The current implementation uses a cryptographically secure OS RNG.
- **Password mode KDF:** Argon2id v1.3 (version 19), memory 65,536 KiB, iterations 3, parallelism 1, output 32 bytes, fresh 16-byte salt. Parameters must be reviewed for user devices and updated by defining a new versioned profile, rather than accepting arbitrary attacker-specified work factors. Password text is encoded as UTF-8 exactly, without implicit Unicode normalization; this makes exact character sequence important.
- **Direct-key mode:** A separately supplied uniformly random 32-byte key; no KDF. **Never** use a weak human password as a direct key.
- **Integrity:** GCM authentication covers the ciphertext and canonicalized header as additional authenticated data (AAD). Authentication failure, wrong password or unsupported profile all prevent decryption. Encrypting does not authenticate the named sender; signatures would be a separate optional feature.

## Experimental envelope schema

UTF-8 JSON containing exactly these six keys: `profile`, `cipher`, `mode`, `nonce`, `kdf`, `ciphertext`. `profile` is `UCL-ENCRYPTED/0.1-preview`; `cipher` is `AES-256-GCM`; `mode` is `password` or `direct-key`.

- `nonce`, `ciphertext`, and password `kdf.salt`: *unpadded base64url*.
- Password `kdf`: `{ "name":"Argon2id", "version":19, "memory_kib":65536, "iterations":3, "parallelism":1, "salt":"..." }`.
- Direct-key `kdf`: JSON `null`.
- Ciphertext includes the 16-byte GCM authentication tag appended to the encrypted data.
- AAD: ASCII prefix `UCL-ENVELOPE-AAD-1\n` followed by canonical JSON encoding of the five envelope fields *other than* `ciphertext`. This code uses sorted keys, ASCII-escaped strings, no whitespace, `allow_nan=False`. **This optional envelope remains experimental and is not claimed to have independent cross-language interoperability.**
- Local preview limits: input plaintext <=2 MB, envelope <=3 MB. Limits are safety choices, not the proposed permanent universal language limits. They must be reconciled with UCL's own inner-message limits.

Cleartext message metadata, key recipients, filenames, routing addresses and message length are not protected by this envelope if exposed separately by the transport. The encrypted JSON still reveals the algorithm, password-vs-key mode, salt/nonce and approximate message size. Password strength and out-of-band secret transfer remain crucial; weak passwords are susceptible to offline guessing. Encryption cannot prevent a recipient from sharing or modifying plaintext after decryption.

## Required receiver behavior

1. Detect the explicit `UCL-ENCRYPTED` outer profile, not by guessing whether bytes 'look encrypted'.
2. Check envelope byte size, schema, profile, base64url and fixed KDF parameters **before** expensive key derivation or decryption.
3. Obtain the secret from a secure out-of-band channel. Never include it in UCL's content, share it in an untrusted message, or put it in a URL.
4. Verify AEAD authentication while decrypting. On failure, do not interpret or return partial plaintext; use a generic failure response to avoid leaking details.
5. Validate decrypted UCL normally; authenticated encryption does not make its claims, embedded instructions or purported authorship trustworthy.

## CLI demo (experimental)

Install Python `cryptography` and `argon2-cffi`. Usage:

```bash
python optional/ucl_security.py encrypt existing_ucl_message.txt private.uclenc
python optional/ucl_security.py decrypt private.uclenc restored_ucl_message.txt
```

Passwords are entered through a masked terminal prompt, not a command-line flag. For direct-key use, supply a 32-byte random key encoded as 43-character unpadded base64url in a designated environment variable, and pass `--direct-key-env VARIABLE_NAME`. Environment variables are convenient for testing but not a full secret-management system; production implementations should use platform secret storage. No sample encrypted message includes an actual password.

## Limitations and future security review

This is **prototype code, not an audited encryption product**. Required next steps include independently checking an implementation in another language against deterministic interoperability test vectors (explicitly marked *test-only* fixed salt/nonce); platform memory constraints and denial-of-service handling; secret-handling and exception-flow audit; versioned crypto-agility policy; guidance on key rotation and compromise; and a test proving exact byte-for-byte recovery of complete standalone UCL packets. Password-mode test fixtures must never publish real passwords or suggest that embedded passwords are secure.

## Optional future feature (not part of current profile)

Digital signatures to authenticate a sender and the origin of signed UCL claims. Encryption protects confidentiality and tamper-detection against parties without the key, **not authorship**. Public signatures could be added without changing the eleven-symbol language core.