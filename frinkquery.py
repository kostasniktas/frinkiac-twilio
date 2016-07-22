import difflib
import json
import logging
import logging.handlers
import multiprocessing
import random
import requests
import urllib

logger = logging.getLogger('frinkiacsms')


FRINKIAC_URL = "https://www.frinkiac.com"
CAPTION_MAX_LINE = 25
MOST_CHOICES = 5

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

def _add_caption_raw_to_frame(frame):
    frame["caption_raw"] = get_captions_for_frame(frame)
    return frame

def query_all_frames(query):
    """
    Query Frinkiac for all frames matching the query.

    Returns list of dicts with frame info
    """
    qurl = urllib.urlencode({"q": query.encode('utf8')})
    r = requests.get(u"{}/api/search?{}".format(FRINKIAC_URL,qurl))
    if not r.ok:
        logger.error(u"Query [{}] failed: {} {}".format(query, r.status_code, r.reason))
    result = r.json()
    logger.debug(u"Query [{}] found {} results.".format(query,len(result)))
    all_results = [{"id": i["Id"], "episode": i["Episode"], "timestamp": i["Timestamp"]}
                        for i in result]

    pool = multiprocessing.Pool(processes=4)
    all_results = pool.map(_add_caption_raw_to_frame, all_results)

    return all_results

def _string_score(query, caption):
    return difflib.SequenceMatcher(None, query, caption).ratio()

def query_one_frame(query, better_choosing=True):
    """
    Query Frinkiac for one random frame that matches the query.

    Returns a dict with the frame info
    """
    results = query_all_frames(query)
    if len(results) < 1:
        return None

    if not better_choosing:
        return random.choice(results)

    queryl = query.lower()
    for result in results:
        result["caption_to_score"] = " ".join(result["caption_raw"]).lower()
        result["score"] = _string_score(queryl, result["caption_to_score"])
    sliced_sorted = sorted(results, key=lambda s: s["score"], reverse=True)[:MOST_CHOICES]

    # Find max weight
    total = sum([result["score"] for result in sliced_sorted])

    # Pick a random one based on the weights
    choice = random.uniform(0, total)
    so_far = 0
    for result in sliced_sorted:
        if so_far + result["score"] >= choice:
            ranked_captions = []
            for c in result["caption_raw"]:
                ranked_captions.append({"score":_string_score(queryl,c), "caption": c})
            result["caption_first"] = sorted(ranked_captions, key=lambda s: s["score"], reverse=True)[0]["caption"]
            return result
        so_far += result["score"]
    return None # uh oh

def get_captions_for_frame(frame):
    """
    Query Frinkiac for the caption information for a frame.

    Returns a list of strings with all captions
    """
    url = "{}/api/caption?{}".format(FRINKIAC_URL,
            urllib.urlencode({"e": frame["episode"], "t": frame["timestamp"]}))
    r = requests.get(url)
    if not r.ok:
        logger.error(u"CaptionQuery [{}] failed: {} {}".format(url, r.status_code, r.reason))
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
        captions = frame["caption_raw"]
        return "{}?{}".format(url, urllib.urlencode({"lines": fix_captions(captions, caption_first=frame["caption_first"],
                                all_captions=all_captions).encode('utf8')}))
    return url

def get_full_gif_url(frame, before=0, after=0, caption=False, all_captions=False):
    """
    Get the GIF URL for a frame
    """
    midpoint = int(frame["timestamp"])
    if before + after > 10:
        overflow = before + after - 10
        if before > after:
            before -= overflow
        elif after > before:
            after -= overflow
        else:
            before -= (overflow / 2)
            after -= (overflow / 2)
    start = int(midpoint - (before * 1000))
    end = int(midpoint + (after * 1000))
    url = "{}/gif/{}/{}/{}.gif".format(FRINKIAC_URL, frame["episode"], start, end)
    if caption:
        captions = frame["caption_raw"]
        return "{}?{}".format(url, urllib.urlencode({"lines": fix_captions(captions, caption_first=frame["caption_first"],
                                    all_captions=all_captions).encode('utf8')}))
    return url

def fix_captions(captions, caption_first=None, all_captions=False):
    if all_captions:
        return "\n".join([_fix_single_caption(c) for c in captions]) #TODO
    elif caption_first is not None:
        return _fix_single_caption(caption_first)
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
    logger.debug(u"{} => {}".format(caption_line,"\n".join(lines)))
    return "\n".join(lines)
