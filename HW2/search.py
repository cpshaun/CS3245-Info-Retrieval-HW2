#!/usr/bin/python3
import re
import nltk
import sys
import getopt
from nltk.stem.porter import *
import pickle

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

ps = PorterStemmer()


def applyOp(a,b,op,dic,diclen):
    
    if op == 'OR': 
        return query_OR(a,b,dic)
    if op == 'AND': 
        return query_AND(a,b,dic)
    if op == 'NOT': 
        return query_NOT(a,dic,diclen)

# def evaluate_postfix(postfix_string,postingdic):
def evaluate_postfix(postfix_string,postingdic,diclen):
    stack = []
    operators = ['NOT','AND','OR']

    # operators = ['*','+','-','(',')']
    while len(postfix_string)!=0:
        if postfix_string[0] not in operators:
            temp = postfix_string.pop(0)
            stack.append(temp)
        elif postfix_string[0] in operators:
            op = postfix_string.pop(0)
            print("op : ",op)
            if op != 'NOT':
                temp2 = stack.pop()
                # print("temp2 : ",temp2)
                temp1 = stack.pop()
                # print("temp1 : ",temp1)
                temp3 = applyOp(temp1,temp2,op,postingdic,diclen)
                stack.append(temp3)
            elif op == 'NOT':
                temp1 = stack.pop()
                temp2 = temp1
                print("temp1 :",temp1)
                temp3 = applyOp(temp1,temp2,op,postingdic,diclen)
                stack.append(temp3)
    print("stack : ",stack[0])
    return stack[0]

def shunting_yard(query,postingdic,diclen):
    operator_stack = []
    postfix_string = []
    operators = ['NOT','AND','OR','(',')']
    precedence = {'NOT':2, 'AND':1,'OR':0}
    # operators = ['*','+','-','(',')']
    # precedence = {'*':2, '+':1,'-':1}
    for i in range(0,len(query)):
        # if term
        if query[i] not in operators:
            postfix_string.append(query[i])
            print("postfix :",postfix_string)
        # if operator
        elif query[i] in operators:
            if len(operator_stack) == 0:
                operator_stack.append(query[i])
                print("opstack :",operator_stack)
            else:
                print('query: ',query[i])
                if query[i] == ')':
                    while(operator_stack[len(operator_stack)-1]) != '(':
                        temp = operator_stack.pop()
                        print("temp : ",temp)
                        postfix_string.append(temp)
                        print("postfix :",postfix_string)
                    operator_stack.pop()
                    print("opstack :",operator_stack)
                # if operator is (
                elif query[i] == '(':
                    operator_stack.append(query[i])
                    print("opstack :",operator_stack)
                # if operator is not ( 
                else:
                    if(operator_stack[len(operator_stack)-1] == '('):
                        operator_stack.append(query[i])
                        print("opstack :",operator_stack)
                    else:
                        # if incoming operator has higher precedence
                        if precedence[operator_stack[len(operator_stack)-1]] <= precedence[query[i]]:
                            operator_stack.append(query[i])
                            print("opstack :",operator_stack)
                        # if incoming operato has lower precedence
                        elif precedence[operator_stack[len(operator_stack)-1]] > precedence[query[i]]:
                            temp = operator_stack.pop()
                            print("temp : ",temp)
                            postfix_string.append(temp)
                            print("postfix :",postfix_string)
                            operator_stack.append(query[i])
                            print("opstack :",operator_stack)
    while len(operator_stack) != 0:
        temp = operator_stack.pop()
        print("opstack :",operator_stack)
        print("temp : ",temp)
        postfix_string.append(temp)
    
    print("postfix :",postfix_string)
    result = evaluate_postfix(postfix_string,postingdic,diclen)
    # print("Result: ",result)
    return result

# function for OR query between two terms
def query_OR(a,b,dic):
    # merge both lists
    if type(a) != list:
        posting_lista = dic[a]
    else: 
        posting_lista = a
    if type(b) != list:
        posting_listb = dic[b]
    else: 
        posting_listb = b
    
    for i in range(0,len(posting_lista)):
        if type(posting_lista[i]) == tuple:
            posting_lista[i] = posting_lista[i][0] 
    
    posting_list = posting_lista
    for j in range(0,len(posting_listb)):
        if type(posting_listb[j]) == tuple:
            posting_listb[j] = posting_listb[j][0] 
        if posting_listb[j] not in posting_list:
            posting_list.append(posting_listb[j])
    
    posting_list.sort()
    # print(posting_list)
    return posting_list

# function for AND query between two terms
def query_AND(a,b,dic):
    # compare between elements in each list and take intersection
    if type(a) != list:
        posting_lista = dic[a]
    else: 
        posting_lista = a
    if type(b) != list:
        posting_listb = dic[b]
    else: 
        posting_listb = b
    posting_list = []
    i=0
    j=0
    # print("len: ",len(posting_lista),len(posting_listb))
    while i<len(posting_lista):
        while j<len(posting_listb):
            if (i==len(posting_lista)):
                break
            # if b not tuple
            if type(posting_listb[j]) is not tuple:
            # case 1: a is tuple 
                if type(posting_lista[i]) is tuple:
                    # a == b
                    if posting_lista[i][0] == posting_listb[j]:
                        posting_list.append(posting_listb[j])
                        j+=1
                    # a > b
                    elif posting_lista[i][0] > posting_listb[j]:
                        j+=1
                    # a < b , check for skip pointer
                    elif posting_lista[i][0] < posting_listb[j]:
                        # might not be a tuple
                        if type(posting_lista[i+posting_lista[i][1]]) is tuple:
                            if posting_lista[i+posting_lista[i][1]][0] < posting_listb[j]:
                                i+=posting_lista[i][1]
                            else:
                                i+=1
                        elif type(posting_lista[i+posting_lista[i][1]]) is not tuple:
                            if posting_lista[i+posting_lista[i][1]] < posting_listb[j]:
                                i+=posting_lista[i][1]
                            else:
                                i+=1
            # case 2: a is not tuple 
                elif type(posting_lista[i]) is not tuple:
                    # a == b
                    if posting_lista[i] == posting_listb[j]:
                        posting_list.append(posting_lista[i])
                        i+=1
                        j+=1
                    # a > b
                    elif posting_lista[i] > posting_listb[j]:
                        j +=1
                    # a < b
                    elif posting_lista[i] < posting_listb[j]:                 
                        i+=1
            # if a is not tuple 
            elif type(posting_lista[i]) is not tuple: 
                # case 3: b is tuple 
                if type(posting_listb[j]) is tuple:
                    # a == b
                    if posting_listb[j][0] == posting_lista[i]:
                        posting_list.append(posting_lista[i])
                        i+=1
                    # a < b
                    elif posting_lista[i] < posting_listb[j][0]:
                        i+=1
                    # a > b
                    elif posting_lista[i] > posting_listb[j][0]:
                        if type(posting_listb[j+posting_listb[j][1]]) is tuple:
                            if posting_listb[j+posting_listb[j][1]][0] < posting_lista[i]:
                                j+=posting_listb[j][1]
                            else:
                                j+=1
                        elif type(posting_listb[j+posting_listb[j][1]]) is not tuple:
                            if posting_listb[j+posting_listb[j][1]] < posting_lista[i]:
                                j+=posting_listb[j][1]
                            else:
                                j+=1
            # if a and b are tuples
            elif type(posting_lista[i]) is tuple and type(posting_listb[j]) is tuple : 
                # case 4: a and b are tuples
                # a == b
                # TO CHECK FOR TUPLES AND NON TUPLE
                if posting_lista[i][0] == posting_listb[j][0]:
                    posting_list.append(posting_lista[i][0])
                    if type(posting_lista[i+posting_lista[i][1]]) is tuple:
                        if posting_lista[i+posting_lista[i][1]][0] < posting_listb[j+1]:
                            i+=posting_lista[i][1]
                            j+=1
                        elif posting_lista[i+posting_lista[i][1]][0] == posting_listb[j+1]:
                            i+=posting_lista[i][1]
                            j+=1
                        elif posting_lista[i+posting_lista[i][1]][0] > posting_listb[j+1]:
                            i+=1
                            j+=1
                    elif type(posting_lista[i+posting_lista[i][1]]) is not tuple:
                        if posting_lista[i+posting_lista[i][1]] < posting_listb[j+1]:
                            i+=posting_lista[i][1]
                            j+=1
                        elif posting_lista[i+posting_lista[i][1]] == posting_listb[j+1]:
                            i+=posting_lista[i][1]
                            j+=1
                        elif posting_lista[i+posting_lista[i][1]] > posting_listb[j+1]:
                            i+=1
                            j+=1
                    elif type(posting_listb[j+posting_listb[j][1]]) is tuple:
                        if posting_listb[j+posting_listb[j][1]][0] < posting_lista[i+1]:
                            j+=posting_listb[j][1]
                            i+=1
                        elif posting_listb[j+posting_listb[j][1]][0] == posting_lista[i+1]:
                            j+=posting_listb[j][1]
                            i+=1
                        elif posting_listb[j+posting_listb[j][1]][0] > posting_lista[i+1]:
                            j+=1
                            i+=1
                    elif type(posting_listb[j+posting_listb[j][1]]) is not tuple:
                        if posting_listb[j+posting_listb[j][1]] < posting_lista[i+1]:
                            j+=posting_listb[j][1]
                            i+=1
                        elif posting_listb[j+posting_listb[j][1]] == posting_lista[i+1]:
                            j+=posting_listb[j][1]
                            i+=1
                        elif posting_listb[j+posting_listb[j][1]] > posting_lista[i+1]:
                            j+=1
                            i+=1
                # a smaller than b
                elif posting_lista[i][0] < posting_listb[j][0]:
                    if type(posting_lista[i+posting_lista[i][1]]) is tuple:
                        if posting_lista[i+posting_lista[i][1]][0] < posting_listb[j][0]:
                            i+=posting_lista[i][1]
                        elif posting_lista[i+posting_lista[i][1]][0] > posting_listb[j][0]:
                            i+=1
                    elif type(posting_lista[i+posting_lista[i][1]]) is not tuple:
                        if posting_lista[i+posting_lista[i][1]] < posting_listb[j][0]:
                            i+=posting_lista[i][1]
                        elif posting_lista[i+posting_lista[i][1]] > posting_listb[j][0]:
                            i+=1
                # a larger than b
                elif posting_lista[i][0] > posting_listb[j][0]:
                    if type(posting_listb[j+posting_listb[j][1]]) is tuple:
                        if posting_listb[j+posting_listb[j][1]][0] < posting_lista[i][0]:
                            j+=posting_listb[j][1]
                        elif posting_listb[j+posting_listb[j][1]][0] > posting_lista[i][0]:
                            j+=1
                    elif type(posting_listb[j+posting_listb[j][1]]) is not tuple:
                        if posting_listb[j+posting_listb[j][1]] < posting_lista[i][0]:
                            j+=posting_listb[j][1]
                        elif posting_listb[j+posting_listb[j][1]] > posting_lista[i][0]:
                            j+=1
            # print("len: ",len(posting_lista),len(posting_listb))
            # print("i,j : ",i,j)
            # print(posting_list)

        if i == len(posting_lista) or j == len(posting_listb):
                break
            
    posting_list.sort()
    # print(posting_list)
    return posting_list

def query_NOT(a,dic,diclen):
    if type(a) != list:
        posting_lista = dic[a]
    else: 
        posting_lista = a
    
    excl_list = []
    for i in range(1,diclen+1):
        if i not in posting_lista:
            excl_list.append(i)
    
    return excl_list

def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')
    # This is an empty method
    # Pls implement your code in below

    # load in dictionary
    fp = open(dict_file, 'rb')
    dic = pickle.load(fp)
    fp.close() 
    
    diclen = len(dic)
    outputs = []
    # read in queries file
    queries = open(queries_file, 'r')
    for query in queries:
        print(query)
        sentence = nltk.sent_tokenize(query)
        for sentence_token in sentence:
            word_token = nltk.word_tokenize(sentence_token)
        stemmed_tokens = []
        # print("before stemming: ",word_token)
        for token in word_token:
            stemmed_token = ps.stem(token)
            stemmed_tokens.append(stemmed_token)
        # filter query to have uppercase and,or and not
        filtered_query =[]
        for operator in stemmed_tokens:
            if operator == 'and' or operator == 'or' or operator == 'not':
                operator = operator.upper()
            filtered_query.append(operator)

        rows = []
        # check which rows in dictionary query term is in
        for query_token in filtered_query:
            if query_token in dic.keys():
                rows.append(dic[query_token][1])
            elif query_token == 'AND' or query_token == 'OR' or query_token == 'NOT' or query_token == '(' or query_token == ')':
                continue
        rows.sort()
        # print("rows dictionary query terms are in: ",rows)
        
        postings = []
    
        # find rows in postings.txt to get back posting lists
        with open("postings.txt","r") as file:
            for i, line in enumerate(file):
                # print(i+1,line)
                for row in rows:
                    # print (i,row)
                    if i+1 == row:
                        postings.append(nltk.word_tokenize(line))
                    
        # print("postings for said rows: ",postings)
        for posting in postings:
            for i in range(0,len(posting)):
                if ',' in posting[i]:
                    posting[i] = (int(posting[i].split(',')[0]),int(posting[i].split(',')[1]))
                else:
                    posting[i] = int(posting[i])
        
        postingdic = {}
        for i in range(0,len(rows)):
            postingdic[list(dic)[rows[i]-1]]= postings[i]
        


        outputs.append(shunting_yard(filtered_query,postingdic,diclen))
        
    with open (results_file,'w+') as fp:
        for output in outputs:
            for doc in output:
                fp.write(str(doc)+" ")
            fp.write("\n")
    
        
        # print(postings)
        # print("postingdic: ",postingdic)
    # print("postingdic: ",postingdic)
    # query_OR('kingdom','data',postingdic)
    # query_AND('it','data',postingdic)
    # testquery = ['A','NOT','(', 'B','AND','C','NOT','D',')','AND','E']
    # testquery = ['A','*','(', 'B','+','C','*','D',')','+','E']
    # testquery = ['30','*','(', '20','+','10','*','40',')','+','5']
    # testquery = (filtered_query)
    # shunting_yard(testquery,postingdic,diclen)
    

    



    

dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
