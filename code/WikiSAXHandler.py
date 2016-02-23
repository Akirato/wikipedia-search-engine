#/usr/bin/python
#coding: utf8

import xml.sax as sax
import re
import Indexer

INFOBOX_START_STRING = u"{{Infobox"
infobox_start_detection = re.compile(INFOBOX_START_STRING,re.I)
CITE_START_STRING = u"{{cite"
cite_start_detection = re.compile(CITE_START_STRING,re.I)

external_links_detection = re.compile(u"http[^\s]+\s",re.I|re.M)
flower_detection = re.compile("{{(.*?)}}");

redirect_detection = re.compile(u"#REDIRECT\s?\[\[(.*?)\]\]",re.I)
stub_detection = re.compile(u"-stub}}")
disambig_detection = re.compile(u"{{disambig}}")
category_detection = re.compile(u"\[\[Category:(.*?)\]\]",re.M)
link_detection = re.compile(u"\[\[(.*?)\]\]",re.M)
relations_detection = re.compile(u"\[\[([^\[\]]+)\]\]",re.M|re.S)
section_detection = re.compile(u"^==([^=].*?[^=])==$",re.M)
sub_section_detection =re.compile(u"^===([^=].*?[^=])===$",re.M)

class WikiArticle(object):
    
    def __init__(self):
        self.title = ""
        self.id = ""
        self.revision_id = ""
        self.timestamp = ""
        self.contributer_username = ""
        self.contributer_id = ""
        self.minor = ""
        self.comment = ""
        self.text = ""
        self.infobox = {}
        self.infobox_string = ""
        self.infobox_values_string = ""
        self.infobox_type = ""
        self.categories = []
        self.external_links = []
        
    def processArticle(self):
        self.getInfoBoxValuesString()
        self.getCategories()
        self.getExternalLinks()
        self.makeTextAlphaNumeric()
        
    def getInfoBox(self):
        start_match = re.search(infobox_start_detection,self.text)
        if start_match:
            start_pos = start_match.start()
            if start_pos < 0 :
                return
            brack_count = 2
            end_pos = start_pos + len(INFOBOX_START_STRING)
            while(end_pos < len(self.text)):
                if self.text[end_pos] == '}':
                    brack_count = brack_count - 1
                if self.text[end_pos] == '{':
                    brack_count = brack_count + 1
                if brack_count == 0:
                    break
                end_pos = end_pos+1
            if end_pos+1 >= len(self.text):
                return
            self.infobox_string = self.text[start_pos:end_pos+1]
            self.text = self.text[0:start_pos] + " " + self.text[end_pos+1:]
            self.infobox_string = re.sub(u'<ref.*?>.*?</ref>|</?.*?>',' ',self.infobox_string)
            self.infobox_string = self.infobox_string.replace("&gt;",">").replace("&lt;", "<").replace("&amp;", "&") #.replace("<ref.*?>.*?</ref>", " ").replace("</?.*?>", " ")
            
            new_line_splits = self.infobox_string.split("\n")
            if new_line_splits:
                temp = new_line_splits[0].lower()
                pipe_find = temp.find("|")
                if pipe_find > 0 :
                    temp = temp[0:pipe_find]
                brack_find = temp.find("}}")
                if brack_find > 0 :
                    temp = temp[0:brack_find]
                gt_mark_find = temp.find("<!")
                if gt_mark_find > 0 :
                    temp = temp[0:gt_mark_find]
                temp = re.sub(u'{{infobox|\\n|#|_', ' ', temp).strip()
                self.infobox_type = temp
            for str in new_line_splits:
                if str.find("=") < 0 :
                    continue
                if str.find("{{") >= 0 :
                    bmatches = re.finditer(flower_detection, self.text)
                    if bmatches:
                        for bmatch in bmatches:
                            mtcd = bmatch.group(1)
                            changed = mtcd.replace("|", "-").replace("=", "-")
                            str.replace(mtcd, changed)
                if str.find("|") >= 0 :
                    piped_strings = str.split("|")
                    for ps in piped_strings:
                        key_val = ps.split("=")
                        
                        if len(key_val) != 2 :
                            continue
                        
                        key = re.sub(u'[|?{}[\]]+', ' ', key_val[0]).strip().lower()
                        #key = key_val[0].replace("|", "").replace("?", "").replace("{", "").replace("}", "").replace("[", "").replace("]", "").strip().lower()
                        val = re.sub(u'[|?{}[\]]+', ' ', key_val[1]).strip().lower()
                        #val = key_val[1].replace("|", "").replace("{", "").replace("}", "").replace("[", "").replace("]", "").strip().lower()
                        self.infobox[key] = val
        
    def removeCite(self, string_to_strip):
        start_match = re.search(cite_start_detection,self.text)
        if start_match:
            start_pos = start_match.start()
            if start_pos < 0 :
                return string_to_strip
            brack_count = 2
            end_pos = start_pos + len(INFOBOX_START_STRING)
            while(end_pos < len(self.text)):
                if self.text[end_pos] == '}':
                    brack_count = brack_count - 1
                if self.text[end_pos] == '{':
                    brack_count = brack_count + 1
                if brack_count == 0:
                    break
                end_pos = end_pos+1
            string_to_strip = string_to_strip[0:start_pos-1] + string_to_strip[end_pos:]
            return self.removeCite(string_to_strip)
        return string_to_strip
    
    def getInfoBoxValuesString(self):
        self.infobox_values_string = ''.join(self.infobox.values())
    
    def getInfoBoxType(self):
        if self.infobox_string:
            new_line_splits = self.infobox_string.split("\n")
            if new_line_splits:
                temp = new_line_splits[0].lower()
                pipe_find = temp.find("|")
                if pipe_find > 0 :
                    temp = temp[0:pipe_find]
                brack_find = temp.find("}}")
                if brack_find > 0 :
                    temp = temp[0:brack_find]
                gt_mark_find = temp.find("<!")
                if gt_mark_find > 0 :
                    temp = temp[0:gt_mark_find]
                temp = temp.replace("{{infobox", "").replace("\n", "").replace("#", "").replace("_"," ").strip()
                self.infobox_type = temp
        #print("infobox_type = {0}".format(self.infobox_type))
    
    def getCategories(self):
        matches = re.finditer(category_detection, self.text)
        if matches:
            for match in matches:
                temp = match.group(1).split("|")
                if temp:
                    self.categories.extend(temp)
        re.sub(category_detection, ' ', self.text) # this is for removing the category headings....
            
    
    def getExternalLinks(self):
        matches = re.finditer(external_links_detection, self.text)
        for match in matches:
            temp = match.group()
            if temp:
                self.external_links.append(temp)
        #for link in self.external_links:
            #print(link)
    
    def makeTextAlphaNumeric(self):
        self.title = re.sub(u'[^a-zA-Z0-9]+', ' ', self.title)
        
    
class WikiContentHandler(sax.ContentHandler):
    
    def __init__(self, outfile):
        sax.ContentHandler.__init__(self)
        self.elements = []
        self.parent_element = ""
        self.current_element = ""
        self.current_article = {}
        self.current_lines = []
        self.outfile = outfile
    
    def startElement(self, name, attrs):
        #print("The Element Pushed = {0}".format(name))
        self.elements.append(name)
        if self.current_element:
            self.parent_element = self.current_element
        self.current_element = name
        #self.current_characters = ""
        self.current_lines = []
        if name == "page":
            self.current_article = WikiArticle()
    
    def endElement(self, name):
        if name == "page":
            self.current_article.processArticle()    #### This is where the processing for the article starts........starts
            Indexer.doIndex(self.current_article, self.outfile)
            
        to_store = ""
        if len(self.current_lines):
            try:
                to_store = (''.join(self.current_lines)).strip()
            except Exception:
                print "exception occured at id={0} and title={1}\n {2}".format(self.current_article.id,self.current_article.title,Exception)
        if name == "title":
            self.current_article.title = to_store
        if name == "id":
            if self.parent_element == "page":
                self.current_article.id = to_store
        if name == "text":
            self.current_article.text = to_store
        self.elements.pop()
        if self.elements:
            self.current_element = self.parent_element
            if len(self.elements) == 1:
                self.parent_element = ""
            else:
                self.parent_element = self.elements[len(self.elements)-1]
        else:
            self.current_element = ""
    
    def characters(self, content):
        if content and self.current_element:
            self.current_lines.append(content)
            self.current_lines.append(" ")
