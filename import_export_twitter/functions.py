# import_export_twitter/functions.py
# Brought to you by We Vote. Be good.
# -*- coding: UTF-8 -*-

from config.base import get_environment_variable
from exception.models import handle_exception
import tweepy
import wevote_functions.admin
from wevote_functions.functions import positive_value_exists

logger = wevote_functions.admin.get_logger(__name__)


WE_VOTE_SERVER_ROOT_URL = get_environment_variable("WE_VOTE_SERVER_ROOT_URL")

TWITTER_CONSUMER_KEY = get_environment_variable("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET = get_environment_variable("TWITTER_CONSUMER_SECRET")
TWITTER_ACCESS_TOKEN = get_environment_variable("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = get_environment_variable("TWITTER_ACCESS_TOKEN_SECRET")


def retrieve_twitter_user_info(twitter_user_id, twitter_handle):
    auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth)

    # Strip out the twitter handles "False" or "None"
    if twitter_handle is False:
        twitter_handle = ''
    elif twitter_handle is None:
        twitter_handle = ''
    elif twitter_handle:
        twitter_handle_lower = twitter_handle.lower()
        if twitter_handle_lower == 'false' or twitter_handle_lower == 'none':
            twitter_handle = ''

    twitter_handle_found = False
    twitter_json = []
    try:
        if positive_value_exists(twitter_user_id):
            twitter_user = api.get_user(user_id=twitter_user_id)
            twitter_json = twitter_user._json
            success = True
            status = 'TWITTER_RETRIEVE_SUCCESSFUL-TWITTER_USER_ID ' + str(twitter_user_id)
            twitter_handle_found = True
        elif positive_value_exists(twitter_handle):
            twitter_user = api.get_user(screen_name=twitter_handle)
            twitter_json = twitter_user._json
            success = True
            status = 'TWITTER_RETRIEVE_SUCCESSFUL-TWITTER_HANDLE ' + str(twitter_handle)
            twitter_handle_found = True
        else:
            twitter_json = {}
            success = False
            status = 'TWITTER_RETRIEVE_NOT_SUCCESSFUL-MISSING_VARIABLE'
            twitter_handle_found = False
    except tweepy.RateLimitError as rate_limit_error:
        success = False
        status = 'TWITTER_RATE_LIMIT_ERROR'
        handle_exception(rate_limit_error, logger=logger, exception_message=status)
    except tweepy.error.TweepError as error_instance:
        success = False
        status = twitter_handle + " " if positive_value_exists(twitter_handle) else ""
        status += str(twitter_user_id) + " " if positive_value_exists(twitter_user_id) else " "
        error_tuple = error_instance.args
        for error_dict in error_tuple:
            for one_error in error_dict:
                status += '[' + one_error['message'] + '] '
        handle_exception(error_instance, logger=logger, exception_message=status)

    results = {
        'status':               status,
        'success':              success,
        'twitter_handle':       twitter_handle,
        'twitter_handle_found': twitter_handle_found,
        'twitter_json':         twitter_json,
    }
    return results


def retrieve_twitter_user_possibilities(full_name='', state_code=''):
    search_term = full_name

    auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    results = {'possible_twitter_handles_list': []}
    search_results = api.search_users(q=search_term, page=1)
    search_results.sort(key=lambda possible_candidate: possible_candidate.followers_count, reverse=True)
    denom = sum(candidate.followers_count for candidate in search_results)
    possibility_percentages = [candidate.followers_count / denom for candidate in search_results]

    for possible_candidate_index in range(len(search_results)):
        one_result = search_results[possible_candidate_index]

        current_candidate_twitter_info = {}
        current_candidate_twitter_info['search_term'] = search_term
        current_candidate_twitter_info['likelihood_percentage'] = int(possibility_percentages[possible_candidate_index] * 100)
        current_candidate_twitter_info['twitter_json'] = one_result._json

        results['possible_twitter_handles_list'].append(current_candidate_twitter_info)

    results['success'] = bool(results['possible_twitter_handles_list'])

    return results
