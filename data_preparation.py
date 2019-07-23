from xml_parser import get_data
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

all_parties = []


def has_valid_speaker(comment):
    if comment['speaker'] == 'none':
        return False
    return True


def contains_applause(comment):
    if 'Beifall' in comment['comment']:
        # split comment at hyphen in case of several action within one comment
        sub_comments = comment['comment'].split(' – ')
        comment['comment'] = []
        for sub_comment in sub_comments:
            # replace comment content with list of parts containing applause
            # NOTE: length can be larger than 1
            if 'Beifall' in sub_comment:
                comment['comment'].append(sub_comment)
        return True
    return False

def split_calls(comment):
    
    # split comment at hyphen in case of several action within one comment
    sub_actions = comment['comment'].split(' – ')
    comment['comment'] = []
    for sub_action in sub_actions:
        # replace comment content with list of parts; separate speaker from actual content of call
        # NOTE: length can be larger than 1
        # TODO: look for "]," (speaker is usually on left side); otherwise search entire string for party or
        # TODO: search for this format: "Weiterer Gegenruf, des Abg. Johannes Kahrs [SPD]"
        
        # seperate single speaker given on left side of ":" as <name> [<party>]: <call>
                        
        if ":" in sub_action:
            call_left = sub_action.split(':')[0]
            
            if "]" in call_left[-1]:
                # find "Johannes Kahrs" case with speaker on left side of ":", but with "," left in call_left
                if ',' in call_left:
                        print(call_left)
                pass # all good, meaning this format for sub_action: <name> [<party>]: <call>
            
            # deal with case if extra information is given after [<party>] (usually specifies who single commenter addresses)
            # search for party in "caller_left"
            elif '],' in call_left:
                call_from_to = call_left.split(',')
                call_left = call_from_to[0]
                directed_at = call_from_to[1]
                pass
            else:
                # case of no single commenter; or single commenter is given in  right part for some reason
                # assumption: multiple calls from all parties left in this string
                if ',' in call_left:
                    pass
                    #print(call_left)
                
            
            
            comment['comment'].append(call_left)
        else:
            # no comment, but applause or something similar, can contain single and multiple acteurs
            if ',' in sub_action:
                if ']' in sub_action:
                    pass               
                    # print(sub_action)
            comment['comment'].append(sub_action)
    return True


def get_list_of_parties(comment_list):
    all_parties = set()
    for comment in comment_list:
        all_parties.add(comment['speaker'])
    return sorted(all_parties)


# TODO: get rid of last comment when speaker changes
# TODO: check whether party is surrounded by square brackets
def extract_applauding_party(sub_comments_list):
    global all_parties
    
    for sub_comment in sub_comments_list:
        matching = [party for party in all_parties if party in sub_comment]
        
        # check for "der LINKEN" and "des BÜNDNISSES...",
        if "der LINKEN" in sub_comment:
                matching.append("DIE LINKE")
                # print('manual add for LINKE: ', sub_comment)
        if "des BÜNDNISSES 90/DIE GRÜNEN" in sub_comment:
            matching.append("BÜNDNIS 90/DIE GRÜNEN")
            # print('manual add GRÜNE: ', sub_comment)
        
        # check for "ganzen Hause" or just "Beifall"
        if len(matching) == 0:
            # TODO: use string in sub_comment
            if sub_comment == "Beifall" or sub_comment == "Beifall im ganzen Hause" or sub_comment == "Beifall bei Abgeordneten im ganzen Hause":
                matching = all_parties
        # print(matching)
        if len(matching) == 0:
            print(f'Error: no party applauding could be found for comment: {sub_comment}!')
    return matching


def get_data_matrix_applause(comment_list):
    comment_list_applause = list(filter(contains_applause, comment_list))
    
    global all_parties
    all_parties = get_list_of_parties(comment_list_applause)
    
    # dictionary with party being applauded as key and dictionary as value
    # value dictionary maps party applauding to value to measure how often party is being applauded
    dict_applause = {}
    for party_from in all_parties:
        dict_applause[party_from] = {}
        for party_to in all_parties:
            dict_applause[party_from][party_to] = 0
    
    for comment in comment_list_applause:
        # print(comment['comment'])
        parties_applauding = extract_applauding_party(comment['comment'])
        # print(comment['speaker'], parties_applauding)
        # print(parties_applauding)
        
        # add dict of parties applauding to exisiting dict in dict_applause for speaking party
        # TODO: set value proportional to amount of people clapping / number of MOPs of party
        for party in parties_applauding:
            if party in dict_applause[comment['speaker']]:
                dict_applause[comment['speaker']][party] += 1
            else: 
                dict_applause[comment['speaker']][party] = 1
        #print(dict_applause)
    
    #print(all_parties)
    return dict_applause


# TODO: get rid of last comment when speaker changes
# TODO: check whether party is surrounded by square brackets
# TODO: extract party commenting from left part of ':'; comment might be about another party
def extract_commenting_party(comment_str):
    global all_parties
    
    matching = [party for party in all_parties if party in comment_str]
    
    # check for "der LINKEN" and "des BÜNDNISSES...",
    if "der LINKEN" in comment_str:
        matching.append("DIE LINKE")
        #print('manual add for LINKE: ', sub_comment)
    if "des BÜNDNISSES 90/DIE GRÜNEN" in comment_str:
        matching.append("BÜNDNIS 90/DIE GRÜNEN")
        # print('manual add GRÜNE: ', sub_comment)
    
    # check for "ganzen Hause" or just "Beifall"
    if len(matching) == 0:
        if comment_str == "Beifall" or comment_str == "Beifall im ganzen Hause":
            matching = all_parties
    # print(matching)
    if len(matching) == 0:
        # raise ValueError(f'Error: no party applauding could be found for comment: {sub_comment}!')
        print(f'Error: no party commenting could be found for comment: {comment_str}!')
    return matching


def get_data_matrix_comments(comment_list):
    global all_parties
    all_parties = get_list_of_parties(comment_list)
    
    # dictionary with party being applauded as key and dictionary as value
    # value dictionary maps party applauding to value to measure how often party is being applauded
    dict_comments = {}
    for party_from in all_parties:
        dict_comments[party_from] = {}
        for party_to in all_parties:
            dict_comments[party_from][party_to] = 0
    
    for comment in comment_list:
        parties_commenting = extract_commenting_party(comment['comment'])
        
        # TODO: remove
        #if comment['speaker'] in parties_commenting:
            #print(comment['speaker'], ' :', comment['comment'])
        
        # TODO: set value proportional to amount of people commenting / number of MOPs of party
        
        for party in parties_commenting:
            if party in dict_comments[comment['speaker']]:
                dict_comments[comment['speaker']][party] += 1
            else: 
                dict_comments[comment['speaker']][party] = 1
    
    # print(all_parties)
    return dict_comments


def create_heatmap(dict_parties, label):
    # convert nested dict to dataframe using pandas
    df = pd.DataFrame.from_dict(dict_parties)
    df = df.reindex(sorted(df.columns), axis=1)
    # print(df)
    
    ax = sns.heatmap(df, cmap='RdYlGn_r', linewidths=0.5, annot=True, fmt='d')
    if label == "Beifall":
        ax.set_title('Beifall von ... für ...')
    elif label == "Kommentare":
        ax.set_title('Kommentare von ... für ...')
    else:
        raise ValueError('Invalid label given for heatmap!')
    plt.show()


if __name__ == "__main__":

    """
    comment_list = get_data()
    # filters comments with speaker 'none'
    comment_list = list(filter(has_valid_speaker, comment_list))
    dict_applause = get_data_matrix_applause(comment_list)
    create_heatmap(dict_applause, 'Beifall')
    """
    
    # TODO: work on copy of list is "filter" function, otherwise comment_list gets overwritten
    comment_list = get_data()
    # filters comments with speaker 'none'
    comment_list = list(filter(has_valid_speaker, comment_list))
    #comment_list = list(filter(split_calls, comment_list))
    
    dict_comments = get_data_matrix_comments(comment_list)
    create_heatmap(dict_comments, 'Kommentare')

