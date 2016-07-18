import frinkquery

def do_stuff(query):
    frame = frinkquery.query_one_frame(query)
    return frinkquery.get_full_image_url(frame, caption=True)

def _get_full_response(query, caption_on_image=False, gif=False, random=False):
    if random:
        frame = frinkquery.get_random_frame()
    else:
        frame = frinkquery.query_one_frame(query)

    response = {}

    captions = frinkquery.get_captions_for_frame(frame)
    if not gif:
        imageurl = frinkquery.get_full_image_url(frame, caption=caption_on_image)

    response["captions"] = frinkquery.fix_captions(captions)
    response["imageurl"] = imageurl
    return response
