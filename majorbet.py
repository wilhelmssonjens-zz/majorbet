from flask import Flask
from flask_table import Table, Col
import json
import urllib.request
import operator
import time
from flask_table.html import element

app = Flask(__name__)



def get_leaderboard():
    url1 = "http://www.pgatour.com/data/r/034/2017/leaderboard-v2.json?ts=1498381167707"
    with urllib.request.urlopen(url1) as url:
        data = json.loads(url.read().decode())
    return data['leaderboard']['players']


def get_bet_total(player_dict, name):
    totals = [player_dict[name[0]], player_dict[name[1]], player_dict[name[2]], player_dict[name[3]],
              player_dict[name[4]]]
    totals_2 = list()
    for val in totals:
        if val is None:
            totals_2.append(0)
        else:
            totals_2.append(val)
    totals_sorted_and_summed = sum(sorted(totals_2)[0:3])
    return totals_sorted_and_summed


def get_total_scores(leaderboard):
    player_dict = dict()
    for player in leaderboard:
        temp_name = player['player_bio']['first_name'] + " " + player['player_bio']['last_name']
        player_dict[temp_name] = player['total']
    return player_dict


def get_round_scores(leaderboard):
    player_dict = dict()
    for player in leaderboard:
        temp_name = player['player_bio']['first_name'] + " " + player['player_bio']['last_name']
        player_dict[temp_name] = player['today']
    return player_dict


def get_player_team(name):
    players = {"Jens Wilhelmsson": ['Jonas Blixt', 'Jonas Blixt', 'Jonas Blixt', 'Jonas Blixt', 'Jonas Blixt'],
               "Alexander Gustafsson": ['Brett Drewitt', 'Brett Drewitt', 'Brett Drewitt', 'David Hearn', 'Jonas Blixt'],
               "Malin Wallhede": ['Jonas Blixt', 'Jordan Spieth', 'Daniel Berger', 'Charley Hoffman','Danny Lee']}
    return players[name]


def players_playing(player_dict, name):
    count = 0
    on_course = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]
    for player in name:
        if player in on_course:
            count = count + 1
    return str(count)+"/6"


def get_current_holes(leaderboard):
    player_dict = dict()
    for player in leaderboard:
        temp_name = player['player_bio']['first_name'] + " " + player['player_bio']['last_name']
        player_dict[temp_name] = player['thru']
    return player_dict


def prettify_team_names(players):
    return players[0] + ', ' + players[1] + ', ' + players[2] + ', ' + players[3] + ', ' + players[4]


@app.route('/')
def display():
    PGA_data = get_leaderboard()
    all_players_totals = get_total_scores(PGA_data)
    all_players_round = get_round_scores(PGA_data)
    all_players_current_hole = get_current_holes(PGA_data)


    majorbet_leaderboard = {"Jens Wilhelmsson": get_bet_total(all_players_totals,get_player_team("Jens Wilhelmsson")),
                           "Alexander Gustafsson": get_bet_total(all_players_totals, get_player_team("Alexander Gustafsson")),
                            "Malin Wallhede": get_bet_total(all_players_totals, get_player_team("Malin Wallhede"))}

    majorbet_leaderboard_sorted = {key: value for (key, value) in sorted(majorbet_leaderboard.items(), key=operator.itemgetter(1))}

    round_scores = {key: get_bet_total(all_players_round, get_player_team(key)) for (key, value) in sorted(majorbet_leaderboard.items(), key=operator.itemgetter(1))}

    players_in_play = {key: players_playing(all_players_current_hole, get_player_team(key)) for (key, value) in sorted(majorbet_leaderboard.items(), key=operator.itemgetter(1))}

    items = [Item(idx+1,
                  name,
                  majorbet_leaderboard_sorted[name],
                  round_scores[name],
                  players_in_play[name],
                  prettify_team_names(get_player_team(name))) for idx,name in enumerate(majorbet_leaderboard_sorted)]

    table = ItemTable(items,html_attrs={"bgcolor":"#6599FF","style":"font-family: calibri; color: white; padding: 0px 15px 15px 15px"})

    header_and_background = "<head> <title>Majorbet Leaderboard</title> " \
                  "</head><body style=\"background-color:#6599FF;\">" \
                  "<h1 style=\"font-size: 40pt; padding: 30px 15px 0px 15px;text-align:left;font-family: calibri;color:white\">" \
                  "Majorbet Leaderboard</h1>"

    output_html =  header_and_background + table.__html__() + "</body>"
    return output_html


class Col2(Col):
    def td(self, item, attr):
        content = self.td_contents(item, self.get_attr_list(attr))
        if attr == "total":
            if item.total > 0:
                over_par = {"bgcolor": "#0047b3", "style": 'text-align:center; font-size: 16pt; font-family: calibri; border-radius: 6px'}
                return element(
                    'td',
                    content="+"+str(content),
                    escape_content=False,
                    attrs=over_par)
            elif item.total < 0:
                under_par = {"bgcolor":"#FF0000","style":'text-align:center; font-size: 16pt; font-family: calibri; border-radius: 6px'}
                return element(
                    'td',
                    content=content,
                    escape_content=False,
                    attrs=under_par)
            elif item.total == 0:
                on_par = {"bgcolor":"#d3d3d3","style":'text-align:center; font-size: 16pt; font-family: calibri; border-radius: 6px'}
                return element(
                    'td',
                    content=content,
                    escape_content=False,
                    attrs=on_par)
        elif attr == "round":
            if item.round > 0:
                over_par = {"bgcolor": "#0000FF", "style": 'text-align:center; font-size: 16pt; font-family: calibri'}
                return element(
                    'td',
                    content="+"+str(content),
                    escape_content=False,
                    attrs=over_par)

            elif item.round < 0:
                under_par = {"bgcolor":"#FF0000","style":'text-align:center; font-size: 16pt; font-family: calibri'}
                return element(
                    'td',
                    content=content,
                    escape_content=False,
                    attrs=under_par)

            elif item.round == 0:
                on_par = {"bgcolor":"#d3d3d3","style":'text-align:center; font-size: 16pt; font-family: calibri'}
                return element(
                    'td',
                    content=content,
                    escape_content=False,
                    attrs=on_par)
        else:
            return element(
                'td',
                content=content,
                escape_content=False,
                attrs=self.td_html_attrs)


# Declare your table
class ItemTable(Table):
    pos = Col2('Pos',th_html_attrs={"style":'font-size: 23pt'},td_html_attrs={"style":'text-align:center;font-size: 16pt; color: black; border-radius: 6px','bgcolor':"#FFDE00"})
    name = Col2('Name',th_html_attrs={"style":'font-size: 23pt; padding: 0px 15px 0px 15px'},td_html_attrs={"style":'font-size: 16pt; padding: 0px 15px 0px 15px'})
    total = Col2('Total',td_html_attrs={"style":'text-align:center;font-size: 16pt'},th_html_attrs={"style":'font-size: 23pt'})
    round = Col('Today',td_html_attrs={"style":'text-align:center;font-size: 16pt'},th_html_attrs={"style":'font-size: 23pt; padding: 0px 15px 0px 15px'})
    in_play = Col2('Active players',th_html_attrs={"style":'font-size: 23pt; padding: 0px 15px 0px 0px'},td_html_attrs={"style":'text-align:center;font-size: 16pt'})
    team = Col2('Players',th_html_attrs={"style":'text-align:center;font-size: 23pt'},td_html_attrs={"style":'text-align:center;font-size: 16pt'})

# Get some objects
class Item(object):
    def __init__(self, pos, name, total, round, in_play, team):
        self.pos = pos
        self.name = name
        self.total = total
        self.round = round
        self.in_play = in_play
        self.team = team


if __name__=='__main__':
    app.run(host="0.0.0.0")