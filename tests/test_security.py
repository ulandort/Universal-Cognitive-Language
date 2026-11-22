import copy,json,os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"optional"))
from ucl_security import encrypt,decrypt,DecryptionError,_b64,_decode

class EncryptionTests(unittest.TestCase):
    def setUp(self):
        self.message=b'BEGIN_UCL_PAYLOAD\nhello\nEND_UCL_PAYLOAD\n'
        self.key=os.urandom(32)
    def test_password_roundtrip(self):
        self.assertEqual(decrypt(encrypt(self.message,password='correct horse battery staple'),password='correct horse battery staple'),self.message)
    def test_direct_key_roundtrip(self):
        self.assertEqual(decrypt(encrypt(self.message,key=self.key),key=self.key),self.message)
    def test_wrong_password(self):
        with self.assertRaises(DecryptionError): decrypt(encrypt(self.message,password='one'),password='two')
    def test_wrong_key(self):
        with self.assertRaises(DecryptionError): decrypt(encrypt(self.message,key=self.key),key=os.urandom(32))
    def test_unique_nonce(self):
        a=json.loads(encrypt(self.message,key=self.key));b=json.loads(encrypt(self.message,key=self.key))
        self.assertNotEqual(a['nonce'],b['nonce']);self.assertNotEqual(a['ciphertext'],b['ciphertext'])
    def test_unique_password_salt(self):
        a=json.loads(encrypt(self.message,password='x'));b=json.loads(encrypt(self.message,password='x'))
        self.assertNotEqual(a['kdf']['salt'],b['kdf']['salt'])
    def test_tampered_ciphertext(self):
        d=json.loads(encrypt(self.message,key=self.key));c=bytearray(_decode(d['ciphertext']));c[0]^=1;d['ciphertext']=_b64(c)
        with self.assertRaises(DecryptionError):decrypt(json.dumps(d),key=self.key)
    def test_tampered_metadata(self):
        d=json.loads(encrypt(self.message,key=self.key));d['nonce']=_b64(os.urandom(12))
        with self.assertRaises(DecryptionError):decrypt(json.dumps(d),key=self.key)
    def test_unknown_field(self):
        d=json.loads(encrypt(self.message,key=self.key));d['override']='bad'
        with self.assertRaises(DecryptionError):decrypt(json.dumps(d),key=self.key)
    def test_wrong_mode(self):
        with self.assertRaises(DecryptionError):decrypt(encrypt(self.message,key=self.key),password='x')
    def test_mixed_credentials_rejected(self):
        with self.assertRaises(ValueError):encrypt(self.message,password='x',key=self.key)
    def test_invalid_key_length(self):
        with self.assertRaises(ValueError):encrypt(self.message,key=b'x'*16)
    def test_empty_message(self):
        self.assertEqual(decrypt(encrypt(b'',key=self.key),key=self.key),b'')
    def test_binary_message(self):
        payload=bytes(range(256))*100
        self.assertEqual(decrypt(encrypt(payload,key=self.key),key=self.key),payload)
    def test_unicode_password_exact(self):
        s='pa\u0301ss';e=encrypt(self.message,password=s)
        self.assertEqual(decrypt(e,password=s),self.message)
        with self.assertRaises(DecryptionError):decrypt(e,password='p\u00e1ss')
    def test_oversized_input(self):
        with self.assertRaises(ValueError):encrypt(b'a'*2_000_001,key=self.key)
    def test_oversized_envelope(self):
        with self.assertRaises(ValueError):decrypt(b'a'*3_000_001,key=self.key)

if __name__=='__main__':unittest.main()
