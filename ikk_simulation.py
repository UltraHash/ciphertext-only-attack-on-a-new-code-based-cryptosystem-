#!/usr/bin/env python
# coding: utf-8



def random_code(G):
    """
    Generate a random code from given generator matrix.
    INPUT:
    - ''G'' -- a matrix; this is a generator matrix for a code.
    OUTPUT:
    An vector with the base ring R which is a codeword of the code generated by input matrix G.
    This function uses build-in random number generator in SageMath 9.0.
    """
    v = random_vector(R, G.nrows())
    return v*G




def random_nonsingular_matrix(ring, k, n):
    """
    Generate a k x n random non singular matrix with base ring 'ring'.
    INPUT:
    - ''ring'' -- base ring for the matrix.
    - ''k'' -- number of rows of the matrix.
    - ''n'' -- number of columns of the matrix.
    OUTPUT:
    A k x n random non singular matrix with base ring 'ring'.
    This function uses build-in random number generator in SageMath 9.0.
    This function might be slow due to it generatea a whole new matrix and rejects if it is not a full rank matrix.
    """
    while True:
        G = random_matrix(ring, k, n)
        if G.rank() == min(k,n):
            return G




def key_gen(n, k):
    """
    Key generation of Ivanov, Kabatiansky and Krouk's cryptosystem (CBCrypto '20).
    For the detaile, see the proceeding or slide.
    https://cbcrypto.dii.univpm.it/program 
    This code is for the ''upgraded cryptosystem''.
    INPUT:
    - ''n'' -- code length.
    - ''k'' -- dimension of the code.
    OUTPUT:
    - ''pk'' -- a tuple including public key pk = (G1, G2).
    - ''sk'' -- a tuple including secret key sk = (G, M, T, Q, G0, J).

    This function uses build-in random number generator in SageMath 9.0.
    This function might be slow due random_nonsingular_matrix() and random_code().
    """
    G = random_nonsingular_matrix(R, k, n)
    
    G0 = zero_matrix(R, n, n)

    for i in range(G0.nrows()):
        G0[i, :] = random_code(G)
        
    J = G.pivots()
    
    T = random_nonsingular_matrix(R, n, n)
    TJ = T.matrix_from_columns(J)
    HJ = TJ.transpose().right_kernel_matrix()
    
    L = random_nonsingular_matrix(R, n, n-k)
    
    Q = L*HJ
    
    M = random_nonsingular_matrix(R, n, n)
    
    G1 = G*M
    G2 = Q*(G0 + T)*M
    
    pk = (G1, G2)
    sk = (G, M, T, Q, G0, J)
    
    return pk, sk




def enc(pk, u):
    """
    Encryption of Ivanov, Kabatiansky and Krouk's cryptosystem (CBCrypto '20).
    For the detaile, see the proceeding or slide.
    https://cbcrypto.dii.univpm.it/program 
    This code is for the ''upgraded cryptosystem''.
    INPUT:
    - ''pk'' -- A tuple including public key pk = (G1, G2).
    - ''u'' -- A vector with the same base ring with pk; The plaintext to be encrypted.
    OUTPUT:
    - ''ct'' -- A ciphertext which is an encrption of 'u' with 'pk'.

    This function uses build-in random number generator in SageMath 9.0.
    """
    (G1, G2)  = pk
    e = random_vector(R, n)
    
    ct = u*G1 + e*G2
    
    return ct
    




def dec(sk, ct):
    """
    Decryption of Ivanov, Kabatiansky and Krouk's cryptosystem (CBCrypto '20).
    For the detaile, see the proceeding or slide.
    https://cbcrypto.dii.univpm.it/program 
    This code is for the ''upgraded cryptosystem''.
    INPUT:
    - ''sk'' -- a tuple including secret key sk = (G, M, T, Q, G0, J).
    - ''ct'' -- A ciphertext.
    OUTPUT:
    A plaintext which is an decryption of 'ct' with 'sk'.

    This function uses build-in random number generator in SageMath 9.0.
    """
    (G, M, T, Q, G0, J) = sk
    y = ct*M.inverse()
    
    GJ = G.matrix_from_columns(J)
    
    ymat = matrix(R, 1, n)
    ymat[0, :] = y
    yJ = ymat.matrix_from_columns(J)
    
    eQT = y - vector(yJ*GJ.inverse()*G)
    eQ = eQT*T.inverse()
    
    eQG0 = eQ*G0
    
    uG = y - eQG0 - eQT
    
    # solving linear equation
    Gconc = G.transpose().augment(matrix(R, n, 1, uG))
    Gsoln = Gconc.rref()
    
    return vector(Gsoln[:k,-1])




def attack(pk, ct):
    """
    A ciphertext-only attack of Ivanov, Kabatiansky and Krouk's cryptosystem (CBCrypto '20).
    This cryptanalysis utilizes the linearity of encryption.
    The code is for the ''upgraded cryptosystem''.
    INPUT:
    - ''pk'' -- A tuple including public key pk = (G1, G2).
    - ''ct'' -- A ciphertext.
    OUTPUT:
    A tuple (out1, out2) for possible plaintext which is an decryption of 'ct'.
    Note that it do not requires secret key.
    The solution is given by out1 + out2*x for all x in F_{q}^{rank of out 2}.
    Usually, out2 is a zero matrix and thus there are one and only possible plaintext.

    This function uses build-in random number generator in SageMath 9.0.
    """
    (G1, G2)  = pk
    
    G1t = G1.transpose()
    G2red = G2.rref()[:n-k, :]
    G2t = G2red.transpose()
    
    Gmult = G1t.augment(G2t)
    
    rank = Gmult.rank()
    
    # solving Gmult*(u|e') = ct
    Gaug = Gmult.augment(matrix(R, n, 1, ct))
    Gsoln = Gaug.rref()
    
    return Gsoln[:k, -1], Gsoln[:k, rank:-1]
    




import time

def test():
    """
    Iterates each step and time it.

    This function uses build-in random number generator in SageMath 9.0.
    """
    fail = 0
    keygen_time = []
    enc_time = []
    dec_time = []
    attack_time = []
    
    for i in range(100):
        t0 = time.time()
        #
        pk, sk = key_gen(n, k)
        #
        t1 = time.time()
        keygen_time.append(t1-t0)
        
           
        u = random_vector(R, k)
        
        t0 = time.time()
        #
        ct = enc(pk, u)
        #
        t1 = time.time()
        enc_time.append(t1-t0)
        
        t0 = time.time()
        #
        u0 = dec(sk, ct)
        #
        t1 = time.time()
        dec_time.append(t1-t0)
        
        t0 = time.time()
        #
        sln1, sln2 = attack(pk, ct)
        #
        t1 = time.time()
        attack_time.append(t1-t0)
        
        
        num_of_sol = sln2.ncols()

        if num_of_sol != 0:
            fail += 1
            
    return keygen_time ,enc_time, dec_time, attack_time, fail




q = 2
R = GF(q)




n = 1024
k = 524
t = 50


def run():

    pk, sk = key_gen(n, k)

    u = random_vector(R, k)
    ct = enc(pk, u)

    dec(sk, ct) == u

    sln1, sln2 = attack(pk, ct)

    num_of_sol = sln2.ncols()

    times = test()

    print("Key Generation: %s s"%(sum(times[0])/len(times[0])))
    print("Encryption: %s s"%(sum(times[1])/len(times[1])))
    print("Decryption: %s s"%(sum(times[2])/len(times[2])))
    print("Attack: %s s"%(sum(times[3])/len(times[3])))
    print("Number of Failure: %s"%(times[-1]))

