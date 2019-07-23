from xml.etree import ElementTree as ET
import os


def get_xml_files():
    files = os.listdir('data')
    xml_files = []
    for file in files:
        if file.endswith('.xml'):
            xml_files.append('data/' + file)
    xml_trees = list(xml_files)
    print(xml_trees)
    
    for i in range(0, len(xml_files)):
        with open(xml_files[i], 'rb') as xml_file:
            xml_trees[i] = ET.parse(xml_file)
    return xml_trees


def get_data():
    trees = get_xml_files()

    comment_list = []

    # TODO: remove after testing
    trees = trees[:]
    print(trees)
    print(len(trees))

    for xml_tree in trees:
        root = xml_tree.getroot()
        print('got here')

        # extract date
        date = ''
        for datum in root.iter('datum'):
            date = datum.attrib['date']
            print(date)

        # extract data about speeches from XML protocol
        for topic in root.iter('tagesordnungspunkt'):
            if topic.attrib['top-id'] == 'Geschaeftsordnung':
                continue
            for rede in topic.iter('rede'):
                # extract metainformation about speaker
                current_speaker = 'none'  # e.g if speaker is announced
                for speaker in rede.iter('redner'):
                    meta_dict = {}

                    for speaker_tag in speaker.iter():
                        if speaker_tag.tag == 'vorname':
                            meta_dict['vorname'] = speaker_tag.text
                        if speaker_tag.tag == 'nachname':
                            meta_dict['nachname'] = speaker_tag.text
                        if speaker_tag.tag == 'fraktion':
                            meta_dict['fraktion'] = speaker_tag.text
                            current_speaker = meta_dict['fraktion']

                # extract content of comment
                for comments in rede.iter('kommentar'):
                    if comments == 'Beifall bei der SPD, der CDU/CSU, der FDP und dem BÜNDNIS 90/DIE GRÜNEN sowie bei Abgeordneten der AfD':
                        print('Found it in 19108!')
                    comment = comments.text.strip('()').replace(u'\xa0', u' ')
                    
                    comment_list.append({'speaker': current_speaker, 'comment': comment, 'date': date})
    return comment_list
    
# TODO: serialization of comment_list


if __name__ == "__main__":
    pass