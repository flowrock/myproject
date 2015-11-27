from functools import partial

from json_finder import _parse_json
from http import http_request, smart_urlencode, paginate

class FiveHundredPx(object):
    BASE_URL = 'https://api.500px.com/v1'
    def __init__(self, consumer_key, consumer_secret, verify_url=None):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret

    def get_photos(self, skip=None, rpp=20, **kwargs):
        request_function = partial(self.request, '/photos', **kwargs)
        for photo in paginate(skip, rpp, request_function, 'photos'):
            yield photo

    def get_followers(self, user_id, skip=None, rpp=50, **kwargs):
        path = '/users/'+user_id+'/followers'
        request_function = partial(self.request_followers, path, **kwargs)
        for follower in paginate(skip, rpp, request_function, 'followers', 'followers_pages'):
            yield follower

    def request(self, path, post_args=None, log_request=False, **kwargs):
        """Handles the actual request to 500px. Posting has yet 
        to be implemented.
        """
        if post_args:
            raise NotImplementedError
        self._set_consumer_key_to_args_(post_args, kwargs)
        base_url = FiveHundredPx.BASE_URL
        return http_request(base_url, path, post_args, log_request, **kwargs) 

    def request_followers(self, path, post_args=None, log_request=False, **kwargs):
        """Requesting followers does not need consumer key
        """
        if post_args:
            raise NotImplementedError
        base_url = FiveHundredPx.BASE_URL
        return http_request(base_url, path, post_args, log_request, **kwargs) 

    def _set_consumer_key_to_args_(self, post_args, kwargs):
        if post_args is not None:
            post_args["consumer_key"] = self.consumer_key
        else:
            kwargs["consumer_key"] = self.consumer_key  