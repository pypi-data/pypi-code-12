--- itemData.py	(original)
+++ itemData.py	(refactored)
@@ -17,7 +17,7 @@
 """
 import unicodecsv
 import sqlite3
-import urllib2
+import urllib.request, urllib.error, urllib.parse
 
 class contextItem(object):
     __numEnteries = 4
@@ -38,7 +38,7 @@
         return self.__category[:]
     def categoryString(self):
         """return the categories as a string delimited by '_'"""
-        return u'_'.join(self.__category)
+        return '_'.join(self.__category)
 
 
     def isA(self,testCategory):
@@ -56,13 +56,13 @@
     def getRule(self):
         return self.__rule
     def __unicode__(self):
-        txt = u"""literal<<%s>>; category<<%s>>; re<<%s>>; rule<<%s>>"""%(
+        txt = """literal<<%s>>; category<<%s>>; re<<%s>>; rule<<%s>>"""%(
             self.__literal,self.__category,self.__re, self.__rule)
         return txt
     def __str__(self):
-        return unicode(self).encode('utf-8')
+        return str(self).encode('utf-8')
     def __repr__(self):
-        return unicode(self).encode('utf-8')
+        return str(self).encode('utf-8')
    
 class itemData(list):
     def __init__(self,*args):
@@ -120,15 +120,15 @@
                 itm = contextItem(i)
             super(itemData,self).append(itm)
     def __unicode__(self):
-        tmp = u"""itemData: %d items ["""%len(self)
+        tmp = """itemData: %d items ["""%len(self)
         for i in self:
             tmp = tmp+"%s, "%i.getLiteral()
         tmp = tmp+"]"
         return tmp
     def __repr__(self):
-        return unicode(self).encode('utf-8')
+        return str(self).encode('utf-8')
     def __str__(self):
-        return unicode(self).encode('utf-8')
+        return str(self).encode('utf-8')
 
 def instantiateFromCSV(csvFile, encoding='utf-8'):
     """takes a CSV file of itemdata rules and creates itemData instances.
@@ -145,7 +145,7 @@
 #        print case
             category = items.get(case,itemData())
             tmp = row[1:5]
-            tmp[2] = ur"%s"%tmp[2] # convert the regular expression string into a raw string
+            tmp[2] = r"%s"%tmp[2] # convert the regular expression string into a raw string
             item = contextItem(tmp)
             category.append(item)
             items[case] = category
@@ -174,18 +174,18 @@
 
     items = itemData() # itemData to be returned to the user
     header = []
-    f0 =  urllib2.urlopen(csvFile,'rU')
+    f0 =  urllib.request.urlopen(csvFile,'rU')
     reader = unicodecsv.reader(f0, encoding=encoding, delimiter="\t" )
     #reader = csv.reader(open(csvFile, 'rU'))
     # first grab numbe rof specified header rows
     for i in range(headerRows):
-        row = reader.next()
+        row = next(reader)
         header.append(row)
     # now grab each itemData
     for row in reader:
         tmp = [row[literalColumn], row[categoryColumn],
             row[regexColumn], row[ruleColumn]]
-        tmp[2] = ur"%s"%tmp[2] # convert the regular expression string into a raw string
+        tmp[2] = r"%s"%tmp[2] # convert the regular expression string into a raw string
         item = contextItem(tmp)
         items.append(item)
     f0.close()
@@ -209,7 +209,7 @@
     for row in c.execute(ex_cmd , (label, )):
         tmp = [row[0], row[1], 
                row[2], row[3]]
-        tmp[2] = ur"%s"%tmp[2]
+        tmp[2] = r"%s"%tmp[2]
         item = contextItem(tmp)
         items.append(item)
         
