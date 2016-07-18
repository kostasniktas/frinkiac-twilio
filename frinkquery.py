import json
import requests
import urllib

FRINKIAC_URL = "https://www.frinkiac.com"

def get_random_frame():
    """
    Ask Frinkiac for a completely random scene
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
