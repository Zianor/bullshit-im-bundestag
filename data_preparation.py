from xml_parser import get_data
import json
import os.path

all_parties = set()
seats_total = {}
attendance_rate = 0.2
percentage_participating = 0.2
initialized = False
path_comments = ''


def get_seats_total(session_number):
    """
    Sets global dict seats_total for number of seats per party and total number
    of seats. Make sure the JSON file has the name: 'seats_totalYY.json'.
    Throws an exception if JSON for session_year does not exist. Returns
    seats_total after initialization.
    :param session_number: number of current session with the format YY
    """
    global seats_total
    file_name = f'data/seats_total{session_number}.json'
    if not os.path.exists(file_name):
        raise ValueError(f'No JSON input data for session year {session_number} found!')

    with open(file_name, encoding='utf-8') as seat_file:
        seats_total = json.load(seat_file)
    return seats_total


def get_list_of_parties(comment_list):
    """
    Extracts all parties from comment_list (list containing comment dictionaries)
    and returns set with alphabetically sorted names.
    :param comment_list: list of comment dictionaries
    """
    for comment in comment_list:
        all_parties.add(comment['speaker'])
    return sorted(all_parties)


def has_valid_speaker(comment):
    if comment['speaker'] == 'none':
        return False
    return True


def get_party_dict():
    """
    Returns nested dictionary with indices [party_from][party_to] for all parties
    with values set to 0.
    """
    global all_parties
    dict_all = {}
    for party_from in all_parties:
        dict_all[party_from] = {}
        for party_to in all_parties:
            dict_all[party_from][party_to] = 0
    return dict_all


def get_factor_multiple(party, is_single_caller):
    """
    Returns a weighting factor according to number of seats per party
    in case the comment has multiple participants/callers. Otherwise, 1 is returned.
    :param party: string with name of party involved
    :param is_single_caller: boolean to indicate whether comment is made by single person
    """
    factor_multiple = 1
    if not is_single_caller:
        factor_multiple = int(max(seats_total[party] * attendance_rate * percentage_participating, 1))
    return factor_multiple


def extract_commenting_party(comment, weighted):
    """
    Input argument is comment dict from comment_list. Comment is reduced to relevant part
    containing party. Function returns nested dict with indices [party_from][party_to]
    and value for number of actions each.
    :param weighted: boolean if multiple_caller should be weighted
    :param comment: comment dictionary from list of comments
    """
    global attendance_rate, percentage_participating
    dict_all = get_party_dict()

    party_found = False

    # split comment at hyphen in case of several actions within one comment
    sub_actions = comment['comment'].split(' – ')

    # track previous speakers in case parties address each other in calls
    previous_callers = []

    for sub_action in sub_actions:
        is_single_caller = False
        party_addressed = None
        is_no_comment = False
        caller_found = False

        # separate single speaker given on left side of ":" as in <name> [<party>]: <call>
        if ":" in sub_action:
            call_left = sub_action.split(':')[0]
            is_single_caller = True

            # deal with case if extra information is given after [<party>] (usually specifies who single commenter addresses)
            # example format of sub_action: Kai Gehring [BÜNDNIS 90/DIE GRÜNEN], an die AfD gewandt: <call>
            if '],' in call_left:
                call_from_to = call_left.split(',')
                call_left = call_from_to[0]

                # evaluate directed_at to determine if call is directed at party other than current speaker
                # in this case, the call replies to a call by another party
                directed_at = call_from_to[1]
                matching = [party for party in all_parties if party in directed_at]
                if len(matching) == 0:
                    continue
                if 'gewandt' in directed_at:
                    if len(matching) != 1:
                        # print(f'Error: tried to find single party in directed_at part of call, but failed: {comment["comment"]}')
                        continue
                    else:
                        party_addressed = matching[0]

            elif call_left.startswith("Gegenruf"):
                if len(previous_callers) == 0:
                    # call refers to actual speech, not the previous call because it's the first call
                    previous_callers.append(comment['speaker'])
                party_addressed = previous_callers[-1]

            elif call_left.startswith("Weiterer Gegenruf"):
                # a maximum of two calls referring to the same previous call are documented
                party_addressed = previous_callers[-2]

            elif call_left.startswith("Zurufe"):
                is_single_caller = False

            # cases left are those of single commenter without party, e.g. call_left: "Bettina Hagedorn, Parl. Staatssekretärin"

            # condense sub_action to relevant part containing caller
            sub_action = call_left

        # reply without content given
        elif sub_action.startswith("Gegenruf"):
            if len(previous_callers) == 0:
                previous_callers.append(comment['speaker'])
            party_addressed = previous_callers[-1]
            is_single_caller = True

        # calls without content or applause or something similar, can contain single and multiple participants
        else:
            if sub_action.startswith("Zurufe") or sub_action.startswith("Zuruf"):
                callers = [party for party in all_parties if party in sub_action]
                if len(callers) == 0:
                    if "der LINKEN" in sub_action:
                        callers.append("DIE LINKE")
                        caller_found = True
                    if "des BÜNDNISSES 90/DIE GRÜNEN" in sub_action:
                        callers.append("BÜNDNIS 90/DIE GRÜNEN")
                        caller_found = True
                if len(callers) > 0:
                    previous_callers.append(callers[0])
                    caller_found = True
                is_single_caller = sub_action.startswith("Zuruf ")
            else:
                is_no_comment = True

        # search for party in sub_action for tracking callers in case call is a direct comment
        if not is_no_comment \
                and ('Gegenruf' in comment['comment'] or "gewandt" in comment['comment']):
            callers = [party for party in all_parties if party in sub_action]
            if "der LINKEN" in sub_action:
                callers.append("DIE LINKE")
                caller_found = True
            if "des BÜNDNISSES 90/DIE GRÜNEN" in sub_action:
                callers.append("BÜNDNIS 90/DIE GRÜNEN")
                caller_found = True
            if len(callers) > 0:
                previous_callers.append(callers[0])
                caller_found = True
            if not caller_found:
                continue

        if party_addressed is None:
            party_addressed = comment['speaker']

        # create resulting dictionary
        for party in all_parties:
            count_single = sub_action.count(f'[{party}]')
            dict_all[party][party_addressed] += count_single
            count_multiple = sub_action.count(party) - count_single
            if weighted:
                count_multiple *= get_factor_multiple(party, is_single_caller)
            dict_all[party][party_addressed] += count_multiple

            if count_single > 0 or count_multiple > 0:
                party_found = True

        # check for "der LINKEN" and "des BÜNDNISSES..."
        if "der LINKEN" in sub_action:
            party_found = True
            if weighted:
                dict_all["DIE LINKE"][party_addressed] += get_factor_multiple("DIE LINKE", is_single_caller)
            else:
                dict_all["DIE LINKE"][party_addressed] += 1
        if "des BÜNDNISSES 90/DIE GRÜNEN" in sub_action:
            party_found = True
            if weighted:
                dict_all["BÜNDNIS 90/DIE GRÜNEN"][party_addressed] += get_factor_multiple("BÜNDNIS 90/DIE GRÜNEN",
                                                                                          is_single_caller)
            else:
                dict_all["BÜNDNIS 90/DIE GRÜNEN"][party_addressed] += 1

        # check for "ganzen Hause" or just "Beifall"; ignore "Heiterkeit" etc.
        if sub_action == "Beifall" or sub_action == "Beifall im ganzen Hause" \
                or sub_action == "Beifall bei Abgeordneten im ganzen Hause":
            party_found = True
            for party_from in dict_all:
                if weighted:
                    dict_all[party_from][party_addressed] += get_factor_multiple(party_from, is_single_caller)
                else:
                    dict_all[party_from][party_addressed] += 1

        if not party_found:
            pass
            # print(f'Error: no party commenting could be found for comment: {sub_action}!')

    return dict_all


def get_data_matrix_comments(comment_list, relative=False, weighted=True):
    """
    Returns nested dict for comment_list with indices [party_from][party_to] containing number
    of actions each. Sums up values per comment for entire comment_list.
    :param weighted: boolean if multiple_caller should be weighted
    :param comment_list: list of comment dictionaries
    :param relative: if true, value will be ratio of number of comments to number of seats
    """
    if not initialized:
        initialize(comment_list)

    dict_comments = get_party_dict()

    for comment in comment_list:
        parties_commenting = extract_commenting_party(comment, weighted)
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


def extract_applauding_party(comment, weighted):
    """
    Returns list of parties applauding in part of original comment containing "Beifall". 
    This does not take into account whether the party is given in brackets, e.g. whether there are single
    or multiple participants. Note that whenever there is a speaker change, the party next up applauds their 
    upcoming speaker, however, this applause is associated with the previously presenting party in this
    implementation.
    :param comment: comment dictionary, can still contain multiple actions
    :param weighted: boolean if multiple_caller should be weighted
    """
    global all_parties
    dict_all = get_party_dict()
    party_found = False

    sub_actions = comment['comment'].split(' – ')

    for sub_action in sub_actions:
        if 'Beifall' not in sub_action:
            continue

        for party in all_parties:
            count_single = sub_action.count(f'[{party}]')
            dict_all[party][comment['speaker']] += count_single
            count_multiple = sub_action.count(party) - count_single
            if weighted:
                count_multiple *= get_factor_multiple(party, False)
            dict_all[party][comment['speaker']] += count_multiple

            if count_single > 0 or count_multiple > 0:
                party_found = True

        # check for "der LINKEN" and "des BÜNDNISSES..."
        if "der LINKEN" in sub_action:
            party_found = True
            if weighted:
                dict_all["DIE LINKE"][comment['speaker']] += get_factor_multiple("DIE LINKE", False)
            else:
                dict_all["DIE LINKE"][comment['speaker']] += 1
        if "des BÜNDNISSES 90/DIE GRÜNEN" in sub_action:
            party_found = True
            if weighted:
                dict_all["BÜNDNIS 90/DIE GRÜNEN"][comment['speaker']] += get_factor_multiple("BÜNDNIS 90/DIE GRÜNEN",
                                                                                             False)
            else:
                dict_all["BÜNDNIS 90/DIE GRÜNEN"][comment['speaker']] += 1

        # check for "im ganzen Hause" or just "Beifall"
        if sub_action == "Beifall" or "Beifall im ganzen Hause" in sub_action or "Beifall bei Abgeordneten im ganzen Hause" in sub_action:
            party_found = True
            for party_from in all_parties:
                if weighted:
                    dict_all[party_from][comment['speaker']] += get_factor_multiple(party_from, False)
                else:
                    dict_all[party_from][comment['speaker']] += 1

        if not party_found:
            # print(f'Error: no party applauding could be found for comment: {sub_action}!')
            pass

    return dict_all


def get_data_matrix_applause(comment_list, relative=False, weighted=True):
    """
    Returns nested dict with indices [party_from][party_to] containing number of applause given
    each for entire comment_list.
    :param weighted: boolean if multiple_caller should be weighted
    :param comment_list: list of comment dictionaries
    :param relative: boolean to indicate whether values are sums or ratio of amount of applause to number of seats
    """
    global initialized

    if not initialized:
        initialize(comment_list)

    comment_list_applause = list(filter(contains_applause, comment_list))

    dict_applause = get_party_dict()

    for comment in comment_list_applause:
        parties_applauding = extract_applauding_party(comment, weighted)
        for party_from in parties_applauding:
            for party_to in parties_applauding[party_from]:
                dict_applause[party_from][party_to] += parties_applauding[party_from][party_to]

    if relative:
        for party_from in all_parties:
            for party_to in all_parties:
                dict_applause[party_from][party_to] /= seats_total[party_from]

    return dict_applause


def contains_laughter(comment):
    if 'Lachen' in comment['comment']:
        return True
    return False


def extract_laughing_party(comment, weighted):
    """
    Input argument is comment dict from comment_list. Comment is reduced to relevant part
    containing laughter. Function returns nested dict with indices [party_from][party_to]
    and value for number of laughter each; value is set according to number of participants
    and proportional to size of party.
    :param weighted: boolean if multiple_caller should be weighted
    :param comment: comment dictionary
    """
    global attendance_rate, percentage_participating
    dict_all = get_party_dict()

    party_found = False

    # split comment at hyphen in case of several action within one comment
    sub_actions = comment['comment'].split(' – ')

    for sub_action in sub_actions:
        if 'Lachen' not in sub_action:
            continue

        # this means 'Lachen' is not the action, but part of a call
        if ":" in sub_action:
            continue

        # search for party in sub_action
        for party in all_parties:
            count_single = sub_action.count(f'[{party}]')
            dict_all[party][comment['speaker']] += count_single
            count_multiple = sub_action.count(party) - count_single
            if weighted:
                count_multiple *= get_factor_multiple(party, False)
            dict_all[party][comment['speaker']] += count_multiple

            if count_single > 0 or count_multiple > 0:
                party_found = True

        # check for "der LINKEN" and "des BÜNDNISSES..."
        if "der LINKEN" in sub_action:
            party_found = True
            if weighted:
                dict_all["DIE LINKE"][comment['speaker']] += get_factor_multiple("DIE LINKE", False)
            else:
                dict_all["DIE LINKE"][comment['speaker']] += 1
        if "des BÜNDNISSES 90/DIE GRÜNEN" in sub_action:
            party_found = True
            if weighted:
                dict_all["BÜNDNIS 90/DIE GRÜNEN"][comment['speaker']] += get_factor_multiple("BÜNDNIS 90/DIE GRÜNEN",
                                                                                             False)
            else:
                dict_all["BÜNDNIS 90/DIE GRÜNEN"][comment['speaker']] += 1

        if not party_found:
            pass
            # print(f'Error: no party commenting could be found for comment: {sub_action}!')

    return dict_all


def get_data_matrix_laughter(comment_list, relative=False, weighted=True):
    """
    Returns nested dict with indices [party_from][party_to] containing number of laughter
    or ratio of number of laughter to number of seats for entire comment_list.
    :param comment_list: list of comment dictionaries
    :param relative: boolean to indicate whether to calculate relative numbers
    :param weighted: boolean if multiple_caller should be weighted
    """
    global initialized

    if not initialized:
        initialize(comment_list)

    comment_list_laughter = list(filter(contains_laughter, comment_list))

    dict_laughter = get_party_dict()

    for comment in comment_list_laughter:
        parties_laughing = extract_laughing_party(comment, weighted)
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
    :param comment: comment dictionary
    """
    dict_all = get_party_dict()

    previous_callers = []

    # split comment at hyphen in case of several action within one comment
    sub_actions = comment['comment'].split(' – ')

    for sub_action in sub_actions:

        caller_found = False
        is_relevant = False
        party_addressed = None
        is_no_comment = False

        if ":" in sub_action:
            call_left = sub_action.split(':')[0]

            # case 1: "<speaker> [<party>], an ... gewandt" is given before quote
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

        # reply without content given
        elif sub_action.startswith("Gegenruf"):
            if len(previous_callers) == 0:
                previous_callers.append(comment['speaker'])
            party_addressed = previous_callers[-1]
            is_relevant = True

        # call by single person or multiple people without content
        elif sub_action.startswith("Zurufe") or sub_action.startswith("Zuruf"):
            callers = [party for party in all_parties if party in sub_action]
            if len(callers) == 0:
                if "der LINKEN" in sub_action:
                    callers.append("DIE LINKE")
                    caller_found = True
                if "des BÜNDNISSES 90/DIE GRÜNEN" in sub_action:
                    callers.append("BÜNDNIS 90/DIE GRÜNEN")
                    caller_found = True
            if len(callers) > 0:
                caller_found = True
                # set first party listed as previous caller; there is just 1 caller in most cases
                previous_callers.append(callers[0])
        else:
            is_no_comment = True

        if party_addressed is None:
            party_addressed = comment['speaker']

        # extract previously commenting party first
        if not is_no_comment \
                and ("Gegenruf" in comment['comment'] or "gewandt" in comment['comment']):

            callers = [party for party in all_parties if party in sub_action]
            if "der LINKEN" in sub_action:
                callers.append("DIE LINKE")
                caller_found = True
            if "des BÜNDNISSES 90/DIE GRÜNEN" in sub_action:
                callers.append("BÜNDNIS 90/DIE GRÜNEN")
                caller_found = True
            if len(callers) > 0:
                # assuming the caller listed first is the most relevant one
                previous_callers.append(callers[0])
                caller_found = True

            if not caller_found:
                # print(f'Error: no caller could be found for {sub_action}!')
                continue

            if is_relevant:
                for caller in callers:
                    dict_all[caller][party_addressed] += 1

    return dict_all


def get_data_matrix_direct_calls(comment_list, relative=False):
    """
    Returns nested dict with indices [party_from][party_to] containing number of direct
    comments, that address specific parties either by replying to a previous call or by 
    speaking to a party, or ratio of number of direct comments to number of seats.
    :param comment_list: list of comment dictionaries
    :param relative: boolean to indicate whether to calculate relative numbers
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
    """
    Initialize global variables seats_total and all_parties for comment_list.
    :param comment_list: list of comment dictionaries
    """
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
        distribution_self_other[party_from]['self'] = sum_self / sum_all * 100
    return distribution_self_other


if __name__ == "__main__":
    pass
