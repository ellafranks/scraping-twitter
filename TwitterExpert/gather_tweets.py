import json

import time

from tqdm import tqdm

import tweepy

from TwitterExpert.gather_experts import scrape_experts
from TwitterExpert.utils import flatten_lists


def iterate_through_users_tweets(_iterator):
    return [{'full_text': tweet.full_text,
             'created_at': str(tweet.created_at),
             'tweet_id': tweet.id_str,
             'tweet_favourite': tweet.favorite_count,
             'tweet_retweet': tweet.retweet_count,
             'tweet_lang': tweet.lang,
             'tweet_in_reply': tweet.in_reply_to_user_id_str,
             'tweet_isquote': tweet.is_quote_status,
             'user_name': tweet.user.name,
             'user_screename': tweet.user.screen_name,
             'user_id': tweet.user.id_str,
             'user_location': tweet.user.location,
             'user_url': tweet.user.url,
             'user_description': tweet.user.description,
             'user_verified': tweet.user.verified,
             'user_follower': tweet.user.followers_count,
             'user_friend': tweet.user.friends_count,
             'user_favourite': tweet.user.favourites_count,
             'user_status': tweet.user.statuses_count,
             'user_listed': tweet.user.listed_count,
             'user_profile_image_url': tweet.user.profile_image_url_https,
             'user_default_profile': tweet.user.default_profile,
             'user_default_profile_image': tweet.user.default_profile_image
             } for tweet in _iterator]


class TwitterCollector:
    def __init__(self, api):
        self.api = api

    @staticmethod
    def from_credentials(key, secret):
        api = tweepy.API(
            tweepy.AppAuthHandler(key, secret),
            wait_on_rate_limit=True,
            wait_on_rate_limit_notify=True
        )

        return TwitterCollector(api)

    def query_by_text(self, text_query, m_tweets, coordinates=None):
        cursor = tweepy.Cursor(
            self.api.search,
            q=text_query,
            geocode=coordinates,
            tweet_mode='extended'
        )

        return cursor.items(m_tweets)

    def convert_nonexpert_to_tweets(self, num_tweets_by_text):
        non_experts_tweets = iterate_through_users_tweets(self.query_by_text(
            text_query="tech -filter:retweets",
            coordinates='37.48164467541928,-122.15819183044557,50mi',
            m_tweets=num_tweets_by_text
        ))
        return non_experts_tweets

    def query_byname(self, m_tweets, experts=None):
        cursor = tweepy.Cursor(self.api.user_timeline,
                               id=experts,
                               tweet_mode='extended'
                               )
        return cursor.items(m_tweets)

    def convert_expert_to_tweets(self, num_tweets_per_user):
        experts = scrape_experts()
        experts_tweets = []
        for username in tqdm(experts):
            try:
                experts_tweets.append(iterate_through_users_tweets(self.query_byname(
                    m_tweets=num_tweets_per_user,
                    experts=username
                )))
            except tweepy.TweepError as e:
                print('Twitter internal excpetion: {}'.format(e))
            except Exception as e:
                print('Other exception: {}'.format(e))

        return list(flatten_lists(experts_tweets))


def write_to_json(fname, data):
    with open(fname, 'w') as file:
        json.dump(data, file)


def execute(key, secret):
    t = TwitterCollector.from_credentials(key=key, secret=secret)
    non_experts_tweets = t.convert_nonexpert_to_tweets(num_tweets_by_text=9000)
    # experts_tweets = t.convert_expert_to_tweets(num_tweets_per_user=100)

    # write_to_json('experts.json', experts_tweets)
    write_to_json('non_experts', non_experts_tweets)


if __name__ == '__main__':
    KEY = 'ctPrHdRrbU3HD4CbvQnYOzWNN'
    SECRET = 'HPENaXC5uuX0IImsE2714focIOGPE1cyLEUSvTMaf7WAGv5Bnx'

    execute(key=KEY, secret=SECRET)
