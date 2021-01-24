from PIL import Image
import numpy as np
import json


path = 'C:/Users/piedp/Documents/Resources/image/face/differ.json'
with open(path,"r") as json_file:

    data  = json.load(json_file)

    width = data["width"]
    height = data["height"]

    img2 = Image.new('RGB', (width, height))

    for i, p in enumerate( data["pix"] ):
        if p == 1 :
            img2.putpixel(( i//width, i%width), (256,256,256))
        else :
            img2.putpixel(( i//width, i%width), (0,0,0))

    img2.show()
    img2.save('C:/Users/piedp/Documents/Resources/image/face/test.jpg')