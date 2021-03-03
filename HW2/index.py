#!/usr/bin/python3
import re
import nltk
import os
import sys
import getopt
import linecache
import string
from nltk.stem.porter import *
import pickle
import math



def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')
    # This is an empty method
    # Pls implement your code in below
    pathlist = os.listdir(in_dir)
    
    # initialize variables
    termID = 1
    termdic = {}
    
    ps = PorterStemmer()

    # First create term-termID mapping dic
    for doc in pathlist:
        f = open(os.path.join(in_dir, doc), 'r')
        print("doc: "+doc)
        for line in f:
            # casefolding
            line = line.lower()
        
            # tokenize
            sent_line = nltk.sent_tokenize(line)
            for sent_tokens in sent_line:
                word_tokens = nltk.word_tokenize(sent_tokens)

            stemmed_tokens=[]
            for token in word_tokens:
                # stem tokens
                stemmed_word = ps.stem(token)
                # remove punctuations
                if stemmed_word not in list(string.punctuation):
                    stemmed_tokens.append(stemmed_word)

            for stemmed_token in stemmed_tokens:
                if stemmed_token not in termdic.keys():
                    termdic[stemmed_token] = termID
                    termID += 1
    
           
    # blkSize = 10000
    # blkCount=1
    # pointer=1
    dic={}  # format {term: (docfreq,pointer)}
    postings={}
    

    for doc in pathlist:
        f = open(os.path.join(in_dir, doc), 'r')
        print("doc: "+doc)
        for line in f:
            # casefolding
            line = line.lower()
        
            # tokenize
            sent_line = nltk.sent_tokenize(line)
            for sent_tokens in sent_line:
                word_tokens = nltk.word_tokenize(sent_tokens)

            stemmed_tokens=[]
            for token in word_tokens:
                # stem tokens
                stemmed_word = ps.stem(token)
                # remove punctuations
                if stemmed_word not in list(string.punctuation):
                    stemmed_tokens.append(stemmed_word)

            for stemmed_token in stemmed_tokens:
                if termdic[stemmed_token] not in dic.keys():
                    dic[termdic[stemmed_token]] = 1
                    postings[termdic[stemmed_token]] = [int(doc)]
                if termdic[stemmed_token] in dic.keys() and int(doc) not in postings[termdic[stemmed_token]]:
                    dic[termdic[stemmed_token]] +=1
                    postings[termdic[stemmed_token]].append(int(doc))
    
    newdic={}
    termdiclist = list(termdic.keys())
    for item in termdiclist:
        newdic[item] = (dic[termdic[item]],termdic[item])
    # print(newdic)
    with open (out_dict,'wb+') as fp:
        # for item in dic:
        #     fp.write(str(termdiclist[item-1])+" "+str(dic[item]))  
        #     fp.write("\n")
        pickle.dump(newdic,fp)
        fp.close()
        
    
    with open (out_postings,'w+') as fp:
        for posting in postings:
            postings[posting].sort()
            addSkipPointer(postings[posting])
            for item in postings[posting]:
                    if type(item) is tuple:
                        fp.write(str(item[0])+","+str(item[1])+" ")
                    else:
                        fp.write(str(item)+" ")
            fp.write("\n")

    # print("dic : ",dic)
    # print("postings : ",postings)
    
    return (dic,postings)

def addSkipPointer(list):
    # access postings list of docs
    index = 0
    # calculate skip intervals
    skip_interval = int(math.sqrt(len(list)))
    # if len of list > 2, iterate through list and add skip pointers 
    if(len(list) > 3):
        while(index < (len(list)-skip_interval)):
            list[index] = (list[index],skip_interval)
            index += skip_interval
    

input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # input directory
        input_directory = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
