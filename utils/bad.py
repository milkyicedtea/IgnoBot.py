

def getImages(url):
    submission = reddit.submission(url=url)
    # Tell API to return all comment in thread, results are
    # paginated by default
    submission.comments.replace_more(limit=None)

    # Create RegEx object for matching images
    REGEX_TEST = r"((http|https)://i.imgur.com/.+?(jpg|png))"
    p = re.compile(REGEX_TEST, re.IGNORECASE)

    imageMatches = []
    for comment in submission.comments.list():
        matches = p.findall(comment.body)
        for match in matches:
            if checkLinkActive(match[0]):
                imageMatches.append(
                    {"image": match[0], "thumbnail": getImgurThumbnail(match[0], "m")}
                )

    return imageMatches