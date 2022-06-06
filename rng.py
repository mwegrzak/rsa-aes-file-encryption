#pip install pycryptodome imageio matplotlib

import numpy as np
import matplotlib.pyplot as plt
import imageio

class Rng:
    def __init__(self, filename, r, x0, y0):
        self.img = imageio.imread(filename)
        self.cols = len(self.img)
        self.rows = len(self.img[0])
        self.bytes_x = 0
        self.bytes_y = 0

        if self.img.ndim == 3:
            self.img = self.rgb2gray(self.img)

        self.encryptedImg = self.img.copy()
        self.encryptedImg = self.shuffle(r, x0, y0)

    def dispImgHist(self, image1 = None, image2 = None):

        if image1 is None:
            image1 = self.img
        if image2 is None:
            image2 = self.encryptedImg
        fig, axs = plt.subplots(2, 2, figsize=[10,10], constrained_layout=True)
        axs[0][0].imshow(image1, vmin=0, vmax=255, cmap='gray')
        axs[0][0].set_title(f'Obraz wejściowy \n Entropia: {self.calcEntropy(image1)}')
        axs[0][1].hist(image1.ravel(), bins=256, range=[0, 255])

        axs[1][0].imshow(image2, vmin=0, vmax=255, cmap='gray')
        axs[1][0].set_title(f'Obraz wyjściowy \n Entropia: {self.calcEntropy(image2)}')
        axs[1][1].hist(image2.ravel(), bins=256, range=[0, 255])
        plt.show()

    def rgb2gray(self, rgb):
        r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
        gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
        return gray.astype(np.uint8)

    def calcEntropy(self, img):
        # liczenie prawdopodobienstwa
        marg = np.histogramdd(np.ravel(img), bins = 256)[0]/img.size
        # filtrowanie zer
        marg = list(filter(lambda p: p > 0, np.ravel(marg)))
        entropy = -np.sum(np.multiply(marg, np.log2(marg)))
        return entropy

    def generateSequence(self, r, x0, i, colRowLen):
        '''
        Iteracyjna implementacja mapy logistycznej
        '''
        x_i = r * x0 * (1 - x0)
        for i in range(1, i):
            x_i = r * x_i * (1 - x_i)
        return int(x_i * colRowLen - 1)

    def shuffle(self, r, x0, y0):
        original = self.img.copy()
        self.encryptedImg = self.img.copy()
        # szuflowanie kolumn

        xi_seq = np.zeros((self.cols, self.rows)).astype(int)
        i = 1
        j = 0
        # zamiana rzedow
        print('Shuffling cols...')
        while j < self.cols:
            # losowanie indeksu kolumny wg mapy logistycznej
            x_i = self.generateSequence(r, x0, i, self.cols)
            if x_i > self.cols - 1:
                i += 1
            else:
                for k in range(0, self.rows):
                    xi_seq[j][k] = x_i
                # zamiana rzedu j z rzedem x_i
                for k in range(0, self.rows):
                    tmp = self.encryptedImg[j][k]
                    self.encryptedImg[j][k] = self.encryptedImg[x_i][k]
                    self.encryptedImg[x_i][k] = tmp
                #xor rzedu j oraz j+1
                if(j < self.cols - 1):
                    for k in range(0, self.rows - 1):
                        self.encryptedImg[j][k] = self.encryptedImg[j][k] ^ self.encryptedImg[j+1][k]
                    self.encryptedImg[j][self.rows - 1] = self.encryptedImg[j][self.rows - 1] ^ self.encryptedImg[0][self.rows - 1]
                else:
                    for k in range(0, self.rows - 1):
                        self.encryptedImg[j][k] = self.encryptedImg[j][k] ^ self.encryptedImg[0][k]
                    self.encryptedImg[j][self.rows - 1] = self.encryptedImg[j][self.rows - 1] ^ self.encryptedImg[0][self.rows - 1]

                j += 1
                i += 1
        
        # zamiana kolumn
        i = 1
        j = 0
        yi_seq = np.zeros((self.cols, self.rows)).astype(int)
        print('Shuffling rows...')
        while j < self.rows:
            # losowanie indeksu kolumny wg mapy logistycznej
            y_i = self.generateSequence(r, y0, i, self.rows)
            if y_i > self.rows - 1:
                i += 1
            else:
                for k in range(0, self.cols):
                    yi_seq[k][j] = y_i
                # zamiana rzedu j z rzedem y_i
                for k in range(0, self.cols):
                    tmp = self.encryptedImg[k][j]
                    self.encryptedImg[k][j] = self.encryptedImg[k][y_i]
                    self.encryptedImg[k][y_i] = tmp
                #xor rzedu j oraz j+1
                if(j < self.rows - 1):
                    for k in range(0, self.cols - 1):
                        self.encryptedImg[k][j] = self.encryptedImg[k][j] ^ self.encryptedImg[k][j+1]
                    self.encryptedImg[self.cols - 1][j] = self.encryptedImg[self.cols - 1][j] ^ self.encryptedImg[self.cols - 1][0]
                else:
                    for k in range(0, self.cols - 1):
                        self.encryptedImg[k][j] = self.encryptedImg[k][j] ^ self.encryptedImg[k][0]
                    self.encryptedImg[self.cols - 1][j] = self.encryptedImg[self.cols - 1][j] ^ self.encryptedImg[self.cols - 1][0]

                j += 1
                i += 1

        # permutacja pikseli
        print('Shuffling pixels...')
        for j in range(0, self.cols):
            for k in range(0, self.rows):
                tmp = self.encryptedImg[j][k]
                self.encryptedImg[j][k] = original[xi_seq[j][k], yi_seq[j][k]]
                original[xi_seq[j][k], yi_seq[j][k]] = tmp

        
        # equalization
        hist = np.histogram(self.encryptedImg.ravel(), bins=256, range=[0, 255])
        for value, count in enumerate(hist[0]):
            avg = count / (len(self.encryptedImg) * len(self.encryptedImg[0])) * 100
            if avg >= 1.2 :
                self.equalize(value, count)
        print('Done.')

        return self.encryptedImg

    def equalize(self, value, count):
        '''
        every img should have equally distributed values
        (1/256) * 100% = 0,4%
        jezeli ilosc punktow dla wartosci x przekracza 3 razy wiecej (czyli 1,2%) 
        to rownomiernie rozdziel pomiedzy wszystkie wartosci do 0,8%
        (x zamien na wartosci kolejno 0, 1, 2, 3...)
        '''
        total_pixels = self.cols * self.rows
        pixels_to_change = count - int(total_pixels * 0.008)

        i = 0
        incr = 0
        self.encryptedImg = self.encryptedImg.ravel()
        while(pixels_to_change > 0):
            if i > total_pixels:    i = 0
            if incr == value:       incr += 1
            if incr > 255:          incr = 0

            if self.encryptedImg[i] == value:
                self.encryptedImg[i] = incr
                incr += 1
                pixels_to_change -= 1
            i += 1

        self.encryptedImg = self.encryptedImg.reshape(self.cols, self.rows)
        return self.encryptedImg

    def generateBytes(self, byte_count):
        '''
        '''
        bytes = b''
        while(len(bytes) < byte_count):
            # iterate over the img and append bytes to bytes variable
            if self.bytes_x >= self.cols:
                self.bytes_x = 0
            while self.bytes_x < self.cols:
                if self.bytes_y >= self.rows:
                    self.bytes_y = 0
                while self.bytes_y < self.rows:
                    bytes += self.encryptedImg[self.bytes_x][self.bytes_y].tobytes()
                    if len(bytes) >= byte_count:
                        return bytes
                    self.bytes_y += 1
                self.bytes_x += 1

if __name__ == '__main__':
    r = 3.68
    x0 = 0.7
    y0 = 0.7
    dupa = Rng('lena.png', r, x0, y0)
    dupa.dispImgHist()