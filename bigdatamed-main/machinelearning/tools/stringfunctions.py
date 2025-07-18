# Python useful libraries and plotting to generate the images
import matplotlib.pyplot as plt
import io
import urllib, base64

"""
Function that finds the n appareance of a substring in a bigger one

Parameters:

big_string: string where we want to find the nth appareance of a substring
search_string: substring 
n: nth appareance

Return:

start: Position where the substring starts
"""
def find_nth(big_string, search_string, n):
    start = big_string.find(search_string)
    while start >= 0 and n > 1:
        start = big_string.find(search_string, start+len(search_string))
        n -= 1
    return start

"""
Function that generates a png image from plt

Parameters:

Return:

image: string that contains the png information of the image
"""
def get_image():
    fig = plt.gcf()
    buf = io.BytesIO()
    fig.savefig(buf,format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    image = urllib.parse.quote(string)
    return image