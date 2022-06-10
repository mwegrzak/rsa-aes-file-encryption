#pip install imageio matplotlib

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

        # if color img swap to grayscale
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
        axs[0][0].set_title(f'Input image \n Entropy: {self.calcEntropy(image1)}')
        axs[0][1].hist(image1.ravel(), bins=256, range=[0, 255])

        axs[1][0].imshow(image2, vmin=0, vmax=255, cmap='gray')
        axs[1][0].set_title(f'Shuffled image \n Entropy: {self.calcEntropy(image2)}')
        axs[1][1].hist(image2.ravel(), bins=256, range=[0, 255])
        plt.show()

    def rgb2gray(self, rgb):
        r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
        gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
        return gray.astype(np.uint8)

    def calcEntropy(self, img = None):
        if img is None:
            img = self.encryptedImg

        marg = np.histogramdd(np.ravel(img), bins = 256)[0] / img.size
        marg = list(filter(lambda p: p > 0, np.ravel(marg)))
        entropy = -np.sum(np.multiply(marg, np.log2(marg)))
        return entropy

    def generateSequence(self, r, x0, i, colRowLen):
        # iterative implementation of a logistic map
        x_i = r * x0 * (1 - x0)
        for i in range(1, i):
            x_i = r * x_i * (1 - x_i)
        return int(x_i * colRowLen - 1)

    def shuffle(self, r, x0, y0):

        original = self.img.copy()
        self.encryptedImg = self.img.copy()
        xi_seq = np.zeros((self.cols, self.rows)).astype(np.uint8)
        i = 1
        j = 0
        
        # ------------------------------------------------

        print('Shuffling cols...')
        while j < self.cols:
            # generating column index using logistic map until x_i < cols - 1:
            x_i = self.generateSequence(r, x0, i, self.cols)
            if x_i > self.cols - 1:
                i += 1
            else:
                for k in range(0, self.rows):
                    xi_seq[j][k] = x_i

                # swap j column with x_i column
                for k in range(0, self.rows):
                    tmp = self.encryptedImg[j][k]
                    self.encryptedImg[j][k] = self.encryptedImg[x_i][k]
                    self.encryptedImg[x_i][k] = tmp
                
                # j column XOR j + 1
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
        
        # ------------------------------------------------
        i = 1
        j = 0
        yi_seq = np.zeros((self.cols, self.rows)).astype(int)
        print('Shuffling rows...')
        while j < self.rows:
            # generating column index using logistic map until x_i < cols - 1:
            y_i = self.generateSequence(r, y0, i, self.rows)
            if y_i > self.rows - 1:
                i += 1
            else:
                for k in range(0, self.cols):
                    yi_seq[k][j] = y_i
                
                # swap j row with x_i row
                for k in range(0, self.cols):
                    tmp = self.encryptedImg[k][j]
                    self.encryptedImg[k][j] = self.encryptedImg[k][y_i]
                    self.encryptedImg[k][y_i] = tmp
                
                # j row XOR j + 1
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
        
        # ------------------------------------------------
        print('Shuffling pixels...')
        for j in range(0, self.cols):
            for k in range(0, self.rows):
                tmp = self.encryptedImg[j][k]
                self.encryptedImg[j][k] = original[xi_seq[j][k], yi_seq[j][k]]
                original[xi_seq[j][k], yi_seq[j][k]] = tmp

        
        # equalization
        hist = np.histogram(self.encryptedImg.ravel(), bins=256, range=[0, 255])
        for value, count in enumerate(hist[0]):
            img_avg =  (1/256) * 100    # assuming an image is 256 bits
            avg = count / (self.cols * self.rows) * 100
            if avg >= 3 * img_avg :
                self.equalize(value, count)
        print('Done.')

        return self.encryptedImg

    def equalize(self, value, count):
        '''
        every img should have equally distributed values
        (1/256) * 100% = 0,4%
        if avg amount of points > 1.2%, equally distribute until 0,8%
        eg. for value 0 there are over 1.2% counts, add to 0 values continously 1, 2, 3...
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

    def generateBytes(self, N):
        bytes = b''
        while(len(bytes) < N):
            '''
            iterate over the img and append bytes to bytes variable
            array's records are uint8 type so 1 record == 1 byte
            it's using x and y defined in the object
            keep in mind that it's random until the size of an image
            '''
            if self.bytes_x >= self.cols:
                self.bytes_x = 0
            while self.bytes_x < self.cols:
                if self.bytes_y >= self.rows:
                    self.bytes_y = 0
                while self.bytes_y < self.rows:
                    bytes += self.encryptedImg[self.bytes_x][self.bytes_y].tobytes()
                    if len(bytes) >= N:
                        return bytes
                    self.bytes_y += 1
                self.bytes_x += 1
               

if __name__ == '__main__':
    r = 3.68
    x0 = 0.7
    y0 = 0.7

    myImg = Rng('lena.png', r, x0, y0)
    myImg.dispImgHist()
    myImg.shuffle(3.8, 0.5, 0.8)
    myImg.dispImgHist()
    print(myImg.generateBytes(10))
    print(myImg.generateBytes(10))
    print(f"Entropy: {myImg.calcEntropy()}")