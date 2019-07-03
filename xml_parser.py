from xml.etree import ElementTree as ET

# TODO: function that reads all XML files from input directory

with open('data/19105-data.xml', 'rb') as xml_file:
    tree = ET.parse(xml_file)

root = tree.getroot()

# extract data about speeces from XML protocol

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
        #print(rede)
        
        current_speaker = ''
        
        for subelement in rede:
            
            # extract metainformation about speaker
            
            if subelement.tag == 'p' and subelement.attrib['klasse'] == 'redner':
                    
                meta_dict = {}
                    
                for speaker_tag in subelement.iter():
                    if speaker_tag.tag == 'vorname':
                        meta_dict['vorname'] = speaker_tag.text
                    if speaker_tag.tag == 'nachname':
                        meta_dict['nachname'] = speaker_tag.text
                    if speaker_tag.tag == 'fraktion':
                        meta_dict['fraktion'] = speaker_tag.text
                        current_speaker = meta_dict['fraktion']
                    
            # extract content of comment
            
            if subelement.tag == 'kommentar':
                #print(kommentar.tag, kommentar.attrib)
                
                if current_speaker is None:
                    raise ValueError('Comment was found but no current speaker is set!')
                
                kommentar = subelement.text.strip('()').replace(u'\xa0', u' ')
                comment_list.append({'redner': current_speaker, 'kommentar': kommentar})
                    
print(comment_list)

if __name__ == "__main__":
    pass