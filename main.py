#pip install pycryptodome hashlib matplotlib imageio

from os.path import exists
import hashlib
import rng
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP

# default values
img_filename = ''
input_filename = ''
public_key_filename = 'public.pem'
private_key_filename = 'private.pem'
encrypted_input_filename = ''
decrypted_input_filename = ''

def my_input(default_filename, message = 'Input a filename: '):
    filename = input(f"{message}[{default_filename}]: ")
    if filename == '':
        return default_filename
    else:
        return filename

def hash_file():
    global input_filename
    my_hash = hashlib.sha3_256()
    input_filename = my_input(input_filename)

    # reading file in binary mode
    with open(input_filename,'rb') as file:
        chunk = 0
        # until eof
        while chunk != b'':
            # read only 1024 bytes to avoid overloading memory in case of a big file
            chunk = file.read(1024)
            my_hash.update(chunk)

    return my_hash.hexdigest()

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

def main():
    global img_filename


    print('Data encryption with RSA/AES using image as a RNG source')
    print('by Maciej Wegrzak')

    img_filename = my_input(img_filename, 'Input an image filename: ')
    print('Provide parameters for the logistic map to shuffle image') 
    print('Remeber! Growth parameter r must be between 3.6 and 3.99')
    print('x0 and y0 must be between 0 and 0.99 \n')
    r = float(input('r = '))
    x0 = float(input('x0 = '))
    y0 = float(input('y0 = '))

    myImg = rng.Rng(img_filename, r, x0, y0)
    while(True):
        print('1 - Display histograms of original and shuffled images')
        print('2 - Shuffle entropy source (image) with different parameters r, x0, y0')
        print("3 - Generate RSA keys")
        print("4 - Generate hash")
        print("5 - encrypt input")
        print("6 - decrypt input")
        print("0 - exit")

        choice = input("Choose option: ")
        match choice :
            case '1':
                myImg.dispImgHist()
            case '2':
                r = float(input('Growth parameter r = '))
                x0 = float(input('x0 = '))
                y0 = float(input('y0 = '))
                myImg.shuffle(r, x0, y0)
            case '3':
                print(f'Generating RSA keys. \n Parameters used for {img_filename} are:  r = {r} x0 = {x0} y0 = {y0}')
                generate_rsa_keys(myImg)
            case '4':
                hash_digest = hash_file()
                print(hash_digest)
            case '5':
                encrypt_file(myImg)
            case '6':
                decrypt_file()
            case '0':
                return 0


if __name__ == '__main__':
    main()

