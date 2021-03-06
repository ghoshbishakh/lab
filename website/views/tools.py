import base64
import requests
from itertools import chain

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied

from meta.views import Meta

from website.models import *


# Definition of functions:

def get_website_section(requested_website_position_id):
    """
    Fetch WebsiteSection with website_position_id

    Parameters
    ----------
    requested_website_position_id : string

    Returns
    ------
    returns WebsiteSection object or None if not found
    """
    try:
        section = WebsiteSection.objects.get(
            website_position_id=requested_website_position_id)
    except ObjectDoesNotExist:
        section = None
    return section


def get_latest_event_posts(limit):
    """
    Fetch Latest EventPost according to post_date

    Parameters
    ----------
    limit : int

    Returns
    ------
    returns a list of NewsPost objects
    """
    return EventPost.objects.order_by('-post_date')[0:limit]


def get_latest_blog_posts(limit):
    """
    Fetch Latest BLogPosts according to post_date

    Parameters
    ----------
    limit : int

    Returns
    ------
    returns a list of BlogPost objects
    """
    return BlogPost.objects.filter(show_in_lab_blog=True).order_by('-posted')[0:limit]


def get_news_posts(limit=None):
    """
    Fetch Latest BLogPosts and EventPosts according to post_date

    Returns
    ------
    returns a list of News objects
    """
    all_blog_posts = BlogPost.objects.filter(show_in_lab_blog=True)
    all_events = EventPost.objects.exclude(end_date__lt=timezone.now()).order_by('-created')
    news_list = sorted(chain(all_blog_posts, all_events), key=lambda news: news.created, reverse=True)
    return news_list if limit is None else news_list[0:limit]


def get_highlight(limit):
    """
    Fetch Latest highlited according to post_date

    Returns
    ------
    returns a list of News objects
    """
    all_blog_posts = BlogPost.objects.filter(is_highlighted=True)
    all_events = EventPost.objects.filter(is_highlighted=True).order_by('-created')
    all_publication = Publication.objects.filter(is_highlighted=True).order_by('-created')
    highlight_list = sorted(chain(all_blog_posts, all_events, all_publication), key=lambda highlight: highlight.created, reverse=True)
    return highlight_list[0:limit]


def has_commit_permission(access_token, repository_name):
    """
    Determine if user has commit access to the repository in nipy organisation.

    Parameters
    ----------
    access_token : string
        GitHub access token of user.
    repository_name : string
        Name of repository to check if user has commit access to it.
    """
    if access_token == '':
        return False
    response = requests.get('https://api.github.com{}repos'.format(settings.REPOSITORY_URL),
                            params={'access_token': access_token})
    response_json = response.json()
    for repo in response_json:
        if repo["name"] == repository_name:
            permissions = repo["permissions"]
            if permissions["pull"]:
                return True
    return False


def github_permission_required(view_function):
    """
    Decorator for checking github commit permission of users
    """
    def wrapper(request, *args, **kwargs):
        try:
            social = request.user.social_auth.get(provider='github')
            access_token = social.extra_data['access_token']
        except:
            access_token = ''
        has_permission = has_commit_permission(access_token, settings.REPOSITORY_NAME)
        if has_permission:
            return view_function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrapper


def get_google_plus_activity(user_id, count):
    """
    Fetch google plus activity list of a user

    Parameters
    ----------
    user_id : string
        The ID of the user to get activities for.

    count : int
        Maximum number of activities to fetch.
    """
    api_key = settings.GOOGLE_API_KEY
    url = "https://www.googleapis.com/plus/v1/people/" + user_id +\
          "/activities/public?maxResults=" + str(count) +\
          "&fields=etag%2Cid%2Citems%2Ckind%2CnextLink%2CnextPageToken%2CselfLink%2Ctitle%2Cupdated&key=" + api_key
    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        return {}
    json_response = r.json()
    if 'error' not in json_response:
        return json_response['items']
    else:
        print(json_response)
        return {}


def get_facebook_page_feed(page_id, count):
    """
    Fetch the feed of posts published by this page, or by others on this page.

    Parameters
    ----------
    page_id : string
        The ID of the page.
    count : int
        Maximum number of posts to fetch.
    """
    app_id = settings.FACEBOOK_APP_ID
    app_secret = settings.FACEBOOK_APP_SECRET

    params = (page_id, count, app_id, app_secret)
    url = ("https://graph.facebook.com/%s/feed?limit=%s&access_token=%s|%s" %
           params)
    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError:
        return {}
    response_json = response.json()
    if 'data' in response_json:
        return response_json["data"]
    else:
        return {}


def get_twitter_bearer_token():
    """
    Fetch the bearer token from twitter and save it to TWITER_TOKEN
    environment variable
    """
    consumer_key = settings.TWITTER_CONSUMER_KEY
    consumer_secret = settings.TWITTER_CONSUMER_SECRET

    bearer_token_credentials = "%s:%s" % (consumer_key, consumer_secret)

    encoded_credentials = base64.b64encode(
        str.encode(bearer_token_credentials)).decode()
    auth_header = "Basic %s" % (encoded_credentials,)

    headers = {'Authorization': auth_header,
               'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
    try:
        response = requests.post('https://api.twitter.com/oauth2/token',
                                 headers=headers,
                                 data={'grant_type': 'client_credentials'})
        response_json = response.json()
    except requests.exceptions.ConnectionError:
        response_json = {}
    if 'access_token' in response_json:
        token = response_json['access_token']
    else:
        token = ''
    os.environ["TWITER_TOKEN"] = token
    return token


def get_twitter_feed(screen_name, count):
    """
    Fetch the most recent Tweets posted by the user indicated
    by the screen_name

    Parameters
    ----------
    screen_name : string
        The screen name of the user for whom to return Tweets for.

    count : int
        Maximum number of Tweets to fetch.
    """
    try:
        token = os.environ["TWITER_TOKEN"]
    except KeyError:
        token = get_twitter_bearer_token()
    parms = (screen_name, str(count))
    url = "https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=%s&count=%s" % parms
    headers = {'Authorization': 'Bearer %s' % (token,)}
    try:
        response = requests.get(url, headers=headers)
    except requests.exceptions.ConnectionError:
        return {}
    response_json = response.json()
    return response_json


def get_meta_tags_dict(title=settings.DEFAULT_TITLE,
                       description=settings.DEFAULT_DESCRIPTION,
                       keywords=settings.DEFAULT_KEYWORDS,
                       url="/", image=settings.DEFAULT_LOGO_URL,
                       object_type="website"):
    """
    Get meta data dictionary for a page

    Parameters
    ----------
    title : string
        The title of the page used in og:title, twitter:title, <title> tag etc.
    description : string
        Description used in description meta tag as well as the
        og:description and twitter:description property.
    keywords : list
        List of keywords related to the page
    url : string
        Full or partial url of the page
    image : string
        Full or partial url of an image
    object_type : string
        Used for the og:type property.
    """
    meta = Meta(title=title,
                description=description,
                keywords=keywords + settings.DEFAULT_KEYWORDS,
                url=url,
                image=image,
                object_type=object_type,
                use_og=True, use_twitter=True, use_facebook=True,
                use_googleplus=True, use_title_tag=True)
    return meta


def get_youtube_videos(channel_id, count):
    """
    Fetch the list of videos posted in a youtube channel

    Parameters
    ----------
    channel_id : string
        Channel ID of the youtube channel for which the videos will
        be retrieved.

    count : int
        Maximum number of videos to fetch.
    """

    parms = (channel_id, settings.GOOGLE_API_KEY)
    url = "https://www.googleapis.com/youtube/v3/search?order=date&part=snippet&channelId=%s&maxResults=25&key=%s" % parms
    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError:
        return {}
    response_json = response.json()
    return response_json['items']
