from xml.etree import ElementTree as ET
import os
import pickle


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


def get_data():
    trees = get_xml_files()

    comment_list = []

    for xml_tree in trees:
        root = xml_tree.getroot()

        # extract date
        date = ''
        for datum in root.iter('datum'):
            date = datum.attrib['date']

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
                    comment = comments.text.strip('()').replace(u'\xa0', u' ')
                    comment_list.append({'speaker': current_speaker, 'comment': comment, 'date': date})
    filename = 'data/comments'
    serialization(comment_list, filename)


def serialization(comment_list, filename):
    with open(filename, 'wb') as pickle_file:
        pickle.dump(comment_list, pickle_file)


if __name__ == "__main__":
    pass
