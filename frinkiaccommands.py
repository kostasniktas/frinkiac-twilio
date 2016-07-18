import frinkquery

USAGE = """Send me a search for simpsons quotes and images:
[#help] [#random] [#nocaption] query
Examples:
#random #nocaption
(returns a random image without a caption on it)

donuts
(returns a random image with a caption. image has to do with donuts)
"""

def do_stuff(full_query):
    if full_query is None or full_query.strip() == "":
        return _build_error_response("You can't ask me to search for nothing!")

    # Build up options
    options = {"random": False, "gif": False, "caption":True, "help": False}
    pieces = full_query.split()
    cmdcount = 0
    for i in pieces:
        if not i.startswith("#"):
            break
        cmdcount += 1
        if i == "#random":
            options["random"] = True
        elif i == "#gif":
            options["gif"] = True
        elif i == "#nocaption":
            options["caption"] = False
        elif i == "#help":
            options["help"] = True

    if options["help"]:
        return _build_response(USAGE, None)

    query = full_query.split(None, cmdcount)[cmdcount:]
    print "DEBUG", "OPTIONS:", options, "QUERY:", query
    response = _get_full_response(query,
                    caption_on_image = options["caption"],
                    gif = options["gif"],
                    random = options["random"])
    return response

def _build_error_response(message):
    return _build_response(message, None, True)

def _build_response(message, imageurl, error=False):
    return {"message": message, "imageurl": imageurl, "error":error}

def _get_full_response(query, caption_on_image=False, gif=False, random=False):
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
        imageurl = frinkquery.get_full_image_url(frame, caption=caption_on_image)
    else:
        pass #TODO Gif?

    return _build_response(frinkquery.fix_captions(captions), imageurl)
