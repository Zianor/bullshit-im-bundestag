from xml_parser import get_data
import json
import os.path

all_parties = set()
seats_total = {}
attendance_rate = 0.2
percentage_participating = 0.2
initialized = False
path_comments = ''


def get_seats_total(session_year):
    """
    Sets global dict seats_total for number of seats per party and total number
    of seats. Make sure the JSON file has the name: 'seats_totalYY.json'.
    Throws an exception if JSON for session_year does not exist. Returns
    seats_total after initialization.
    """
    global seats_total
    file_name = f'data/seats_total{session_year}.json'
    if not os.path.exists(file_name):
        raise ValueError(f'No JSON input data for session year {session_year} found!')
        
    with open(file_name, encoding='utf-8') as seat_file:
        seats_total = json.load(seat_file)
    return seats_total
    

def get_list_of_parties(comment_list):
    """
    Extracts all parties from comment_list (list containing comment dictionaries)
    and returns set with alphabetically sorted names.
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
    """
    global attendance_rate, percentage_participating
    dict_all = get_party_dict()

    party_found = False
    
    # split comment at hyphen in case of several actions within one comment
    sub_actions = comment['comment'].split(' – ')
    
    # track previous speaker in case parties address each other in calls
    previous_callers = []
    
    for sub_action in sub_actions:
        is_single_caller = False
        party_addressed = None
        
        # separate single speaker given on left side of ":" as <name> [<party>]: <call>
        if ":" in sub_action:
            call_left = sub_action.split(':')[0]
            
            # check if party is really given right before <call>
            if "]" in call_left[-1]:
    
                # find cases like "Weiterer Gegenruf, des Abg. Johannes Kahrs [SPD]" with speaker on left side of ":", but with "," left in call_left
                if ',' in call_left:
                        # print(call_left)
                        pass
            
            # deal with case if extra information is given after [<party>] (usually specifies who single commenter addresses)
            # example format of sub_action: Kai Gehring [BÜNDNIS 90/DIE GRÜNEN], an die AfD gewandt: <call>
            elif '],' in call_left:
                call_from_to = call_left.split(',')
                call_left = call_from_to[0]
                
                # evaluate directed_at to determine if call is directed at party other than current speaker
                # in this case, the call replies to a call by another party
                directed_at = call_from_to[1]
                if 'gewandt' in directed_at:
                    matching = [party for party in all_parties if party in directed_at]
                    if len(matching) != 1:
                        #print(f'Error: tried to find single party in directed_at part of call, but failed: {comment["comment"]}')
                        pass
                    else:
                        party_addressed = matching[0]
            
            is_single_caller = True
            
            if call_left.startswith("Gegenruf"):
                if len(previous_callers) == 0:
                    # Gegenruf zum Redeinhalt, nicht zu vorherigem Kommentar
                    previous_callers.append(comment['speaker'])
                #print(call_left, ' - ', previous_callers[-1], ' -\r\n', comment['comment'], '\r\n')
                party_addressed = previous_callers[-1]
                    
            elif call_left.startswith("Weiterer Gegenruf"):
                #print(call_left, ' - ', previous_callers[-2], ' -\r\n', comment['comment'], '\r\n')
                # TODO: does not work for more than two consecutive replies, but that has never occurred
                party_addressed = previous_callers[-2]
            
            # case of single commenter without party or multiple commenters are not specified
            # examples for call_left: "Bettina Hagedorn, Parl. Staatssekretärin", "Zurufe von der SPD, der LINKEN und dem BÜNDNIS 90/DIE GRÜNEN"
            else:
                if ',' in call_left:
                    #print(call_left)
                    pass
                
            # condense sub_action to relevant part containing caller
            sub_action = call_left
        
        # no calls, but applause or something similar, can contain single and multiple participants
        else:
            if sub_action.startswith("Zurufe"):
                single_caller = [party for party in all_parties if party in sub_action]
                caller = None
                if len(single_caller) == 0:
                    if "der LINKEN" in sub_action:
                        caller = "DIE LINKE"
                    elif "des BÜNDNISSES 90/DIE GRÜNEN" in sub_action:
                        caller = "BÜNDNIS 90/DIE GRÜNEN"
                else:
                    caller = single_caller[0]
                if caller is not None:
                    previous_callers.append(caller)
            if ',' in sub_action:
                if ']' in sub_action:
                    #print(sub_action)
                    pass
            
        # search for party in sub_action for tracking in case call is a reply to a previous call
        if is_single_caller and len(sub_actions) > 1 and 'Gegenruf' in comment['comment']:
            single_caller = [party for party in all_parties if party in sub_action]
            caller = None
            if len(single_caller) == 0:
                if "der LINKEN" in sub_action:
                    caller = "DIE LINKE"
                elif "des BÜNDNISSES 90/DIE GRÜNEN" in sub_action:
                    caller = "BÜNDNIS 90/DIE GRÜNEN"
            else:
                caller = single_caller[0]
            if caller is not None:
                previous_callers.append(caller)
            
        
        if party_addressed is None:
            party_addressed = comment['speaker']
        
        # create dictionary
        for party in all_parties:
            count_single = sub_action.count(f'[{party}]')
            dict_all[party][party_addressed] += count_single
            count_multiple = sub_action.count(party)-count_single
            
            count_multiple *= int(max(seats_total[party]*attendance_rate*percentage_participating, 1))
            dict_all[party][party_addressed] += count_multiple
            
            if count_single > 0 or count_multiple > 0:
                party_found = True
        
        # check for "der LINKEN" and "des BÜNDNISSES...",
        if "der LINKEN" in sub_action:
            party_found = True
            dict_all["DIE LINKE"][party_addressed] += int(max(seats_total["DIE LINKE"]*attendance_rate*percentage_participating, 1))
        if "des BÜNDNISSES 90/DIE GRÜNEN" in sub_action:
            party_found = True
            dict_all["BÜNDNIS 90/DIE GRÜNEN"][party_addressed] += int(max(seats_total["BÜNDNIS 90/DIE GRÜNEN"]*attendance_rate*percentage_participating, 1))
        
        # check for "ganzen Hause" or just "Beifall"; ignore "Heiterkeit", "Zurufe" etc.
        if sub_action == "Beifall" or sub_action == "Beifall im ganzen Hause" \
        or sub_action == "Beifall bei Abgeordneten im ganzen Hause":
            party_found = True
            for party_from in dict_all:
                dict_all[party_from][party_addressed] += int(max(seats_total[party_from]*attendance_rate*percentage_participating, 1))
                
        if not party_found:
            pass
            # print(f'Error: no party commenting could be found for comment: {sub_action}!')
        
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
        for party_from in dict_comments:
            for party_to in dict_comments[party_from]:
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
            pass
            # print(f'Error: no party applauding could be found for comment: {sub_comment}!')
    return matching


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
            dict_applause[party][comment['speaker']] += 1
                
    if relative:
        for party_from in all_parties:
            for party_to in all_parties:
                dict_applause[party_from][party_to] /= seats_total[party_from]
    
    return dict_applause


def contains_laughter(comment):
    if 'Lachen' in comment['comment']:
        return True
    return False


def extract_laughing_party(comment):
    """
    Input argument is comment dict from comment_list. Comment is reduced to relevant part
    containing laughter. Function returns nested dict with indices [party_from][party_to]
    and value for number of laughter each; value is set according to number of participants
    and proportional to size of party.
    """
    global attendance_rate, percentage_participating
    dict_all = get_party_dict()

    party_found = False
    
    # split comment at hyphen in case of several action within one comment
    sub_actions = comment['comment'].split(' – ')
    
    for sub_action in sub_actions:
        if not 'Lachen' in sub_action:
            continue
        
        # this means 'Lachen' is not the action, but part of a call
        if ":" in sub_action:
            continue
            
        # search for party in sub_action
        for party in all_parties:
            count_single = sub_action.count(f'[{party}]')
            dict_all[party][comment['speaker']] += count_single
            count_multiple = sub_action.count(party)-count_single
            
            count_multiple *= int(max(seats_total[party]*attendance_rate*percentage_participating, 1))
            dict_all[party][comment['speaker']] += count_multiple
            
            if count_single > 0 or count_multiple > 0:
                party_found = True
        
        # check for "der LINKEN" and "des BÜNDNISSES..."
        if "der LINKEN" in sub_action:
            party_found = True
            dict_all["DIE LINKE"][comment['speaker']] += int(max(seats_total["DIE LINKE"]*attendance_rate*percentage_participating, 1))
        if "des BÜNDNISSES 90/DIE GRÜNEN" in sub_action:
            party_found = True
            dict_all["BÜNDNIS 90/DIE GRÜNEN"][comment['speaker']] += int(max(seats_total["BÜNDNIS 90/DIE GRÜNEN"]*attendance_rate*percentage_participating, 1))
        
        if not party_found:
            pass
            # print(f'Error: no party commenting could be found for comment: {sub_action}!')
        
    return dict_all


def get_data_matrix_laughter(comment_list, relative=False):
    """
    Returns nested dict with indices [party_from][party_to] containing number of laughter
    per party for currently speaking party for entire comment_list.
    """
    global initialize
    
    if not initialized:
        initialize(comment_list)

    comment_list_laughter = list(filter(contains_laughter, comment_list))
        
    dict_laughter = get_party_dict()
    
    for comment in comment_list_laughter:
        parties_laughing = extract_laughing_party(comment)
        for party_from in parties_laughing:
            for party_to in parties_laughing[party_from]:
                dict_laughter[party_from][party_to] += parties_laughing[party_from][party_to]
    
    if relative:
        for party_from in dict_laughter:
            for party_to in dict_laughter[party_from]:
                dict_laughter[party_from][party_to] /= seats_total[party_from]
    
    return dict_laughter


def contains_direct_calls(comment):
    if "Gegenruf" or "gewandt" in comment['comment']:
        return True
    return False

def extract_addressed_party(comment):
    """
    Input argument is comment dict from comment_list. Function returns nested dict 
    with indices [party_from][party_to] and value for number of direct comments each.
    """
    dict_all = get_party_dict()

    previous_callers = []
    party_addressed = None
    
    # split comment at hyphen in case of several action within one comment
    sub_actions = comment['comment'].split(' – ')
    
    for sub_action in sub_actions:
        
        is_single_caller = False
        is_relevant = False
        
        if ":" in sub_action:
            call_left = sub_action.split(':')[0]
            is_single_caller = True
            
            # case 1: "<speaker> [<party>], an ... gewandt" in given before quote
            if '],' in call_left:
                    call_from_to = call_left.split(',')
                    call_left = call_from_to[0]
                    directed_at = call_from_to[1]
                    if 'gewandt' in directed_at:
                        matching = [party for party in all_parties if party in directed_at]
                        if len(matching) != 1:
                            continue
                        party_addressed = matching[0]
                        is_relevant = True
                        
                        # TODO: check for gewandt, but no right side of call
            # case 2: "Gegenruf" refering to previous caller
            elif call_left.startswith("Gegenruf"):
                if len(previous_callers) == 0:
                    previous_callers.append(comment['speaker'])
                party_addressed = previous_callers[-1]
                is_relevant = True
            
            # case 3: consecutive "Gegenruf" refering to original caller
            elif call_left.startswith("Weiterer Gegenruf"):
                # more than 2 consecutive calls never occur
                party_addressed = previous_callers[-2]
                is_relevant = True
            
            sub_action = call_left
        else:
            if sub_action.startswith("Zurufe"):
                single_caller = [party for party in all_parties if party in sub_action]
                caller = None
                if len(single_caller) == 0:
                    if "der LINKEN" in sub_action:
                        caller = "DIE LINKE"
                    elif "des BÜNDNISSES 90/DIE GRÜNEN" in sub_action:
                        caller = "BÜNDNIS 90/DIE GRÜNEN"
                else:
                    caller = single_caller[0]
                if caller is not None:
                    previous_callers.append(caller)
            continue
        
        if party_addressed is None:
            party_addressed = comment['speaker']
            
        # extract previously commenting party first
        if len(sub_actions) > 1 and is_single_caller:
            single_caller = [party for party in all_parties if party in sub_action]
            caller = None
            if len(single_caller) == 0:
                if "der LINKEN" in sub_action:
                    caller = "DIE LINKE"
                elif "des BÜNDNISSES 90/DIE GRÜNEN" in sub_action:
                    caller = "BÜNDNIS 90/DIE GRÜNEN"
            else:
                caller = single_caller[0]
            if caller is not None:
                previous_callers.append(caller)
            else:
                continue
        
            if is_relevant:
                if caller == party_addressed:
                    pass
                    #print('from', caller, 'to', party_addressed, ':', comment['comment'], '\r\n')
                dict_all[caller][party_addressed] += 1
        
    return dict_all


def get_data_matrix_direct_calls(comment_list, relative=False):
    """
    Returns nested dict with indices [party_from][party_to] containing number of direct
    comments that address specific parties either by replying to a previous call or by 
    speaking to a party.
    """
    global initialized
    
    if not initialized:
        initialize(comment_list)
    
    comment_list_direct = list(filter(contains_direct_calls, comment_list))
    
    dict_direct_comments = get_party_dict()
    
    for comment in comment_list_direct:
        parties_addressed = extract_addressed_party(comment)
        for party_from in parties_addressed:
            for party_to in parties_addressed[party_from]:
                dict_direct_comments[party_from][party_to] += parties_addressed[party_from][party_to]
    
    if relative:
        for party_from in dict_direct_comments:
            for party_to in dict_direct_comments[party_from]:
                dict_direct_comments[party_from][party_to] /= seats_total[party_from]
                
    return dict_direct_comments


def initialize(comment_list):
    global initialized, seats_total, all_parties
    get_seats_total(19)
    all_parties = get_list_of_parties(comment_list)
    initialized = True


def load_data(renew_data):
    global path_comments
    if renew_data or not os.path.exists(path_comments):
        path_comments = get_data()
    comments = None
    with open(path_comments, 'r') as comment_file:
        comments = json.load(comment_file)
    if comments:
        comments = list(filter(has_valid_speaker, comments))
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


if __name__ == "__main__":
    pass
