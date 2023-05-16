import re
import pandas as pd
import logging

FORMAT = "[%(filename)s: - %(funcName)20s() ] %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)


class PublicInfo:

    def __init__(self, rebs, cot, nea, loc, flavour_dict, rebs_df):
        self.rebs = rebs
        self.cot = cot
        self.nea = nea
        self.loc = loc
        self.flavour_dict = flavour_dict
        self.rebs_df = rebs_df

    def get_rebs(self):
        return self.rebs

    def get_cot(self):
        return self.cot

    def get_nea(self):
        return self.nea

    def get_loc(self):
        return self.loc

    def get_flavour_dict(self):
        return self.flavour_dict

    # Pandas dataframe of rebs, rather than dict
    def get_rebs_df(self):
        return self.rebs_df 

class TruthInfo:

    def __init__(self, stars, moves, messages, ships, rebels):
        self.stars = stars
        self.moves = moves
        self.messages = messages
        self.ships = ships
        self.rebels = rebels

    def get_stars(self):
        return self.stars

    def get_moves(self):
        return self.moves

    def get_messages(self):
        return self.messages

    def get_max_time(self):
        return self.moves['t'].max()

    def get_ships(self):
        return self.ships

    def get_rebels(self):
        return self.rebels


def parse_public(line):
    logging.debug(line.strip())
    match = re.match(r't=(\d+), (\w+), (\w+), (.*)', line)
    #
    t = int(match.group(1))
    flavour = str(match.group(2))
    name = str(match.group(3))
    msg = str(match.group(4))

    return t, flavour, name, msg


def parse_answer(line):
    logging.debug(line.strip())
    match = re.match(r'(\S+) (\S+) (\S+) (\S+) (\S+) (\S+)', line)
    t = int(match.group(1))
    name = str(match.group(2))
    x = float(match.group(3))
    y = float(match.group(4))
    z = float(match.group(5))
    unc = float(match.group(6))

    return t, name, x, y, z, unc


def parse_starsystem(line):
    logging.debug(line.strip())
    match = re.match(r'StarSystem{loc=\((\d+.\d+), (\d+.\d+), (\d+.\d+)\), nNeigh=(\d+), name=\'(\w+)\'}', line)
    #
    x = float(match.group(1))
    y = float(match.group(2))
    z = float(match.group(3))
    neigh = int(match.group(4))
    star_id = str(match.group(5))

    return x, y, z, neigh, star_id


def parse_rebel(line):
    logging.debug(line.strip())
    match = re.match(r'RebelID_\d+, (\w+)\s+, \w+\s+, (\w+_\d+)', line)
    name = str(match.group(1))
    ship = str(match.group(2))
    return name, ship


def parse_msg(line):
    logging.debug(line.strip())
    match = re.match(r'MSG (\d+) (\w+)\((\w+)\) (\w+) loc=\((\d+.\d+), (\d+.\d+), (\d+.\d+)\) MSG\((\w+)\)', line)
    #
    t = int(match.group(1))
    reb_id = match.group(2)
    name = match.group(3)
    shipid = match.group(4)
    x = float(match.group(5))
    y = float(match.group(6))
    z = float(match.group(7))
    msg = match.group(8)

    return t, reb_id, name, shipid, x, y, z, msg


def parse_movement(line):
    logging.debug(line.strip())
    match = re.match(r'MOVE (\d+) (\w+) \((\d+.\d+), (\d+.\d+), (\d+.\d+)\) (\w+)', line)
    t = int(match.group(1))
    ship_id = match.group(2)
    x = float(match.group(3))
    y = float(match.group(4))
    z = float(match.group(5))
    at_dest = match.group(6)

    return t, x, y, z, ship_id, at_dest


def parse_public_data(path="../out/0001_public.txt"):
    logging.info(" ... Parsing public data!")
    
    p_log = open(path, 'r')

    # Dictionary for all rebel names in public log, and their message types
    rebels = {}

    # Dict for COT messages
    cot = {'messenger': [], 't': [], 'cotraveller': []}
    # Dict for NEA messages
    nea = {'messenger': [], 't': [], 'closestStar': []}
    # Dict for LOC messages
    loc = {'messenger': [], 't': [], 'x': [], 'y': [], 'z': []}

    for line in p_log.readlines():
        t, flavour, name, msg = parse_public(line)
        logging.debug('%d %s %s %s' % (t, flavour, name, msg))
        if name not in rebels:
            rebels[name] = flavour
        if 'COT' == flavour:
            cot['messenger'].append(name)
            cot['t'].append(t)
            cot['cotraveller'].append(msg)
        elif 'NEA' == flavour:
            nea['messenger'].append(name)
            nea['t'].append(t)
            nea['closestStar'].append(msg)
        elif 'LOC' == flavour:
            loc['messenger'].append(name)
            loc['t'].append(t)
            match = re.match(r'\((\d+.\d+), (\d+.\d+), (\d+.\d+)\)', msg)
            loc['x'].append(float(match.group(1)))
            loc['y'].append(float(match.group(2)))
            loc['z'].append(float(match.group(3)))

    df_cot = pd.DataFrame(data=cot)
    df_nea = pd.DataFrame(data=nea)
    df_loc = pd.DataFrame(data=loc)

    # Do some probably overcomplicated crap to get per rebel DF
    mapper = {"COT": df_cot, "NEA": df_nea, "LOC": df_loc}
    dict_rebs = {}
    for rebelName in rebels:
        logging.debug(rebelName)
        dict_rebs[rebelName] = mapper[rebels[rebelName]].loc[(mapper[rebels[rebelName]]['messenger'] == rebelName)]

    if len(rebels) != len(dict_rebs):
        logging.fatal('I made a bug >:(')
        exit(-1)

    # simpler way to return rebel pandas dataframe
    rebs_df = pd.read_csv(path, # '../data/0001_public.txt'
                    header=None, engine='python',
                    sep='t=(\d+), (\w+), (\w+), (.*)').dropna(how='all', axis=1) # stolen from above, alternative: r"t=(\d+),\s*([^,]+),\s*([^,]+),\s*(.+)"
    rebs_df.columns=['t', 'msg_type', 'messenger', 'msg_content']
    rebs_df.reset_index(drop=True)

    ## make time-series for predicting observations at 1-1000 time points
    rebs_df = rebs_df.set_index('t')\
                .groupby('messenger')\
                .apply(lambda df_x: df_x.reindex(range(1, 1000+1)))\
                .drop('messenger', axis=1).reset_index()

    ## add sample number and unique rebel ID
    match = re.search(r"/(\d{4})[^/]*\.txt$", path)
    sample_no = int(match.group(1))
    rebs_df['sample'] = '{:04d}'.format(sample_no)
    rebs_df['ID'] = rebs_df['messenger'] + '_{:04d}'.format(sample_no) # unique across samples


    logging.info(" ... Done parsing public!")
    logging.debug('Found %d rebels!' % len(dict_rebs))

    info = PublicInfo(dict_rebs, df_cot, df_nea, df_loc, rebels, rebs_df) # rebels contains dict_rebs?

    return info


def parse_truth_data(path="../out/1_truth.txt"):
    logging.info(" ... Parsing truth data!")

    f_log = open(path, 'r')

    # Dict for the star locations
    stars = {'x': [], 'y': [], 'z': [], 'nNeigh': [], 'id': []}
    # Dict for the ship movements
    moves = {'t': [], 'x': [], 'y': [], 'z': [], 'id': [], 'at_dest': []}
    # Dict for truth messages
    messages = {'t': [], 'id': [], 'name': [], 'x': [], 'y': [], 'z': [], 'msg': [], 'shipid': []}
    # Dict for relationship between ships and passengers
    ships = {}
    rebels = {}

    # Read through the log and then divy up the line based on what is happening
    counter = 0
    for line in f_log.readlines():
        counter += 1
        if counter > 200:
            # break
            pass

        if line.startswith('StarSystem'):
            x, y, z, num_neigh, star_id = parse_starsystem(line)
            logging.debug("SS: (%f, %f, %f) %s" % (x, y, z, star_id))
            stars['x'].append(x)
            stars['y'].append(y)
            stars['z'].append(z)
            stars['nNeigh'].append(num_neigh)
            stars['id'].append(star_id)

        elif line.startswith('MOVE'):
            t, x, y, z, ship_id, at_dest = parse_movement(line)
            logging.debug("MOVE: %d (%f, %f, %f) %s %s" % (t, x, y, z, ship_id, at_dest))
            moves['t'].append(t)
            moves['x'].append(x)
            moves['y'].append(y)
            moves['z'].append(z)
            moves['id'].append(ship_id)
            moves['at_dest'].append(at_dest)

        elif line.startswith("MSG"):
            t, reb_id, name, shipid, x, y, z, msg = parse_msg(line)
            logging.debug("MSG: %d %s %s %s (%f, %f, %f) %s" % (t, reb_id, name, shipid, x, y, z, msg))
            messages['t'].append(t)
            messages['x'].append(x)
            messages['y'].append(y)
            messages['z'].append(z)
            messages['id'].append(reb_id)
            messages['shipid'].append(shipid)
            messages['name'].append(name)
            messages['msg'].append(msg)

        elif line.startswith("RebelID_"):
            name, ship = parse_rebel(line)
            logging.debug('%s %s' % (name, ship))
            if ship not in ships:
                ships[ship] = []
            if name not in rebels:
                rebels[name] = ship
            else:
                logging.fatal("this shouldn't happen...")
                exit(-1)
            ships[ship].append(name)

    df_stars = pd.DataFrame(data=stars)
    df_moves = pd.DataFrame(data=moves)
    df_msgs = pd.DataFrame(data=messages)

    logging.debug(ships)
    logging.debug(rebels)
    logging.info(" ... Done parsing truth!")

    truth = TruthInfo(df_stars, df_moves, df_msgs, ships, rebels)

    return truth


def make_dummy_answer(path_truth="../out/0001_truth.txt", path_out="../out/sample_answer.txt"):
    logging.info('Reading from %s' % path_truth)
    logging.info('Writing to %s' % path_out)

    truth = parse_truth_data(path_truth)

    logging.info('Max time: %d' % truth.get_max_time())
    logging.info('Number of ships: %d' % len(truth.get_ships()))

    f_out = open(path_out, 'w')

    # Go ship by ship and add answer for each passenger
    ships = truth.get_ships()
    moves = truth.get_moves()
    uncertainty = 100
    # I have the feeling this is not smart...
    for row in moves.iterrows():
        x = row[1]['x']
        y = row[1]['y']
        z = row[1]['z']
        t = row[1]['t']
        ship = row[1]['id']
        for rebel in ships[ship]:
            f_out.write('%d %s %f %f %f %f\n' % (t, rebel, x, y, z, uncertainty))

    f_out.close()


# TODO: Make ... better ... and faster ...
def grade_assignment(path_truth="../out/0001_truth.txt", path_answer="../out/sample_answer.txt"):
    from scipy.stats import multivariate_normal
    import numpy as np

    logging.info(" ... Grading your assignment!")

    # I'm doing this via brute force... :(
    answer = open(path_answer, 'r')

    scores = {}
    overall_score = 0.0
    truth = parse_truth_data(path_truth)

    rebel_to_ship_dict = truth.get_rebels()
    movements = truth.get_moves()

    for line in answer.readlines():
        t, name, x, y, z, uncertainty = parse_answer(line)
        logging.debug('Parsed as: %d %s %f %f %f %f' % (t, name, x, y, z, uncertainty))

        # Analytic function
        mu = np.array([x, y, z])
        sigma = np.array([uncertainty, uncertainty, uncertainty])
        covariance = np.diag(sigma)**2

        # look up real location
        logging.debug(rebel_to_ship_dict[name])
        real_location = movements.loc[movements['t'] == t].loc[movements['id'] == rebel_to_ship_dict[name]]
        real_x = real_location['x'].values[0]
        real_y = real_location['y'].values[0]
        real_z = real_location['z'].values[0]
        logging.debug('%f %f %f' % (real_x, real_y, real_z))

        xyz = np.column_stack([real_x, real_y, real_z])
        z = multivariate_normal.pdf(xyz, mean=mu, cov=covariance)
        logging.debug(z)
        z = 1000*z  # little fudge factor...

        # Add the normalized score
        if name not in scores:
            scores[name] = 0.0
        scores[name] += z
        overall_score += z

    overall_score = overall_score/len(rebel_to_ship_dict)
    logging.info(' ... Done grading!')

    print('SCORE BY INDIVIDUAL REBEL: \n##########################')
    for rebel in scores:
        print('%s: %f' % (rebel, scores[rebel]))
    print('##########################\nOVERALL SCORE: %f' % overall_score)


if __name__ == '__main__':
    grade_assignment()
