from xml.etree import ElementTree as ET

# TODO: function that reads all XML files from input directory

with open('data/19105-data.xml', 'rb') as xml_file:
    tree = ET.parse(xml_file)

root = tree.getroot()

# nach Tagesordnungspunkten in Sitzungsverlauf suchen
comment_list = []
for topic in root[1]:
    if not 'top-id' in topic.attrib:
        continue
    elif topic.attrib['top-id'] == 'Geschaeftsordnung':
        continue
    #print(topic.tag, topic.attrib)
    
    for rede in topic:
        if rede.tag != 'rede':
            continue
        #print(rede.tag, rede.attrib)
        
        for kommentar in rede:
            if kommentar.tag == 'kommentar':
                #print(kommentar.tag, kommentar.attrib)
                k_text = kommentar.text.strip('()').replace(u'\xa0', u' ')
                comment_list.append(k_text)
                    
print(comment_list)

if __name__ == "__main__":
    pass