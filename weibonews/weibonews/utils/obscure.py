'''
Created on Apr 11, 2013

@author: fli
'''
import base64

def unobscure(encoded_str):
    length = len(encoded_str)
    data = encoded_str[:length/2][::-1]+encoded_str[length/2:][::-1]
    return base64.urlsafe_b64decode(data)

def obscure(json_str):
    data = base64.urlsafe_b64encode(json_str)
    length = len(data)
    result = data[:length/2][::-1] + data[length/2:][::-1]
    return result
