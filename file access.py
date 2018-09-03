import string        #use string library

 import re                         #use regular expression library

 inputfile = "c:\Work\CNET\Inventory.txt"      #set "inputfile" to be the name of the delimitated file.

 outputfile = "c:\Work\CNET\inv.txt"     #set "outputfile" to the name of the output file.

 f = open(inputfile)                        #open "inputfile" for reading

 o = open(outputfile, "w")              #open "outputfile" for writing              

 while (1):                                       #process the input file
    offset =0                                 #the first 30 charater field offset
    line = f.readline()                       #assign the current line to "line"
    if not line : break                       #exit the while loop at the end of the file
    line = line.rstrip()                      #remove the newline character (and any ending whitespaces)
    cols = line.split('\t')                   #split on tabs
    splitme = cols[6]                #set "splitme" to be the data from the 7th column
    splitup = list(splitme)       #set "splitup" to be a list of characters from the string "splitme"
    p = re.compile('\s')          #compile a regular expression object "p" to find spaces.
    if len(splitup) > 30:         #if the item description contains more than 30 characters
        for i in range(11):       #count from 0 to 10
            m = p.match(splitup[(30 -i)]) #find the first space
            if m:                                          #when found ...
                splitup[(30 - i)] = '\t' #replace the space with a tab
                offset = i        #set "offset" for defining the next 30 character field
                i = 10                   # end the for loop
          #end if
        #end for
        newguy = string.join(splitup,'') + '\t'  #make the list a string
        next = 60 - offset               #where to end the next 30 character field
        if len(splitup) > next:                 #if there needs to be 3 fields
            for i in range(11):
                m = p.match(splitup[(next - i)])
                if m:
                    splitup[(next - i)] = '\t';
                    i = 10
                    newguy = string.join(splitup,'')
              #end if
          #end for
        #end if
    #end if
    else:
        newguy = string.join(splitup,'') + "\t\t"      #if the description was less than 30 characters make two empty fields
    if len(splitup) <= 0 :
        newguy = "\t\t\t"                #if no description is given make 3 empty fields
    cols[6] = newguy                     #insert 3 field description into list
    newline = string.join(cols, '\t')           #create output string
    o.write( newline + '\n')                    #write output string to file.
    #print newline

 #end while
