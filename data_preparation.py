from xml_parser import get_data


def has_valid_speaker(comment):
    if comment['speaker'] == 'none':
        return False
    return True


comment_list = get_data()

# filters comments with speaker 'none'
comment_list = list(filter(has_valid_speaker, comment_list))

# TODO: use parties which give it instead of True/False
for comment in comment_list:
    if 'Beifall' in comment['comment']:
        comment['Beifall'] = True
    else:
        comment['Beifall'] = False

print(comment_list)

