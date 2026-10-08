"""Windows current-user DPAPI store; never expose plaintext through logs or HTTP."""
import ctypes, json, os
from ctypes import wintypes
from pathlib import Path

PATH=Path(__file__).resolve().parent/'.eudic-auth.bin'
class Blob(ctypes.Structure):
    _fields_=[('size',wintypes.DWORD),('data',ctypes.POINTER(ctypes.c_ubyte))]

def crypt(data,encrypt):
    if os.name!='nt':raise RuntimeError('Credential storage requires Windows')
    buf=ctypes.create_string_buffer(data)
    src=Blob(len(data),ctypes.cast(buf,ctypes.POINTER(ctypes.c_ubyte)));out=Blob()
    lib=ctypes.WinDLL('crypt32',use_last_error=True)
    fn=lib.CryptProtectData if encrypt else lib.CryptUnprotectData
    fn.restype=wintypes.BOOL
    ok=fn(ctypes.byref(src),None,None,None,None,1,ctypes.byref(out))
    if not ok:raise ctypes.WinError(ctypes.get_last_error())
    try:return ctypes.string_at(out.data,out.size)
    finally:
        free=ctypes.WinDLL('kernel32').LocalFree
        free.argtypes=[ctypes.c_void_p];free.restype=ctypes.c_void_p
        free(out.data)

def save(token,target=None):
    data=crypt(json.dumps({'token':token,'target':target}).encode('utf-8'),True)
    temp=PATH.with_suffix('.tmp');temp.write_bytes(data);temp.replace(PATH)

def load():
    if not PATH.exists():return {}
    return json.loads(crypt(PATH.read_bytes(),False))

def forget():
    PATH.unlink(missing_ok=True)
