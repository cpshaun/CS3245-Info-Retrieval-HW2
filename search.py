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

# function to apply operators to lists
def applyOp(a,b,op,dic,diclen):
    
    if op == 'OR': 
        return query_OR(a,b,dic)
    if op == 'AND': 
        return query_AND(a,b,dic)
    if op == 'NOT': 
        return query_NOT(a,dic,diclen)

# function to evaluate postfix string that is returned from shunting yard algorithm
def evaluate_postfix(postfix_string,postingdic,diclen):
    
    # initialise evaluated stack and operators list
    stack = []
    operators = ['NOT','AND','OR']

    # iterate through postfix string
    while len(postfix_string)!=0:
        # if term in postfix string is not an operator, pop it and push to stack
        if postfix_string[0] not in operators:
            temp = postfix_string.pop(0)
            stack.append(temp)
        # elif term in postfix string is an operator, pop it
        elif postfix_string[0] in operators:
            op = postfix_string.pop(0)
            
            # if operator is AND or OR
            if op != 'NOT':
                temp2 = stack.pop()
                temp1 = stack.pop()
                temp3 = applyOp(temp1,temp2,op,postingdic,diclen)
                stack.append(temp3)
            
            # if operator is NOT
            elif op == 'NOT':
                temp1 = stack.pop()
                temp2 = temp1
                temp3 = applyOp(temp1,temp2,op,postingdic,diclen)
                stack.append(temp3)
    return stack[0]

# shunting yard algorithm to convert queries to postfix strings
def shunting_yard(query,postingdic,diclen):
    
    # initialise a stack for storing operators and an array for storing finalised postfix string
    operator_stack = []
    postfix_string = []

    # intialise possible operators and assign a precedence score for operators apart from '(' and ')' as different operators have different priorities
    operators = ['NOT','AND','OR','(',')']
    precedence = {'NOT':2, 'AND':1,'OR':0}
    
    # read in query and iterate from first term
    for i in range(0,len(query)):
        
        # if query term is not an operator
        if query[i] not in operators:
            postfix_string.append(query[i])
        
        # if query term is an operator
        elif query[i] in operators:
            # if operator stack is empty
            if len(operator_stack) == 0:
                operator_stack.append(query[i])
            else:
                # if operator is ')', pop operator stack til '(' is reached and append to postfix string
                if query[i] == ')':
                    while(operator_stack[len(operator_stack)-1]) != '(':
                        temp = operator_stack.pop()
                        postfix_string.append(temp)
                    # remove '('
                    operator_stack.pop()

                # if operator is '('
                elif query[i] == '(':
                    operator_stack.append(query[i])
    
                # if operator is not '(', check if operator at top of stack is '(', 
                # if so append current operator regardless of priority  
                # else check for priority
                else:
                    if(operator_stack[len(operator_stack)-1] == '('):
                        operator_stack.append(query[i])
                    else:
                        # if incoming operator has higher or same priority as operator at top of operator stack, push to stack
                        if precedence[operator_stack[len(operator_stack)-1]] <= precedence[query[i]]:
                            operator_stack.append(query[i])
                            
                        # if incoming operator has lower priority, pop operator from stack and append to postfix string
                        elif precedence[operator_stack[len(operator_stack)-1]] > precedence[query[i]]:
                            temp = operator_stack.pop()
                            postfix_string.append(temp)
                            operator_stack.append(query[i])
    
    # when query is fully read, if operator stack still has operators, pop them and append to postfix string to get finalised postfix string
    while len(operator_stack) != 0:
        temp = operator_stack.pop()
        postfix_string.append(temp)
    
    # evaluate postfix string
    result = evaluate_postfix(postfix_string,postingdic,diclen)
    return result

# function for OR query between two terms
def query_OR(a,b,dic):
    # merge both lists
    # first check if term is query token or list
    if type(a) != list:
        posting_lista = dic[a]
    else: 
        posting_lista = a
    if type(b) != list:
        posting_listb = dic[b]
    else: 
        posting_listb = b
    
    # first remove all skip pointers from one posting list
    for i in range(0,len(posting_lista)):
        if type(posting_lista[i]) == tuple:
            posting_lista[i] = posting_lista[i][0] 

    # then remove all skip pointers from another posting list while simulataneously appending posting if it does not exist in first list -> prevent duplicates
    posting_list = posting_lista
    for j in range(0,len(posting_listb)):
        if type(posting_listb[j]) == tuple:
            posting_listb[j] = posting_listb[j][0] 
        if posting_listb[j] not in posting_list:
            posting_list.append(posting_listb[j])
    
    # sort merged list
    posting_list.sort()
    # print(posting_list)
    return posting_list

# function for AND query between two terms
def query_AND(a,b,dic):
    # compare between elements in each list and take same values
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
    
    # while iterating through both posting lists, check if current term is tuple, if its a tuple, a skip pointer is present
    # due to evenly spaced skip pointers, tuples will always point to tuples unless its the last term pointed to within the posting list
    # append when values in both posting lists are equal, move pointers/ skip pointers when values are different
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

        if i == len(posting_lista) or j == len(posting_listb):
                break
    
    # sort resultant posting list
    posting_list.sort()

    return posting_list

# function for NOT query for a term
def query_NOT(a,dic,diclen):
    if type(a) != list:
        posting_lista = dic[a]
    else: 
        posting_lista = a
    
    excl_list = []

    # brute force method of appending all documents that dont exist in a list (inefficient :()
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

    # load in dictionary
    fp = open(dict_file, 'rb')
    dic = pickle.load(fp)
    fp.close() 
    
    # to find rows in postings.txt
    diclen = len(dic)

    # initialise list for outputs to queries
    outputs = []

    # read in queries file
    queries = open(queries_file, 'r')

    for query in queries:
        
        # tokenise and stem queries
        sentence = nltk.sent_tokenize(query)
        for sentence_token in sentence:
            word_token = nltk.word_tokenize(sentence_token)
        stemmed_tokens = []
        
        for token in word_token:
            stemmed_token = ps.stem(token)
            stemmed_tokens.append(stemmed_token)

        # filter query to have uppercase and,or and not as they have been converted to lower case by stem
        filtered_query =[]
        for operator in stemmed_tokens:
            if operator == 'and' or operator == 'or' or operator == 'not':
                operator = operator.upper()
            filtered_query.append(operator)

        # initialise list to store the non operator query terms 
        rows = []
        # check which rows in dictionary query term is in
        for query_token in filtered_query:
            if query_token in dic.keys():
                rows.append(dic[query_token][1])
            elif query_token == 'AND' or query_token == 'OR' or query_token == 'NOT' or query_token == '(' or query_token == ')':
                continue
        rows.sort()
        
        # initialise list to get posting lists from postings.txt
        postings = []
    
        # find rows in postings.txt to get back posting lists
        # open postings.txt file and read file line by line to get the postings lists for terms in list 'rows' so that not the entire postings file is read onto memory
        with open("postings.txt","r") as file:
            for i, line in enumerate(file):
                for row in rows:
                    if i+1 == row:
                        postings.append(nltk.word_tokenize(line))
                    
        # iterate through each posting list line and convert docs to integer, if skip pointer is present convert to tuple
        for posting in postings:
            for i in range(0,len(posting)):
                if ',' in posting[i]:
                    posting[i] = (int(posting[i].split(',')[0]),int(posting[i].split(',')[1]))
                else:
                    posting[i] = int(posting[i])
        
        # create dictionary to store {query term:posting list} for easy access subsequently when evaluating query
        postingdic = {}
        for i in range(0,len(rows)):
            postingdic[list(dic)[rows[i]-1]]= postings[i]
        
        # apply shunting yard algorithm and evaluate result of filtered query
        outputs.append(shunting_yard(filtered_query,postingdic,diclen))
    
    # write out output for each line of query
    with open (results_file,'w+') as fp:
        for output in outputs:
            for doc in output:
                fp.write(str(doc)+" ")
            fp.write("\n")
        fp.close()
        
    
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
