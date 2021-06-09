import imageio
import cv2
import numpy as np
import glob

images = []
def gif(number, fileName):
    for i in range(number):
        path = "Output/{}.png".format(i)
        try:
            images.append(imageio.imread(path))
        except:
            print("{} Doesn't Exist!".format(i))

    imageio.mimsave(fileName + ".gif", images)

if __name__ == "__main__": 
    number = int(input("How many images did you make?\n"))
    fileName = input("What would you like your GIF to be called?\n")
    gif(number, fileName)
    print("GIF Created!")
