# Ciphertext-only Attack on ''A New Code-based Cryptosystem (CBCrypto '20)''
A proof-of-concept implementation for ''A New Code-based Cryptosystem (CBCrypto '20)" and ciphertext-only attack on  it.

The code is written for SageMath 9.0.
USAGE:
- - -
```
sage: load('ikk_simulation.py')
sage: pk, sk = key_gen(n, k)
sage: u = random_vector(R, k)
sage: ct = enc(pk, u)
sage: dec(sk, ct) == u
True
sage: sln1, sln2 = attack(pk, ct)
sage: vector(sln1) == u
True
```
