from xml_parser import get_data
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json

all_parties = set()
seat_distribution = []


def get_seat_distribution(session_year):
    if session_year == 19:
        distribution = json.load(open('data/seat_distribution19.json'))
        return distribution
    else:
        return None


def get_list_of_parties(comment_list):
    """
    Extracts all parties from comment_list and returns set with alphabetically sorted names.
    """
    for comment in comment_list:
        all_parties.add(comment['speaker'])
    return sorted(all_parties)


def has_valid_speaker(comment):
    if comment['speaker'] == 'none':
        return False
    return True


def extract_commenting_party(comment):
    """
    Input argument is comment dict from comment_list. Comment is reduced to relevant part
    containing party. Function returns nested dict with indices [party_from][party_to]
    and value for number of actions each.
    TODO: set value according to size of party if there are multiple commenters / participants
    """
    
    global all_parties
    dict_all = {}
    for party_from in all_parties:
        dict_all[party_from] = {}
        for party_to in all_parties:
            dict_all[party_from][party_to] = 0
    
    party_found = False
    
    # split comment at hyphen in case of several action within one comment
    sub_actions = comment['comment'].split(' – ')
    
    for sub_action in sub_actions:
        # seperate single speaker given on left side of ":" as <name> [<party>]: <call>
        if ":" in sub_action:
            call_left = sub_action.split(':')[0]
            
            # check if party is really given right before <call>
            if "]" in call_left[-1]:
    
                # find cases like "Weiterer Gegenruf, des Abg. Johannes Kahrs [SPD]" with speaker on left side of ":", but with "," left in call_left
                if ',' in call_left:
                        # print(call_left)
                        pass
                
                # all good, meaning this format for sub_action: <name> [<party>]: <call>
            
            # deal with case if extra information is given after [<party>] (usually specifies who single commenter addresses)
            # example format of sub_action: Kai Gehring [BÜNDNIS 90/DIE GRÜNEN], an die AfD gewandt: <call>
            # TODO: search for party in "caller_left"
            elif '],' in call_left:
                call_from_to = call_left.split(',')
                call_left = call_from_to[0]
                
                # ignore directed_at; search for party in "call_left" part
                directed_at = call_from_to[1]
            
            # case of single commenter without party or multiple commenters are not specified
            # examples for call_left: "Bettina Hagedorn, Parl. Staatssekretärin", "Zurufe von der SPD, der LINKEN und dem BÜNDNIS 90/DIE GRÜNEN"
            else:
                if ',' in call_left:
                    #print(call_left)
                    pass
                
            # condense sub_action to relevant part containing caller
            sub_action = call_left
        
        # no calls, but applause or something similar, can contain single and multiple participants
        # TODO: search for [party] and just party, maybe subtract "[party]" hits from "party" matches
        else:
            if ',' in sub_action:
                if ']' in sub_action:
                    #print(sub_action)
                    pass
            
        # search for party in sub_action
        for party in all_parties:
            count_single = sub_action.count(f'[{party}]')
            dict_all[party][comment['speaker']] += count_single
            count_multiple = sub_action.count(party)-count_single
            # TODO: multiply count_multiple with number proportionate to number of MEPs per party
            # TODO: meaningful scale
            # values of seat distribution <1 and >0
            count_multiple = int(count_multiple * seat_distribution[party])
            dict_all[party][comment['speaker']] += count_multiple
            
            if count_single > 0 or count_multiple > 0:
                party_found = True
        
        # check for "der LINKEN" and "des BÜNDNISSES...",
        if "der LINKEN" in sub_action:
            party_found = True
            dict_all["DIE LINKE"][comment['speaker']] += 1
        if "des BÜNDNISSES 90/DIE GRÜNEN" in sub_action:
            party_found = True
            dict_all["BÜNDNIS 90/DIE GRÜNEN"][comment['speaker']] += 1
        
        # check for "ganzen Hause" or just "Beifall"; ignore "Heiterkeit", "Zurufe" etc.
        if sub_action == "Beifall" or sub_action == "Beifall im ganzen Hause" \
        or sub_action == "Beifall bei Abgeordneten im ganzen Hause":
            party_found = True
            for party_from in dict_all:
                dict_all[party_from][comment['speaker']] += 1
                
        if not party_found:
            print(f'Error: no party commenting could be found for comment: {sub_action}!')
        
    return dict_all


def get_data_matrix_comments(comment_list):
    """
    Returns nested dict for comment_list with indices [party_from][party_to] containing number
    of actions each. Sums up values per comment for entire comment_list.
    """
    
    global all_parties
    all_parties = get_list_of_parties(comment_list)
    
    # dictionary with party applauding as key and dictionary as value
    # value maps party applauding to how often every other party is being applauded
    dict_comments = {}
    for party_from in all_parties:
        dict_comments[party_from] = {}
        for party_to in all_parties:
            dict_comments[party_from][party_to] = 0
    
    for comment in comment_list:
        parties_commenting = extract_commenting_party(comment)
        for party_from in parties_commenting:
            for party_to in parties_commenting[party_from]:
                dict_comments[party_from][party_to] += parties_commenting[party_from][party_to]
    
    return dict_comments


def contains_applause(comment):
    """
    Replace comment string inside comment dict with list of relevant substrings containing
    "Beifall" to simplify search for party. Returns true if comment contains "Beifall".
    """
    
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


# TODO: get rid of last comment when speaker changes perhaps?
# TODO: check whether party is surrounded by square brackets
# TODO: change this to something similar to extract_commenting_party?
def extract_applauding_party(sub_comments_list):
    """
    Returns list of parties applauding in list of string that were part of original comment
    and contain "Beifall". This does not take into account whether the party is given in brackets.
    TODO: merge this function with contains_applause to create something similar to extract_commenting_party.
    """
    
    global all_parties
    
    for sub_comment in sub_comments_list:
        matching = [party for party in all_parties if party in sub_comment]
        
        # check for "der LINKEN" and "des BÜNDNISSES...",
        if "der LINKEN" in sub_comment:
                matching.append("DIE LINKE")
        if "des BÜNDNISSES 90/DIE GRÜNEN" in sub_comment:
            matching.append("BÜNDNIS 90/DIE GRÜNEN")
        
        # check for "ganzen Hause" or just "Beifall"
        if len(matching) == 0:
            if sub_comment == "Beifall" or sub_comment == "Beifall im ganzen Hause" or sub_comment == "Beifall bei Abgeordneten im ganzen Hause":
                matching = all_parties
        if len(matching) == 0:
            print(f'Error: no party applauding could be found for comment: {sub_comment}!')
    return matching


def get_data_matrix_applause(comment_list):
    """
    Returns nested dict with indices [party_from][party_to] containing number of applause given
    each for entire comment_list.
    """
    
    comment_list_applause = list(filter(contains_applause, comment_list))
    
    global all_parties
    all_parties = get_list_of_parties(comment_list)
    
    dict_applause = {}
    for party_from in all_parties:
        dict_applause[party_from] = {}
        for party_to in all_parties:
            dict_applause[party_from][party_to] = 0
    
    # dictionary with party applauding as key and dictionary as value
    # value maps party applauding to value to measure how often each party is being applauded
    for comment in comment_list_applause:
        parties_applauding = extract_applauding_party(comment['comment'])
        
        # add dict of parties applauding to exisiting dict in dict_applause for speaking party
        # TODO: set value proportional to amount of people clapping / number of MOPs of party
        for party in parties_applauding:
            if party in dict_applause:
                dict_applause[party][comment['speaker']] += 1
            else:
                dict_applause[party][comment['speaker']] = 1
    
    return dict_applause


def create_heatmap(dict_parties, label):
    # convert nested dict to dataframe using pandas
    df = pd.DataFrame.from_dict(dict_parties)
    df = df.reindex(sorted(df.columns), axis=1)
    
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
    comment_list = list(filter(has_valid_speaker, comment_list))
    dict_applause = get_data_matrix_applause(comment_list)
    create_heatmap(dict_applause, 'Beifall')
    """
    
    # TODO: work on copy of list is "filter" function, otherwise comment_list gets overwritten
    seat_distribution= get_seat_distribution(19)
    comment_list = get_data()
    comment_list = list(filter(has_valid_speaker, comment_list))
    dict_comments = get_data_matrix_comments(comment_list)
    create_heatmap(dict_comments, 'Kommentare')

