import json
import random
import requests
import urllib

FRINKIAC_URL = "https://www.frinkiac.com"

def get_random_frame():
    """
    Ask Frinkiac for a completely random scene

    Returns dict with frame info
    """
    r = requests.get("{}/api/random".format(FRINKIAC_URL))
    if not r.ok:
        raise Exception("Bad times during random check") #TODO
    result = r.json()
    if "Frame" not in result:
        raise Exception("No Frame in random?") #TODO
    return {"id": result["Frame"]["Id"],
            "episode": result["Frame"]["Episode"],
            "timestamp": result["Frame"]["Timestamp"]}

def query_all_frames(query):
    """
    Query Frinkiac for all frames matching the query.

    Returns list of dicts with frame info
    """
    r = requests.get("{}/api/search?{}".format(FRINKIAC_URL,
                        urllib.urlencode({"q": query})))
    if not r.ok:
        raise Exception("Bad times during a query [{}]".format(query)) #TODO
    result = r.json()
    return [{"id": i["Id"], "episode": i["Episode"], "timestamp": i["Timestamp"]}
                for i in result]

def query_one_frame(query):
    """
    Query Frinkiac for one random frame that matches the query.

    Returns a dict with the frame info
    """
    results = query_all_frames(query)
    if len(results) < 1:
        return None
    return random.choice(results)

def get_captions_for_frame(frame):
    """
    Query Frinkiac for the caption information for a frame.

    Returns a list of strings with all captions
    """
    r = requests.get("{}/api/caption?{}".format(FRINKIAC_URL,
                        urllib.urlencode({"e": frame["episode"], "t": frame["timestamp"]})))
    if not r.ok:
        raise Exception("Bad times during finding captions for [{}]",format(frame)) #TODO
    result = r.json()
    captions = []
    #TODO Check for "Subtitles"
    for i in result["Subtitles"]:
        captions.append(i["Content"])
    return captions

def get_full_image_url(frame, caption=False):
    """
    Get the image URL for a frame

    Returns a string with the image URL
    """
    url = "{}/meme/{}/{}".format(FRINKIAC_URL, frame["episode"], frame["timestamp"])
    if caption:
        captions = get_captions_for_frame(frame)
        return "{}?{}".format(url, urllib.urlencode({"lines": fix_captions(captions)}))
    return url

def fix_captions(captions):
    return "\n".join(captions) #TODO
