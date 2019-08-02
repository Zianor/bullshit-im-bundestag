from xml_parser import get_data
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os.path
import pickle

all_parties = set()
seat_distribution = {}
seats_total = {}
attendance_rate = 0.2
percentage_participating = 0.2
initialized = False


def get_seat_distribution(session_year):
    """
        Set global dict seat_distribution for seat distripution in percent.
        Throws an exception if JSON for session_year does not exist.
        """
    global seat_distribution
    if session_year == 19:
        with open('data/seat_distribution19.json', encoding='utf-8') as seat_file:
            seat_distribution = json.load(seat_file)
            return seat_distribution
    else: 
        return None


def get_seats_total(session_year):
    """
    Set global dict seats_total for number of seats per party and total number
    of seats. Helper function for extract_commenting/applauding_party.
    Throws an exception if JSON for session_year does not exist.
    """
    
    global seats_total
    file_name = f'data/seats_total{session_year}.json'
    with open(file_name, encoding='utf-8') as seat_file:
        seats_total = json.load(seat_file)
    return seats_total
    

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


def get_party_dict():
    global all_parties
    dict_all = {}
    for party_from in all_parties:
        dict_all[party_from] = {}
        for party_to in all_parties:
            dict_all[party_from][party_to] = 0
    return dict_all


def extract_commenting_party(comment):
    """
    Input argument is comment dict from comment_list. Comment is reduced to relevant part
    containing party. Function returns nested dict with indices [party_from][party_to]
    and value for number of actions each.
    TODO: set value according to size of party if there are multiple commenters / participants
    """

    global attendance_rate, percentage_participating
    dict_all = get_party_dict()

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
            # TODO: why do we have attendance_rate and percentage_participating? Shouldn't we use only one of them?
            count_multiple *= int(max(seats_total[party]*attendance_rate*percentage_participating, 1))
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


def get_data_matrix_comments(comment_list, relative=False):
    """
    Returns nested dict for comment_list with indices [party_from][party_to] containing number
    of actions each. Sums up values per comment for entire comment_list.
    """
    
    if not initialized:
        initialize(comment_list)
    
    # dictionary with party commenting as key and dictionary as value
    # value maps party commenting to how often every other party is being applauded
    dict_comments = get_party_dict()
    
    for comment in comment_list:
        parties_commenting = extract_commenting_party(comment)
        for party_from in parties_commenting:
            for party_to in parties_commenting[party_from]:
                dict_comments[party_from][party_to] += parties_commenting[party_from][party_to]
    
    if relative:
        for party_from in parties_commenting:
            for party_to in parties_commenting[party_from]:
                dict_comments[party_from][party_to] /= seats_total[party_from]
    
    return dict_comments


def contains_applause(comment):
    if 'Beifall' in comment['comment']:
        return True
    return False


# TODO: get rid of last comment when speaker changes perhaps?
def extract_applauding_party(comment):
    """
    Returns list of parties applauding in list of string that were part of original comment
    and contain "Beifall". This does not take into account whether the party is given in brackets.
    """
    
    global all_parties

    sub_comments = comment.split(' – ')
    sub_comments_list = []
    for sub_comment in sub_comments:
        # replace comment content with list of parts containing applause
        # NOTE: length can be larger than 1
        if 'Beifall' in sub_comment:
            sub_comments_list.append(sub_comment)

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


def initialize(comment_list):
    global initialized, seat_distribution, seats_total, all_parties
    get_seat_distribution(19)
    get_seats_total(19)
    all_parties = get_list_of_parties(comment_list)
    initialized = True


def get_data_matrix_applause(comment_list, relative=False):
    """
    Returns nested dict with indices [party_from][party_to] containing number of applause given
    each for entire comment_list.
    """
    global initialized
    comment_list_applause = list(filter(contains_applause, comment_list))

    if not initialized:
        initialize(comment_list)

    dict_applause = get_party_dict()
    
    # dictionary with party applauding as key and dictionary as value
    # value maps party applauding to value to measure how often each party is being applauded
    for comment in comment_list_applause:
        parties_applauding = extract_applauding_party(comment['comment'])
        for party in parties_applauding:
            if party in dict_applause:
                dict_applause[party][comment['speaker']] += 1
            else:
                dict_applause[party][comment['speaker']] = 1

    # TODO: ergibt das hier überhaupt Sinn mit dem Relativ?
    if relative:
        for party_from in all_parties:
            for party_to in all_parties:
                dict_applause[party_from][party_to] /= seats_total[party_from]
    
    return dict_applause


def create_heatmap(dict_parties, label):
    # convert nested dict to dataframe using pandas
    df = pd.DataFrame.from_dict(dict_parties)
    df = df.reindex(sorted(df.columns), axis=1)

    sns.set(font_scale=0.8)

    ax = sns.heatmap(df, cmap='Blues', annot=True, fmt='.1f')
    plt.title(f'{label} von ... für ...\n\n')
    plt.show()


def load_data(renew_data):
    if renew_data or not os.path.exists('data/comments'):
        get_data()
    comments = None
    with open('data/comments', 'rb') as comment_file:
        comments = pickle.load(comment_file)
    return comments


def create_distribution_self_other(dict_parties):
    distribution_self_other = {}
    for party_from in all_parties:
        distribution_self_other[party_from] = {}
        sum_all = 0
        sum_self = dict_parties[party_from][party_from]
        for party_to in all_parties:
            sum_all += dict_parties[party_from][party_to]
        sum_others = sum_all - sum_self
        distribution_self_other[party_from]['self'] = sum_self/sum_all*100
        # distribution_self_other[party_from]['other'] = sum_others/sum_all*100
    return distribution_self_other


def visualize_distribution_self_other(dict_parties, label):
    df = pd.DataFrame.from_dict(dict_parties)
    df = df.reindex(sorted(df.columns), axis=1)

    sns.set(font_scale=0.8)

    # TODO: search better visual representation (with self and other as stacked bar plot)
    ax = sns.barplot(data=df)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right")
    plt.tight_layout()
    plt.title(f'{label}')
    plt.show()


if __name__ == "__main__":
    comment_list = load_data(False)
    comment_list_filtered = list(filter(has_valid_speaker, comment_list))
    initialize(comment_list_filtered)

    dict_applause = get_data_matrix_applause(comment_list_filtered, relative=True)
    create_heatmap(dict_applause, 'Beifall relativ')
    dict_applause_self = create_distribution_self_other(dict_applause)
    visualize_distribution_self_other(dict_applause_self, 'Beifall für die eigene Partei in %')

    dict_comments = get_data_matrix_comments(comment_list_filtered, relative=True)
    create_heatmap(dict_comments, 'Kommentare relativ')
    dict_comment_self = create_distribution_self_other(dict_comments)
    visualize_distribution_self_other(dict_comment_self, 'Kommentare zur eigenen Partei in %')
