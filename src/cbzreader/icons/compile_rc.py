############################################################
#
print "create qrc file"
#
############################################################
from glob import glob
from xml.dom.minidom import Document

doc = Document()
rcc = doc.createElement("RCC")
doc.appendChild(rcc)

root = doc.createElement("qresource")
root.attributes["prefix"] = "/images"
rcc.appendChild(root)

for name in sorted(glob("*.png") ) :
	node = doc.createElement("file")
	txt = doc.createTextNode(name)
	node.appendChild(txt)
	root.appendChild(node)

f = open("icons.qrc", 'w')
f.write(rcc.toxml() )
f.close()

############################################################
#
print "compile qrc file"
#
############################################################
from subprocess import check_call

out_file = "../icons_rc.py"
check_call("pyrcc4 -o %s %s" % (out_file,"icons.qrc"), shell = True)

############################################################
#
print "clean up"
#
############################################################
from os import remove

remove("icons.qrc")

