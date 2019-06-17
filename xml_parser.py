from xml.etree import ElementTree as ET

# TODO: function that reads all XML files from input directory

tree = ET.parse("data/19105-data.xml")
root = tree.getroot()
for child in root:
    print(child.tag, child.attrib)
print('-------')

# nach Tagesordnungspunkten in Sitzungsverlauf suchen
for child in root[1]:
    if not 'top-id' in child.attrib:
        continue
    elif child.attrib['top-id'] == 'Geschaeftsordnung':
        continue
    
    print(child.tag, child.attrib)
    
    for subchild in child:
        if subchild.tag != 'rede':
            continue
        print(subchild.tag, subchild.attrib)

if __name__ == "__main__":
    pass