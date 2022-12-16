from stravaclient.authorisation import OAuthHandler
from stravaclient.endpoint_methods import StravaClient
from stravaclient.storage.tokens import LocalTokenCache, DynamoDBCache


def create_strava_client():
    YOUR_ATHLETE_ID = 'INTEGER'
    YOUR_CLIENT_ID = 'INTEGER'
    YOUR_CLIENT_SECRET = 'STRING'

    token_cache = LocalTokenCache(filename='token_cache')

    # An OAuthHandler is used to store and retrieve tokens from the cache
    authenticator = OAuthHandler(client_id=YOUR_CLIENT_ID,
                                 client_secret=YOUR_CLIENT_SECRET,
                                 token_cache=token_cache)

    # The client can now be instantiated, and a number of handy endpoint methods are available.
    client = StravaClient(authenticator)
    return client
