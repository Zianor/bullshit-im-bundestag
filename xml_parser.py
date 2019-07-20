from xml.etree import ElementTree as ET
import os


def get_xml_files():
    files = os.listdir('data')
    xml_files = []
    for file in files:
        if file.endswith('.xml'):
            xml_files.append('data/' + file)
    xml_trees = list(xml_files)
    for i in range(0, len(xml_files)):
        with open(xml_files[i], 'rb') as xml_file:
            xml_trees[i] = ET.parse(xml_file)
    return xml_trees


trees = get_xml_files()

comment_list_per_file = []

# TODO: remove after testing
trees = trees[0:2]

for xml_tree in trees:
    root = xml_tree.getroot()

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

    comment_list_per_file.append(comment_list)
    print("Liste einer Datei:")
    print(comment_list)


if __name__ == "__main__":
    pass
