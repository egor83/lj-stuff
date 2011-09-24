import urllib2
import datetime
import logging

from google.appengine.ext import db
from google.appengine.api.urlfetch import DownloadError


caching_period = datetime.timedelta(1) # caching for 1 day


def get_friends(username):
    # TODO - add error handling - eg empty/non existing username
    friends_query = FriendsList.gql("where username = :1", username)
    friends_entity = friends_query.get()

    if (friends_entity == None or
       datetime.datetime.now() - friends_entity.caching_date > caching_period):
        # no data cached yet or it's too old, fetch
        friends_data = fetch_friends(username, friends_entity)
    else:
        # TODO - is there a way to store lists of strings?
        # A: http://goo.gl/tuwmt

        # balance between short names, consistency and readability?
        # (eg friends_entity or fs_entity)
        logging.debug("Retrieved friends data for %s from DB", username)
        friends_data = friends_entity.raw_friends_data

    friends, friend_ofs = [], []
    for line in friends_data.splitlines():
        try:
            if line[0] == '>':
                friends.append(line[2:])
            elif line[0] == '<':
                friend_ofs.append(line[2:])
        except IndexError: # empty string
            pass

    return friends, friend_ofs


def fetch_friends(username, friends_entity):
    logging.info("Fetching friends data for %s from LJ", username)
    
    # TODO - constructing opener - move to __init__ ?
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Crawler, contact owner at '
                          'egor.ryabkov(at)gmail.com')]

    # TODO - use open + with as per http://goo.gl/QaWX4

    count = 0
    errorMsg = None
    while count < 3:
        try:
            friend_feed = 'http://www.livejournal.com/misc/fdata.bml?user='
##            raise DownloadError('testing') # testing
            flist = opener.open(friend_feed + username)
            break # TODO - looks ugly to me - any better way?
        except DownloadError, de:
            err_msg = ("A DownloadError (%s) has occurred "
                       "while fetching, repeating")
            logging.error(err_msg % de)
            errorMsg = de
            count += 1

    if count == 3:
        raise DownloadError(errorMsg)
    
    friends_all = flist.read()

    # store in DB
    if friends_entity == None:
        friends_entity = FriendsList()
        friends_entity.username = username

    friends_entity.caching_date = datetime.datetime.now()
    friends_entity.raw_friends_data = friends_all
    friends_entity.put()
    
    return friends_all


def find_common(list1, list2):
    res_list = []
    for item in list1:
        if item in list2:
            res_list.append(item)

    return res_list


class FriendsList(db.Model):
    username = db.StringProperty()
    caching_date = db.DateTimeProperty()
    # TODO - will change to list/array of strings, see above
    raw_friends_data = db.TextProperty()
