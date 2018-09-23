#!/usr/bin/python
"""
Calculate newly created defensive statistics

INPUTDATA (logindata.ini) is a local file that controls what happens here.

In the DEFAULT section of INPUTDATA, the following must be defined:
    username -- a valid LL name
    password -- the LL password corresponding to username
The following are optional:
    people -- a list of people to be analyzed if get_folks is called
    loginfile -- URL to LL login page, defaults to LOGINFILE
    verbose -- Boolean value, defaults to False.  If True, information about
               every match causing a change in defense stats will be printed.
"""
import configparser
import datetime
from html.parser import HTMLParser
import requests

LLHEADER = 'https://www.learnedleague.com'
LOGINFILE = LLHEADER + '/ucp.php?mode=login'
USER_DATA = LLHEADER + '/profiles/previous.php?%s'
ARUNDLE = LLHEADER + '/standings.php?%d&A_%s'
START_SEASON = 52
START_YEAR = 2011
INPUTDATA = 'logindata.ini'


def get_session(inifile):
    """
    Read an ini file, establish a login session

    Input:
        inifile -- name of local ini file with control information

    Returns:
        ses1 -- logged in requests session to be used in later operations
        verbose -- If True, individual match differences will be displayed
    """
    config = configparser.ConfigParser()
    config.read(inifile)
    payload = {'login': 'Login'}
    for attrib in ['username', 'password']:
        payload[attrib] = config['DEFAULT'][attrib]
    ses1 = requests.Session()
    try:
        loginfile = config['DEFAULT']['loginfile']
    except KeyError:
        loginfile = LOGINFILE
    ses1.post(loginfile, data=payload)
    try:
        verbosity = bool(config['DEFAULT']['verbose'])
    except KeyError:
        verbosity = False
    return ses1, verbosity


class ScoresParse(HTMLParser):
    """
    Parse the Url with a person's LL results
    """
    def __init__(self):
        HTMLParser.__init__(self)
        self.result = {}
        self.newkey = ''
        self.text_next = False

    def handle_starttag(self, tag, attrs):
        """
        Find new matches and new score values
        """
        if tag == 'a':
            for apt in attrs:
                if apt[0] == 'href':
                    if apt[1].startswith('/match.php?'):
                        locv = apt[1].split('?')[1]
                        if locv.startswith('id='):
                            self.text_next = True
                        else:
                            self.newkey = locv

    def handle_data(self, data):
        """
        Grab the score fields out of the data
        """
        if self.text_next:
            self.result[self.newkey] = data
            self.text_next = False


class ScoresObj(object):
    """
    Hold the information in a match score in internal values
    """
    def __init__(self, instr):
        """
        Parse a match score, 9(5)-4(4) for instance, into local variables

        Input:
            instr -- text representation of match score
        """
        locstr = instr.replace(')', '')
        locstr = locstr.replace('(', ' ')
        locstr = locstr.replace('-', ' ')
        locstr = locstr.replace('F', '-1')
        locnums = locstr.split(' ')
        self.my_score = int(locnums[0])
        self.my_qs = int(locnums[1])
        self.opp_score = int(locnums[2])
        self.opp_qs = int(locnums[3])

    def get_my_scores(self):
        """
        Return my score (adjusted and raw questions)
        """
        return self.my_score, self.my_qs

    def get_opp_scores(self):
        """
        Return opponents score (adjusted and raw questions)
        """
        return self.opp_score, self.opp_qs


def massage_data(input_dict):
    """
    Convert raw url fields into integer values in a dictionary

    Input:
        dictionary containing values like '1&4' and '9(5)-4(4)'

    Output:
        similar dictionary with integer values stored
    """
    out_dict = {}
    for keyv in input_dict.keys():
        parts = keyv.split('&')
        rkey = int(parts[0])
        if rkey not in out_dict:
            out_dict[rkey] = {}
        value = int(parts[1])
        out_dict[rkey][value] = ScoresObj(input_dict[keyv])
    return out_dict


def get_scores_for(user, session):
    """
    Get a person's raw webpage data and format into results

    Input:
        user -- user name
        sessions -- requests session identifier passed around through this
                    program

    Returns results -- an integer formatted dictionary of a player's game
                       results
    """
    ses_data = session.get(USER_DATA % user)
    parser = ScoresParse()
    parser.feed(ses_data.text)
    return massage_data(parser.result)


def analyze_results(results, lkey, verbose):
    """
    Run through the results of checking  a season, and compute defensive values

    Input:
        results -- dictionary of a persons results scraped from a page.
        lkey -- season that we are checking
        verbose -- if True, print result when a difference is found for a match

    Results are printed out
    """
    plusminus = 0
    absdiff = 0
    msg = ['loss', 'tie', 'win']
    diffy = lambda a: (a > 0) - (a < 0)
    for gkey in results[lkey]:
        game = results[lkey][gkey]
        if game.my_qs < 0 or game.opp_qs < 0:
            continue
        qval = diffy(game.my_qs - game.opp_qs) + 1
        sval = diffy(game.my_score - game.opp_score) + 1
        if qval == sval:
            continue
        plusminus += (sval - qval)
        absdiff += abs(sval - qval)
        if verbose:
            print('game %d turned a %s into a %s' % gkey, msg[qval], msg[sval])
    return plusminus, absdiff


def make_measurement(player, ses1, verbosity, spl):
    """
    Give an LL player, print that player's defense indicators for each season

    Input:
        player -- player name on LL
        ses1 -- requests session used after signing on
        verbosity -- if True, print results of every game where defense
                     mattered
        spl -- number >= seasons played since LL 52
    """
    result = get_scores_for(player, ses1)
    for league in range(START_SEASON, START_SEASON+spl):
        if league not in result:
            continue
        print("League: %d" % league)
        answer, absdiff = analyze_results(result, league, verbosity)
        print("net gain or loss, total effect: %d, %d" % (answer, absdiff))


def get_folks(inifile):
    """
    For each individual listed in the ini file, measure their defensive
    ratings.

    Input:
        inifile -- ini file with individual names
    """
    ses1, verbosity = get_session(INPUTDATA)
    now = datetime.datetime.now()
    spl = (now.year - START_YEAR) * 4
    config = configparser.ConfigParser()
    config.read(inifile)
    plist = config['DEFAULT']['people'].split(',')
    for name in plist:
        oname = name.strip()
        print ('\nRESULTS FOR %s\n' % oname)
        make_measurement(oname, ses1, verbosity, spl)


class ArundleParse(HTMLParser):
    """
    Parse an A rundle page looking for links to all other rundles
    in the division
    """
    def __init__(self, division):
        HTMLParser.__init__(self)
        self.division = division
        self.result = []

    def handle_starttag(self, tag, attrs):
        """
        Find href rundle links
        """
        if tag == 'a':
            for apt in attrs:
                if apt[0] == 'href':
                    if apt[1].startswith('/standings.php?'):
                        if self.division in apt[1]:
                            self.result.append(apt[1])


def get_rundles(ses1, season, division):
    """
    Find all the rundles in a division

    Input:
        ses1 -- requests session
        season -- LL season number (78 for example)
        division -- division name ("Pacific for example")

    Returns: list of links to all the rundles in a division
    """
    rundle_data = ses1.get(ARUNDLE % (season, division))
    parser = ArundleParse(division)
    parser.feed(rundle_data.text)
    return parser.result


class PeepParse(HTMLParser):
    """
    Parse a rundle page looking for all players
    """
    def __init__(self):
        HTMLParser.__init__(self)
        self.result = []

    def handle_starttag(self, tag, attrs):
        """
        Find td class information with people's names
        """
        if tag == 'td':
            for apt in attrs:
                if apt[0] == 'class':
                    parts = apt[1].split()
                    if parts[-1] == 'std-mid':
                        name = parts[-2]
                        if name not in self.result:
                            self.result.append(name)


def find_best_def(season, division):
    """
    Find the best defensive results for a season.

    Input:
        season -- league season number (LL 78 ended on September 24, 2018)
        division -- Division or league name (Pacific for example)

    Print the best defenders and their ratings.
    """
    ses1, verbose = get_session(INPUTDATA)
    rundles = get_rundles(ses1, season, division)
    big_list = []
    for rundle in rundles:
        peep_data = ses1.get(LLHEADER+rundle)
        parser = PeepParse()
        parser.feed(peep_data.text)
        big_list = big_list + parser.result
    if verbose:
        print(big_list)
    best_def = 0
    best_list = []
    for name in big_list:
        tresult = get_scores_for(name, ses1)
        answer, absdiff = analyze_results(tresult, season, False)
        if verbose:
            print("%s net gain or loss, total effect: %d, %d" %
                  (name, answer, absdiff))
        if answer == best_def:
            best_list.append(name)
        if answer > best_def:
            best_def = answer
            best_list = [name]
    print("The highest defensive rating is: %d" % best_def)
    print("    set by: %s" % ", ".join(best_list))


if __name__ == "__main__":
    find_best_def(78, 'Pacific')
