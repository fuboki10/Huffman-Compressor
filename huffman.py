#!/usr/bin/python3
import sys
import heapq
import json

class WrongFormat(Exception):
    """Wrong file format Error"""
    pass

class fileInterface:
    #write to files
    def write(self, fileName, data):
        if fileName.endswith('.json'):
            with open(fileName, 'w') as file:
                json.dump(data, file)
        elif fileName.endswith('.txt'):
            with open(fileName, 'w+') as file:
                file.write(data)
        elif fileName.endswith('.bin'):
            ascii = data.encode('charmap') #encode the string to extended ascii
            with open(fileName, 'w+b') as file:
                file.write(ascii)
        else:
            raise WrongFormat

    #read from files          
    def read(self, fileName):
        data = ""
        if fileName.endswith('.txt'):
            with open(fileName, 'r') as file:
                data = file.read().replace('\n', '')
        elif fileName.endswith('.json'):
            with open(fileName, 'r') as file:
                data = json.load(file)
        elif fileName.endswith('.bin'):
            with open(fileName, "rb") as file:
                byte = file.read()
                length = byte[0] #read the length of the last bit
                for i in range (1,len(byte)-1): #read the data w/o the last byte
                    b = str(bin(byte[i]))[2:]
                    while(len(b) < 8): #complete the current byte if it less than 8 bits
                        b='0'+b
                    data = data + b
                if(str(bin(byte[-1]))[2:] == '0'): #if the last byte is zero 
                    for i in range(length):
                        data+='0' # then add zeros equal to the last Byte length
                else:
                    data = data + str(bin(byte[-1]))[2:] # else read the last byte
                    data=data[:(length-8)] # and remove the last 8-length of it as we add them as zeros
                data = data[1:] # remove the first bit which we added as 1 
        else:
            raise WrongFormat
            
        return data
    
    #normal recursion
def node_code(node ,code,dict):
    if(node == None):
        return
    if(node.char == None):
        node_code(node.lc,code+"0",dict)
        node_code(node.rc,code+"1",dict)
    else:
        node.code+=code
    if(node.char!=None):
        dict[node.char] = node.code
        
class node:
    def __init__(self, c = None,o=None): 
        self.char = c # character of the current node
        self.occ = o   # occurrence of the current node
        self.code = "" # code of the current node 
        self.parent = None
        self.lc = None #left child
        self.rc =None # right child
    def combine(self,l,r):
        self.occ = l.occ + r.occ
        self.lc = l
        self.rc = r
        l.parent = self
        r.parent = self
    def __lt__(self, other):
        return(self.occ<other.occ) 
    def __gt__(self, other): 
        return (self.occ>other.occ)
    def __str__(self):
        return 'char : {} , occurance : {} , code {}'.format(self.char , self.occ , self.code)
    
class tree:
    def __init__(self,head):
        self.head = head
        
    def construct_from_dict(self,dict):
        tr = self
        for key in dict:
            current_node = tr.head
            val = dict[key]
            for char in val: # if none (not a leaf)  create a new node and move to it 
                if char == '0': 
                    if current_node.lc is None:
                        current_node.lc = node() 
                    current_node = current_node.lc
                elif char == '1':
                     if current_node.rc is None:
                        current_node.rc = node()
                     current_node = current_node.rc
            current_node.char = key #for each key build a leaf node
            
    def decode(self,encoded):
        res = ""
        current_node = self.head
        for char in encoded:
            if char == '0': #go left
                current_node = current_node.lc 
            elif char == '1': #go right 
                current_node = current_node.rc
            else:
                raise ValueError

            if current_node.char is not None:
                res += current_node.char #add the corresponding character
                current_node = self.head #reset to the head
        return res

if len(sys.argv) != 4:
    print('Wrong input.\nEnter --encode <inputFile> <outputFile> to encode your file or \n\
Enter --decode <inputFile> <outputFile> to decode your file')
    exit(1)
    
    
if sys.argv[1] == '--encode':
    try:
        inputFile = sys.argv[2]
        outputFile = sys.argv[3]
        
        data = fileInterface().read(inputFile)
        d=[] 
        for c in set(data) :
            d.append(node(c,  data.count(c))) #create a list of nodes
        heapq.heapify(d) #transform the list into a heap queue
        
        while len(d) > 1: # create the tree
            l =  heapq.heappop(d)
            r =  heapq.heappop(d)
            p = node()
            p.combine(l,r)
            heapq.heappush(d,p)
        
        htree = tree(heapq.heappop(d))
        dict = {}
        node_code(htree.head,"",dict) # create the dict 
        fileInterface().write('dict.json', dict)
        
        encoded = ""
        for c in data: #encode the message
            encoded+=dict[c]
        encoded = '1' + encoded #add 1 at the beginning to prevent less than byte errors (in case of the first byte starts with 0)
        
        lblength=len(encoded) % 8 #the length of the last byte
        for i in range(8-lblength):
            encoded+='0' # make the last byte = 8 bits by adding 0s to the end of it        
        
        # add the length of the last byte at the beginning of the data then transform each 8 bits into an ascii to save it in a
        #binary file
        data =  chr(lblength)+''.join(chr(int(encoded[i:i+8], 2)) for i in range(0, len(encoded), 8))
        
        fileInterface().write(outputFile, data) #write the encoded data to a binary file
        
    except WrongFormat:
        print('Wrong file format')
        exit(1)
    except:
        print('ERROR')
        exit(1)

elif sys.argv[1] == '--decode':
    
    try:
        inputFile = sys.argv[2]
        outputFile = sys.argv[3]
        
        encoded_data = fileInterface().read(inputFile) # read the encoded data 
        
        ndict = {}
        ndict = fileInterface().read('dict.json') # read the dictionary 
        
        huf = tree(node())
        huf.construct_from_dict(ndict)
        
        decoded = huf.decode(encoded_data) #decode the data
        
        fileInterface().write(outputFile, decoded) # save it as a text file
        
    except WrongFormat:
        print('Wrong file format')
        exit(1)
    except:
        print('ERROR')
        exit(1)
        
else:
    print('Wrong input.\nEnter --encode <inputFile> <outputFile> to encode your file or \n\
Enter --decode <inputFile> <outputFile> to decode your file')
    exit(1)