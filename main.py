#pip install pycryptodome imageio matplotlib

import rng
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Hash import SHA3_256
from Crypto.Signature import pkcs1_15

# default values
img_filename = 'lena.png'
input_filename = ''
public_key_filename = 'public.pem'
private_key_filename = 'private.pem'
encrypted_input_filename = ''
decrypted_input_filename = ''
sign_filename = ''

def my_input(default_filename, message = 'Input a filename: '):
    filename = input(f"{message}[{default_filename}]: ")
    if filename == '':
        return default_filename
    else:
        return filename

def generate_sign():
    global input_filename
    global private_key_filename
    global sign_filename

    file_hash = SHA3_256.new()
    
    input_filename = my_input(input_filename)
    sign_filename = 'sign_' + input_filename
    private_key_filename = my_input(private_key_filename, 'Input private key filename: ')
    sign_filename = my_input(sign_filename, 'Input name for sign file: ')

    # generating hash; reading file in a binary mode
    with open(input_filename,'rb') as file:
        chunk = 0
        # until eof
        while chunk != b'':
            # read only 1024 bytes to avoid overloading memory in case of a big file
            chunk = file.read(1024)
            file_hash.update(chunk)

    key = RSA.import_key(open(private_key_filename).read())
    signature = pkcs1_15.new(key).sign(file_hash)

    # save sign to a file
    with open(sign_filename, 'wb') as file:
        file.write(signature)
                
    return signature

def encrypt_file(img):
    global input_filename
    global public_key_filename
    global encrypted_input_filename

    input_filename = my_input(input_filename, 'Input name of a file to encrypt: ')
    public_key_filename = my_input(public_key_filename, 'Input public key filename: ')
    encrypted_input_filename = 'encrypted_' + input_filename
    encrypted_input_filename = my_input(encrypted_input_filename, 'Input name for encrypted file: ')

    with open(input_filename, 'rb') as f:
        data = f.read()

    file_out = open(encrypted_input_filename, "wb")

    recipient_key = RSA.import_key(open(public_key_filename).read())
    session_key = img.generateBytes(16)

    # Encrypt the session key with the public RSA key
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    enc_session_key = cipher_rsa.encrypt(session_key)

    # Encrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(data)
    [ file_out.write(x) for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext) ]
    file_out.close()

    return

def decrypt_file():
    global private_key_filename
    global encrypted_input_filename
    global decrypted_input_filename

    private_key_filename = my_input(private_key_filename, 'Input private key filename: ')
    encrypted_input_filename = my_input(encrypted_input_filename, 'Input encrypted data filename: ')
    decrypted_input_filename = 'decrypted_' + input_filename
    decrypted_input_filename = my_input(decrypted_input_filename, 'Input name for decrypted file: ')

    file_in = open(encrypted_input_filename, "rb")
    private_key = RSA.import_key(open(private_key_filename).read())

    enc_session_key, nonce, tag, ciphertext = \
    [ file_in.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1) ]

    # Decrypt the session key with the private RSA key
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)

    # Decrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    data = cipher_aes.decrypt_and_verify(ciphertext, tag)

    f = open(decrypted_input_filename, 'wb')
    f.write(data)
    f.close()
    return

def generate_rsa_keys(img):
    global private_key_filename
    global public_key_filename

    private_key_filename = my_input(private_key_filename, 'Input name for private key: ')
    public_key_filename = my_input(public_key_filename, 'Input name for public key: ')

    key = RSA.generate(2048, img.generateBytes)
    private_key = key.export_key()
    file_out = open(private_key_filename, "wb")
    file_out.write(private_key)
    file_out.close()

    public_key = key.publickey().export_key()
    file_out = open(public_key_filename, "wb")
    file_out.write(public_key)
    file_out.close()
    return 

def compare_hash():
    global sign_filename
    global public_key_filename
    global input_filename

    # input
    sign_filename = my_input(sign_filename, 'Input sign filename to decrypt: ')
    public_key_filename = my_input(public_key_filename, 'Input public key filename: ')
    input_filename = my_input(input_filename, 'Input filename to check hash: ')
    file_hash = SHA3_256.new()

    key = RSA.import_key(open(public_key_filename).read())
    
    with open(input_filename,'rb') as file:
        chunk = 0
        # until eof
        while chunk != b'':
            # read only 1024 bytes to avoid overloading memory in case of a big file
            chunk = file.read(1024)
            file_hash.update(chunk)
    
    with open(sign_filename, 'rb') as file:
        signature = file.read()
            
    try:
        pkcs1_15.new(key).verify(file_hash, signature)
        print("The signature is valid.")
    except (ValueError, TypeError):
       print("The signature is not valid.")

    return

def main():
    global img_filename

    print('Data encryption with RSA/AES using image as a RNG source')
    print('by Maciej Wegrzak 2022 \n')

    img_filename = my_input(img_filename, 'Input an image filename: ')
    print('Provide parameters for the logistic map to shuffle image') 
    print('Important!')
    print('Growth parameter r should be between 3.6 and 3.99')
    print('x0 and y0 should be between 0 and 0.99 \n')
    r = float(input('r = '))
    x0 = float(input('x0 = '))
    y0 = float(input('y0 = '))

    myImg = rng.Rng(img_filename, r, x0, y0)
    while(True):
        print('\n')
        print('1 - Display histograms of original and shuffled images')
        print('2 - Shuffle entropy source (image) with different parameters r, x0, y0')
        print("3 - Generate RSA keys")
        print("4 - Generate digital sign")
        print("5 - Check sign")
        print("6 - Encrypt file")
        print("7 - Decrypt file")
        print("0 - Exit")

        choice = input("Choose option: ")
        print('\n')
        match choice :
            case '1':
                myImg.dispImgHist()
            case '2':
                r = float(input('Growth parameter r = '))
                x0 = float(input('x0 = '))
                y0 = float(input('y0 = '))
                myImg.shuffle(r, x0, y0)
            case '3':
                print(f'Generating RSA keys. \n Parameters used for {img_filename} are: r = {r} x0 = {x0} y0 = {y0}')
                generate_rsa_keys(myImg)
            case '4':
                print(generate_sign())
            case '5':
                compare_hash()
            case '6':
                encrypt_file(myImg)
            case '7':
                decrypt_file()
            case '0':
                return 0

    
if __name__ == '__main__':
    main()
