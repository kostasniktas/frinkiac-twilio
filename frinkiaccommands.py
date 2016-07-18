import frinkquery

def do_stuff(full_query):
    if full_query is None or full_query.strip() == "":
        return _build_error_response("You can't ask me to search for nothing!")

    # Build up options
    options = {"random": False, "gif": False, "caption":True}
    pieces = full_query.split()
    cmdcount = 0
    for i in pieces:
        if i == "#random":
            options["random"] = True
        elif i == "#gif":
            options["gif"] = True
        elif i == "#nocaption":
            options["caption"] = False
        elif i == "#help":
            options["help"] = True
        else:
            if not i.startswith("#"):
                break
        cmdcount += 1

    query = full_query.split(None, cmdcount)[cmdcount:]
    print "Debug:", options, query
    response = _get_full_response(query,
                    caption_on_image = options["caption"],
                    gif = options["gif"],
                    random = options["random"])
    return response

def _build_error_response(message):
    return {"error": True, "message": message}

def _get_full_response(query, caption_on_image=False, gif=False, random=False):
    if random:
        frame = frinkquery.get_random_frame()
    else:
        frame = frinkquery.query_one_frame(query)
    if frame is None:
        return _build_error_response("I couldn't find anything matching your query. Sorry.")

    response = {"error": False}

    captions = frinkquery.get_captions_for_frame(frame)

    # Build the actual image url
    # TODO: (Ping the url async to make sure it's ready to go?)
    if not gif:
        imageurl = frinkquery.get_full_image_url(frame, caption=caption_on_image)
    else:
        pass #TODO Gif?

    response["message"] = frinkquery.fix_captions(captions)
    response["imageurl"] = imageurl
    return response
