## pip install时 报错提示"module 'lib' has no attribute 'X509_V_FLAG_NOTIFY_POLICY'"

```
  File "/usr/lib/python3/dist-packages/OpenSSL/__init__.py", line 8, in <module>
    from OpenSSL import crypto, SSL
  File "/usr/lib/python3/dist-packages/OpenSSL/crypto.py", line 1553, in <module>
    class X509StoreFlags(object):
  File "/usr/lib/python3/dist-packages/OpenSSL/crypto.py", line 1571, in X509StoreFlags
    NOTIFY_POLICY = _lib.X509_V_FLAG_NOTIFY_POLICY
AttributeError: module 'lib' has no attribute 'X509_V_FLAG_NOTIFY_POLICY'
```

临时解决: 重命名crypto.py可临时解决
```sh
mv "/usr/lib/python3/dist-packages/OpenSSL/crypto.py" "/usr/lib/python3/dist-packages/OpenSSL/crypto.py.bak"
```

## 相关链接
[ansible 问题处理 AttributeError: module ‘lib‘ has no attribute ‘X509_V_FLAG_NOTIFY_POLICY‘](https://blog.csdn.net/weixin_40548182/article/details/141133991)
