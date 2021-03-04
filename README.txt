This is the README file for A0230632U's submission

Email : e0698539@u.nus.edu

== Python Version ==

I'm using Python Version <3.7.7> for
this assignment.

== General Notes about this assignment ==

This program contains of two main files index.py and search.py.
index.py reads in multiple documents from a folder and creates a dictionary file and postings file. The documents are read through and 
tokenized as well as stemmed to create a dictionary of terms and their posting lists which may be retrieved during searching and querying.
The dictionary file consists of the term, its document frequency and a pointer to the postings file while the postings file consists of the 
posting lists of each term, with the skip pointers implemented. Due to difficulty in producing an index construction algorithm, index.py 
utilises a naive form of creating both the dictionary and postings file. 

search.py reads in a query file consisting of different queries, each occupying a line. The operators in the search queries include 'AND','OR','NOT','(' and ')'.
Edsger Dijkstra's shunting yard algorithm is used to parse these Boolean expressions to produce a postfix expression which will subsequently be evaluated for 
each query to return a list of documents in the form of DocID separated by single spaces.

== Files included with this submission ==

index.py : source code for indexing documents
search.py : source code for returning output for queries
dictionary.txt : pickled file which consists of dictionary of format {term: (docfreq,pointer)} 
postings.txt : each line consists of the postings list of each term. docIDs are separated by single spaces and ',' indicates the presence of a skip pointer e.g docID,skip pointer docID

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] I/We, A0230632U, certify that I/we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I/we
expressly vow that I/we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

== References ==

Referenced to piaza forum 
