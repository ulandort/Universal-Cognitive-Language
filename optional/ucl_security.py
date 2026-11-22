#!/usr/bin/env python3
"""EXPERIMENTAL optional UCL transport encryption; not security-audited.

Keeps existing UCL payload bytes unchanged; encrypted envelope carries only
versioned cryptographic metadata + ciphertext. Python cryptography and argon2-cffi.
"""
import base64
import json
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
from argon2.low_level import Type, hash_secret_raw

PROFILE = 'UCL-ENCRYPTED/0.1-preview'
MAX_PLAINTEXT_BYTES = 2_000_000
MAX_ENVELOPE_BYTES = 3_000_000
SALT_BYTES = 16
NONCE_BYTES = 12
KEY_BYTES = 32
ARGON_MEMORY_KIB = 65536
ARGON_ITERATIONS = 3
ARGON_PARALLELISM = 1

class DecryptionError(ValueError):
    pass

def _b64(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')

def _decode(s, length=None):
    if not isinstance(s,str) or not s or any(c not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_' for c in s) or len(s)%4 == 1:
        raise ValueError('invalid base64url')
    try:
        b=base64.urlsafe_b64decode(s + '=' * (-len(s)%4))
    except Exception as e:
        raise ValueError('invalid base64url') from e
    if _b64(b) != s or (length is not None and len(b)!=length):
        raise ValueError('invalid base64url size or encoding')
    return b

def _canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(',', ':'),ensure_ascii=True,allow_nan=False).encode('ascii')

def _password_key(password, salt):
    if not isinstance(password,str) or not password:
        raise ValueError('nonempty unicode password required')
    # Password encoding and normalization are specified; intentionally NO unicode normalization.
    raw=password.encode('utf-8')
    if len(raw)>4096:
        raise ValueError('password too long')
    return hash_secret_raw(raw,salt,time_cost=ARGON_ITERATIONS,memory_cost=ARGON_MEMORY_KIB,
                           parallelism=ARGON_PARALLELISM,hash_len=KEY_BYTES,type=Type.ID)

def _validate_raw_key(key):
    if not isinstance(key,bytes) or len(key)!=KEY_BYTES:
        raise ValueError('direct encryption key must be exactly 32 bytes')
    return key

def _metadata(mode, salt=None):
    meta={'profile':PROFILE,'cipher':'AES-256-GCM','mode':mode,'nonce':_b64(os.urandom(NONCE_BYTES))}
    if mode=='password':
        meta['kdf']={'name':'Argon2id','version':19,'memory_kib':ARGON_MEMORY_KIB,
                     'iterations':ARGON_ITERATIONS,'parallelism':ARGON_PARALLELISM,
                     'salt':_b64(salt)}
    else:
        meta['kdf']=None
    return meta

def encrypt(plaintext, *, password=None, key=None):
    """Return a portable envelope JSON string. Supply exactly one secret type."""
    if (password is None)==(key is None):
        raise ValueError('provide password XOR key')
    if not isinstance(plaintext,bytes) or len(plaintext)>MAX_PLAINTEXT_BYTES:
        raise ValueError('plaintext must be bytes within limit')
    if password is not None:
        salt=os.urandom(SALT_BYTES)
        derived=_password_key(password,salt)
        metadata=_metadata('password',salt)
    else:
        derived=_validate_raw_key(key)
        metadata=_metadata('direct-key')
    aad=b'UCL-ENVELOPE-AAD-1\n'+_canonical(metadata)
    ciphertext=AESGCM(derived).encrypt(_decode(metadata['nonce'],NONCE_BYTES), plaintext,aad)
    return _canonical(dict(metadata,ciphertext=_b64(ciphertext))).decode('ascii')

def decrypt(envelope, *, password=None, key=None):
    """Return unchanged UCL plaintext; wrong secret or modified envelope raises DecryptionError."""
    if (password is None)==(key is None):
        raise ValueError('provide password XOR key')
    if isinstance(envelope,str):
        raw=envelope.encode('utf-8')
    elif isinstance(envelope,bytes):
        raw=envelope
    else:
        raise ValueError('envelope must be UTF-8 JSON text')
    if len(raw)>MAX_ENVELOPE_BYTES:
        raise ValueError('envelope too large')
    try:
        data=json.loads(raw)
        if not isinstance(data,dict) or set(data)!={'profile','cipher','mode','nonce','kdf','ciphertext'}:
            raise ValueError('invalid envelope fields')
        if data['profile']!=PROFILE or data['cipher']!='AES-256-GCM':
            raise ValueError('unsupported cryptographic profile')
        nonce=_decode(data['nonce'],NONCE_BYTES)
        ciphertext=_decode(data['ciphertext'])
        if len(ciphertext)<16 or len(ciphertext)>MAX_PLAINTEXT_BYTES+16:
            raise ValueError('invalid ciphertext length')
        if data['mode']=='password' and password is not None:
            kdf=data['kdf']
            expected={'name':'Argon2id','version':19,'memory_kib':ARGON_MEMORY_KIB,
                      'iterations':ARGON_ITERATIONS,'parallelism':ARGON_PARALLELISM}
            if not isinstance(kdf,dict) or set(kdf)!=set(expected)|{'salt'} or any(kdf[x]!=v or type(kdf[x]) is not type(v) for x,v in expected.items()):
                raise ValueError('unsupported KDF profile')
            salt=_decode(kdf['salt'],SALT_BYTES)
            derived=_password_key(password,salt)
        elif data['mode']=='direct-key' and key is not None and data['kdf'] is None:
            derived=_validate_raw_key(key)
        else:
            raise ValueError('wrong key mode')
        metadata={k:v for k,v in data.items() if k!='ciphertext'}
        aad=b'UCL-ENVELOPE-AAD-1\n'+_canonical(metadata)
        return AESGCM(derived).decrypt(nonce,ciphertext,aad)
    except (InvalidTag,ValueError,TypeError,UnicodeError,KeyError) as e:
        raise DecryptionError('unable to decrypt: wrong secret, corrupted envelope, or unsupported parameters') from e

if __name__=='__main__':
    import argparse,getpass,sys
    p=argparse.ArgumentParser(description='EXPERIMENTAL optional UCL encryption envelope')
    p.add_argument('operation',choices=['encrypt','decrypt'])
    p.add_argument('input_file');p.add_argument('output_file')
    p.add_argument('--direct-key-env',help='environment variable with 43-char unpadded base64url key')
    a=p.parse_args()
    if a.direct_key_env:
        secret={'key':_decode(os.environ[a.direct_key_env],KEY_BYTES)}
    else:
        secret={'password':getpass.getpass('Password: ')}
    with open(a.input_file,'rb') as f: source=f.read()
    result=encrypt(source,**secret).encode('ascii') if a.operation=='encrypt' else decrypt(source,**secret)
    with open(a.output_file,'wb') as f: f.write(result)
    print('Wrote',a.output_file)
