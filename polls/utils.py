import string
import copy
import json
from random import sample
import random
from math import log2, modf,pow
from operator import itemgetter
from django.shortcuts import get_object_or_404

from polls.models_ import VotingScore, VotingPoll,\
    Candidate, UNDEFINED_VALUE, preference_model_from_text
from accounts.models import User

# simple functions ######################################################################


def days_months(candidates):
    months = []
    days = []
    for c in candidates:

        current_month = c.date.strftime("%B/%Y")
        current_day = c.date.strftime("%A/%d")
        if len(months) > 0 and months[-1]["label"].strftime("%B/%Y") == current_month:
            months[-1]["value"] += 1
        else:
            months += [{"label": c.date, "value": 1}]
        if len(days) > 0 and months[-1]["label"].strftime("%B/%Y") == current_month and days[-1]["label"].strftime("%A/%d") == current_day:
            days[-1]["value"] += 1
        else:
            days += [{"label": c.date, "value": 1}]
    return days, months


def voters_undefined(poll):
    voters = VotingScore.objects.values_list('voter', flat=True).filter(candidate__poll__id=poll.id).distinct()
    list_voters = []
    for i in voters:
        if i not in list_voters:
            list_voters.append(i)
    if voters:
        initial_candidates = VotingScore.objects.values_list('candidate', flat=True).filter(
            candidate__poll__id=poll.id).distinct()
        final_candidates = Candidate.objects.values_list('id', flat=True).filter(poll_id=poll.id)
        candidates_diff = list(set(final_candidates).difference(initial_candidates))

        for c in candidates_diff:
            c = get_object_or_404(Candidate, id=c)
            for voter in list_voters:
                voter = get_object_or_404(User, id=voter)
                VotingScore.objects.create(candidate=c, voter=voter, value=UNDEFINED_VALUE)

def dump_polls_as_json(filename='polls/static/polls/data.json'):
    """Dumps all the polls in JSON format.

    This function retrieves all the polls from the database
    and dumps them in JSON format in a file. This function
    is intended to be run periodically to provide a snapshot
    of the database.

    Keyword arguments:
    filename -- the file name in which it should be dumped (default: 'polls/data.json')"""
    polls = VotingPoll.objects.all()
    polls_dict = []
    for poll in polls:
        polls_dict.append(dict(poll.__iter__(anonymize=True)))

    with open(filename, 'w') as outfile:
        json.dump(polls_dict, outfile, indent=4, sort_keys=True)


def scoring_method(candidates,preference_model,votes,list_voters,scores):
    dict_cand1 = dict_candidates(candidates)
    order_votes = order_votes_matrix(list_voters, scores)
    pl = plurality_method(order_votes, dict_cand1)
    plurality = kmass2(pl)
    dict_cand = dict_candidates(candidates)
    veto = veto_method(order_votes, dict_cand)
    scores = {}
    for c in candidates:
        scores[c.id] = []
    for v in votes:
        scores[v["candidate__id"]].append(v["value"])

    approval = dict()

    approval["threshold"] = preference_model.values[2:]

    borda_scores = []

    for i, c in enumerate(candidates):
        sum_borda = 0

        for score in scores[c.id]:
            sum_borda = sum_borda + (score if score != UNDEFINED_VALUE else 0)
        borda_scores.append({"x": str(c), "y": sum_borda})

    borda_scores = kmass2(borda_scores)

    approval_scores = []
    curve_approval = []
    for y in approval["threshold"]:
        th = []
        for c in candidates:
            sum_approval = 0
            for score in scores[c.id]:
                sum_approval = sum_approval + (1 if score >= y else 0)
            th.append({"x": str(c), "y": sum_approval})
            curve_approval.append({"candidate": str(c), "x": preference_model.value2text(y), "y": sum_approval})

        approval_scores = kmass2(th)
    approval["threshold"] = preference_model.texts[2:]
    curve_approval.reverse()
    approval["scores"] = approval_scores

    return{"borda":borda_scores,"plurality":plurality,"veto":veto,"approval":approval,"curve_approval":curve_approval}


def order_votes_matrix(list_voters, scores):
    order_votes = []
    for v in list_voters:
        score = scores[str(v)]
        d = [{"id": x, "value": score[x]} for x in score if score[x] != UNDEFINED_VALUE]
        d = sorted(d, key=itemgetter('value'), reverse=True)
        order_votes.append(d)

    return order_votes


def dict_candidates(candidates):
    dict_cand = {}
    for c in candidates:
        dict_cand[str(c.id)] = {'x': str(c), 'y': 0}

    return dict_cand


def plurality_method(order_votes, dict_cand):
    for v in order_votes:
        if len(v) > 1:
            if v[0]["value"] != v[1]["value"]:
                dict_cand[v[0]["id"]]['y'] += 1
        else:
            dict_cand[v[0]["id"]]['y'] += 1

    return list(dict_cand.values())


def veto_method(order_votes, dict_cand):
    for v in order_votes:
        if len(v) > 1:
            if v[-1]["value"] != v[-2]["value"]:
                dict_cand[v[-1]["id"]]['y'] -= 1
        else:
            dict_cand[v[-1]["id"]]['y'] -= 1

    return list(dict_cand.values())


def randomized_method(candidates,scores,list_voters):

    candidates1 = [{"value": str(x.id),"group":1, "name": str(x), "parent": x.candidate} for x in candidates]
    len_cand = len(candidates)

    a, b = modf(log2(len_cand))
    if a != 0:
        n = len_cand - pow(2, b)
    else:
        n = len_cand / 2
    list1 = []
    while (n > 0):

        k = sample(candidates1, 2)
        cand1 = k[0]
        cand2 = k[1]
        round_randomized(scores, list_voters, cand1, cand2, list1)
        candidates1.remove(cand1)
        candidates1.remove(cand2)
        n = n - 1

    list_x1 = [{"name": x["name"], "value": x["value"],"group":1, "parent": "null", "children": [x]} for x in candidates1]

    list1.extend(list_x1)
    n = len(list1)

    j = log2(n)
    round = j + 1

    while (j > 0):
        list_round = []
        i = 0
        while (i < n):
            cand1 = list1[i]
            cand2 = list1[i + 1]
            round_randomized(scores, list_voters, cand1, cand2, list_round)
            i = i + 2
        n = len(list_round)
        list1 = list_round[:]
        j = j - 1

    color_group(list1[0],round+1)

    return {"list":list1,"round":round}


def color_group(root,n):
    if root["parent"]!=root["name"]:
        root["group"]=n

    if 'children' in root:
        for x in root["children"]:
            x["group"] = root["group"]
            color_group(x, n-1)


def round_randomized(scores,list_voters,cand1,cand2,*parameters):
    sum1 = 0
    sum2 = 0
    for v in list_voters:

        if scores[str(v)][cand1["value"]] > scores[str(v)][cand2["value"]]:
            sum1 = sum1 + 1
        elif scores[str(v)][cand1["value"]] < scores[str(v)][cand2["value"]]:
            sum2 = sum2 + 1
    if sum1 > sum2:
        parent = cand1
    else:
        parent = cand2

    cand1["parent"] = parent["name"]
    cand2["parent"] = parent["name"]
    cand1["diff"] = sum1
    cand2["diff"] = sum2

    parameters[0].append({"name": parent["name"],"value": parent["value"], "group":1,"parent": "null", "children": [cand1, cand2]})


def condorcet_method(list_voters,candidates,scores):

    nodes = [{'x':str(x),'y':0} for x in candidates]
    nodes1 = copy.deepcopy(nodes)

    n = len(candidates)

    Matrix = [[{"x":x,"y":y,"z":0} for x in range(n)] for y in range(n)]

    for v in list_voters:
        for i,c1 in enumerate(candidates):
            for j,c2 in enumerate(candidates):
                if c1.id!=c2.id:
                    if scores[str(v)][str(c1.id)] > scores[str(v)][str(c2.id)] :
                        Matrix[i][j]["z"]+=1

    for i, c in enumerate(candidates):
        list_value=[]
        list_value1=[]
        for j, x in enumerate(Matrix[i]):
            if i!=j:
                a=x["z"]
                b=Matrix[j][i]["z"]
                list_value.append(a)

                if a>b:
                    list_value1.append(1)
                if a==b:
                    list_value1.append(1/2)

        nodes[i]['y'] = sum(list_value1)
        nodes1[i]['y'] = min(list_value)
    links=compute_links(nodes,n)
    links1=compute_links(nodes1,n)
    nodes1 = kmass2(nodes1)

    return {"copeland":{"nodes":nodes,"links":links,"matrix":Matrix},"simpson":{"nodes":nodes1,"links":links1,"matrix":Matrix}}


def compute_links(nodes,n):
    i = 0
    links = []

    while (i < n - 1):
        j = i + 1
        while (j < n):
            a = nodes[i]["y"]
            b = nodes[j]["y"]
            link = {}

            link["y"] = abs(a - b)
            if a - b >= 0:
                link["source"] = i
                link["target"] = j

            if a - b < 0:
                link["source"] = j
                link["target"] = i

            links.append(link)

            j = j + 1
        i = i + 1
    return links


def runoff_compute(cand,list_cand, round1,order):
    letter = list(string.ascii_uppercase)
    n=len(cand)
    while n > 0:
        for h in round1:

            for c in cand:
                if c["id"] == h[0]["id"]:
                    c["plurality"] += 1
                j = [i for i, x in enumerate(h) if x["id"] == c["id"]]
                c["borda"] += n - 1 - j[0]
        cand = sorted(cand, key=itemgetter('plurality', 'borda'), reverse=True)
        list_cand.append(cand[:])

        last = cand[-1]["id"]
        order.append(last)

        for h in round1:
            for x in h:
                if x["id"] == last:
                    h.remove(x)

        cand.remove(cand[-1])
        cand = [{"id": x["id"], 'name': x["name"], 'letter': x["letter"], 'plurality': 0, 'borda': 0} for x in cand]
        n = len(cand)
    order.reverse()

#    for candi in list_cand:
#        for x in candi:
#            index =order.index(x['id'])
#            x['letter'] = letter[index]
    return list_cand




def runoff_method(candidates,list_voters,scores):
    letters = list(string.ascii_uppercase)

    round=[]

    for v in list_voters:
        score = scores[str(v)]
        d = [{"id": x, "value":score[x]} for x in score]
        d = sorted(d, key=itemgetter('value'), reverse=True)
        round.append(d)

    round1 = copy.deepcopy(round)
    cand = [{"id": str(c.id),  'name': str(c), 'letter': letters[i], 'plurality': 0, 'borda': 0} for i, c in enumerate(candidates)]
    stv = runoff_compute(cand, [], round,[])

    trm=[copy.deepcopy(stv[0])]
    n = len(trm[0])
    order1=[]
    for z in trm[0][2:n]:
        last = z["id"]
        order1.append(last)
        for h in round1:
            for x in h:
                if x["id"] == last:
                    h.remove(x)

    cand1 = [{"id": x["id"], 'name': x["name"], 'letter': x['letter'], 'plurality': 0, 'borda': 0} for x in trm[0][0:2]]
    order1.reverse()
    trm = runoff_compute(cand1,trm,round1,order1)

    stv_list = sorted(stv[0], key=itemgetter('letter'))
    trm_list = sorted(trm[0], key=itemgetter('letter'))


    return {"stv":stv,"stv_list": stv_list,"trm_list":trm_list,"trm":trm}

################# K MASS #######


def counting(cand_list, count):
    j = 0
    for _ in range(len(cand_list)):
        if count == cand_list[_]['y']:
            j += 1
    return j


# take a list of candidate and score
def kmass(candidates, list_voters, scores, votes):
    dict_cand1 = dict_candidates(candidates)
    order_votes = order_votes_matrix(list_voters, scores)
    plurality = plurality_method(order_votes, dict_cand1)
    kmp = []
    arr = sorted(plurality, key=itemgetter('y'), reverse=True)
    c = counting(arr, arr[0]['y'])
    while len(arr) > 0:
        kmp.append([arr.pop(0) for _ in range(c)])
        if len(arr) > 0:
            c = counting(arr, arr[0]['y'])

    scores = {}
    for c in candidates:
        scores[c.id] = []
    for v in votes:
        scores[v["candidate__id"]].append(v["value"])
    borda_scores = []
    for i, c in enumerate(candidates):
        sum_borda = 0

        for score in scores[c.id]:
            sum_borda = sum_borda + (score if score != UNDEFINED_VALUE else 0)
        borda_scores.append({"x": str(c), "y": sum_borda})

    kmb = []
    arr = sorted(borda_scores, key=itemgetter('y'), reverse=True)
    c2 = counting(arr, arr[0]['y'])
    while len(arr) > 0:
        kmb.append([arr.pop(0) for _ in range(c2)])
        if len(arr) > 0:
            c2 = counting(arr, arr[0]['y'])

    return {"borda": kmb, "plurality": kmp}

############### -WINNER-RANDOM- ##########


def vincitori(my_list, c: int = 1, shuffle: bool = False):
    n = 0
    vinc_ = []
    if shuffle:
        for x in range(len(my_list)):
            if c < len(my_list[x]):
                arr_c = my_list[x]
                while n < c:  #mettere un vincolo in caso di c = 0
                    a = random.choice(arr_c)
                    vinc_.append(a)
                    arr_c.remove(a)
                    n += 1
                break
            else:
                for y in range(len(my_list[x])):
                    vinc_.append(my_list[x][y])
                c -= len(my_list[x])
    if not shuffle:
        n = 0
        for x in my_list:
            for y in x:
                if n >= c:
                    break
                vinc_.append(y)
                n += 1

    return vinc_

def counting2(arr, count):
    c = 0
    for _ in range(len(arr)):
        if (count == arr[_]["y"]):
            c += 1
    return c


"""" create my k-max table """


def kmass2(arr):
    km = []
    arr = sorted(arr, key=itemgetter('y'), reverse=True)
    c = counting2(arr, arr[0]["y"])
    while len(arr) > 0:
        km.append([arr.pop(0) for _ in range(c)])
        if len(arr) > 0:
            c = counting(arr, arr[0]["y"])
    print(km)
    return km