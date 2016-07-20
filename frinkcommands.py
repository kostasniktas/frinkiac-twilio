import frinkquery
import logging

logger = logging.getLogger('frinkiacsms')

USAGE = """Send me a search for simpsons quotes and images:
[#help] [#random] [#gif] [#nocaption] [#fullcaption] query
Examples:

#random #nocaption
(returns a random image without a caption on it)

donuts
(returns an image with a caption. image has to do with donuts)

#fullcaption donuts
(returns an image with the entire caption. image has to do with donuts)
"""
GIF_BEFORE = 0.3
GIF_AFTER = 1.7

def do_stuff(full_query):
    """
    Take a full query (with commands and query) and actually do the thing.

    Returns a response for the user.
    """
    if full_query is None or full_query.strip() == "":
        return _build_error_response("You can't ask me to search for nothing!")

    # Build up options
    options = {"random": False, "gif": False, "caption":True,
               "fullcaption":False, "help": False, "callme": False}
    pieces = full_query.split()
    cmdcount = 0
    for i in pieces:
        if not i.startswith("#"):
            break
        if i == "#random":
            options["random"] = True
        elif i == "#gif":
            options["gif"] = True
        elif i == "#nocaption":
            options["caption"] = False
        elif i == "#fullcaption":
            options["fullcaption"] = True
        elif i == "#callme":
            options["callme"] = True
        elif i == "#help":
            options["help"] = True
        cmdcount += 1

    if cmdcount >= len(pieces):
        query = None
    else:
        query = full_query.split(None, cmdcount)[cmdcount]

    logger.info(u"FullQuery[{}] => Options[{}] Query[{}]".format(full_query,options,query))

    if options["help"]:
        return _build_response(USAGE, None, error=True)

    if options["callme"]:
        return _build_response("Call", None, callme=True)

    response = _get_full_response(query,
                    caption_on_image = options["caption"],
                    all_captions = options["fullcaption"],
                    gif = options["gif"],
                    random = options["random"])
    return response


def _build_error_response(message):
    return _build_response(message, None, True)


def _build_response(message, imageurl, error=False, callme=False):
    return {"message": message, "imageurl": imageurl, "error":error, "callme":callme}


def _get_full_response(query, caption_on_image=False, all_captions=False, gif=False, random=False):
    if random:
        frame = frinkquery.get_random_frame()
    else:
        frame = frinkquery.query_one_frame(query)
    if frame is None:
        return _build_error_response("I couldn't find anything matching your query. Sorry.")

    captions = frinkquery.get_captions_for_frame(frame)

    # Build the actual image url
    # TODO: (Ping the url async to make sure it's ready to go?)
    if not gif:
        imageurl = frinkquery.get_full_image_url(frame, caption=caption_on_image, all_captions=all_captions)
    else:
        imageurl = frinkquery.get_full_gif_url(frame, before=GIF_BEFORE, after=GIF_AFTER, caption=caption_on_image, all_captions=all_captions)

    return _build_response(frinkquery.fix_captions(captions, all_captions=all_captions), imageurl)
