#import xml.etree.ElementTree as ET
 

#a = []
"""with open('book.xml', 'r') as f:
    a = f.readlines()
    #print(a+"\n")
    

f.close()"""
b = bytes("end", 'utf-8')
c = bytes("end",'utf-8')
print(b==c)



# Passing the path of the
# xml document to enable the
# parsing process
'''tree = ET.parse('book.xml')
 
# getting the parent tag of
# the xml document
root = tree.getroot()


for sub_root in root:
	for sub_tag in su:
		print sub_tag.text
# printing the root (parent) tag
# of the xml document, along with
# its memory location
print(root)
 
# printing the attributes of the
# first tag from the parent
print(root[0].attrib)

 
# printing the text contained within
# first subtag of the 5th tag from
# the parent
print(root[5][1].text)

print(root[0])'''