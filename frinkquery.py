import json
import logging
import random
import requests
import urllib

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

FRINKIAC_URL = "https://www.frinkiac.com"
CAPTION_MAX_LINE = 25

def get_random_frame():
    """
    Ask Frinkiac for a completely random scene

    Returns dict with frame info
    """
    r = requests.get("{}/api/random".format(FRINKIAC_URL))
    if not r.ok:
        logger.error("Random Query failed: {} {}".format(r.status_code, r.reason))
    result = r.json()
    if "Frame" not in result:
        logger.error("Random Query result didn't have frame: {}".format(r.text))
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
        logger.error("Query [{}] failed: {} {}".format(query, r.status_code, r.reason))
    result = r.json()
    logger.debug("Query [{}] found {} results.".format(query,len(result)))
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
    url = "{}/api/caption?{}".format(FRINKIAC_URL,
            urllib.urlencode({"e": frame["episode"], "t": frame["timestamp"]}))
    r = requests.get(url)
    if not r.ok:
        logger.error("CaptionQuery [{}] failed: {} {}".format(url, r.status_code, r.reason))
    result = r.json()
    captions = []
    #TODO Check for "Subtitles"
    for i in result["Subtitles"]:
        captions.append(i["Content"])
    return captions

def get_full_image_url(frame, caption=False, all_captions=False):
    """
    Get the image URL for a frame

    Returns a string with the image URL
    """
    url = "{}/meme/{}/{}".format(FRINKIAC_URL, frame["episode"], frame["timestamp"])
    if caption:
        captions = get_captions_for_frame(frame)
        return "{}?{}".format(url, urllib.urlencode({"lines": fix_captions(captions, all_captions=all_captions)}))
    return url

#TODO: Maybe just take the first line
def fix_captions(captions, all_captions=False):
    if all_captions:
        return "\n".join([_fix_single_caption(c) for c in captions]) #TODO
    else:
        if len(captions) > 0:
            return _fix_single_caption(captions[0])
    return ""

def _fix_single_caption(caption_line):
    lines = []
    current_line = []
    count = 0
    for word in caption_line.split():
        if count + len(current_line) - 1 >= CAPTION_MAX_LINE:
            count = 0
            lines.append(" ".join(current_line))
            current_line = []
        current_line.append(word)
        count += len(word)
    if len(current_line) > 0:
        lines.append(" ".join(current_line))
    print "{} => {}".format(caption_line,"\n".join(lines))
    return "\n".join(lines)
