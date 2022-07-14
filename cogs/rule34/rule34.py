from __future__ import print_function

import asyncio
import math
import random
import os
import atexit
from collections import defaultdict
from xml.etree import cElementTree as ET
import aiohttp
import async_timeout
import warnings

from .objectClasses import Rule34Post

class Rule34_Error(Exception):  # pragma: no cover
    """Rule34 rejected you"""
    def __init__(self, message, *args):
        self.message = message
        super(Rule34_Error, self).__init__(message, *args)


class Request_Rejected(Exception):  # pragma: no cover
    """The Rule34 API wrapper rejected your request"""
    def __init__(self, message, *args):
        self.message = message
        super(Request_Rejected, self).__init__(message, *args)


class SelfTest_Failed(Exception):  # pragma: no cover
    """The self test failed"""
    def __init__(self, message, *args):
        self.message = message
        super(SelfTest_Failed, self).__init__(message, *args)


class Rule34:
    def __init__(self, loop=None, timeout=10):
        """
        :param loop: the event loop. Defaults to none
        :param timeout: how long requests are allowed to run until timing out. Defaults to 10
        """
        if loop:
            self.loop = loop
        else:
            self.loop = asyncio.get_event_loop()
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.timeout = timeout
        atexit.register(self._exitHandler)

    def _exitHandler(self):
        """Makes sure to close the session to avoid warnings"""
        asyncio.run_coroutine_threadsafe(self.session.close(), loop=self.loop)

    def session(self):
        return self.session

    def ParseXML(self, rawXML):
        """Parses entities as well as attributes following this XML-to-JSON "specification"
            Using https://stackoverflow.com/a/10077069"""
        if "Search error: API limited due to abuse" in str(rawXML.items()):
            raise Rule34_Error('Rule34 rejected your request due to "API abuse"')

        d = {rawXML.tag: {} if rawXML.attrib else None}
        children = list(rawXML)
        if children:
            dd = defaultdict(list)
            for dc in map(self.ParseXML, children):
                for k, v in dc.items():
                    dd[k].append(v)
            d = {rawXML.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
        if rawXML.attrib:
            d[rawXML.tag].update(('@' + k, v) for k, v in rawXML.attrib.items())
        if rawXML.text:
            text = rawXML.text.strip()
            if children or rawXML.attrib:
                if text:
                    d[rawXML.tag]['#text'] = text
            else:
                d[rawXML.tag] = text
        return d

    @staticmethod
    def urlGen(tags=None, limit=None, ID=None, PID=None, deleted=None, rating=None, **kwargs):
        """Generates a URL to access the api using your input:
        :param tags: str ||The tags to search for. Any tag combination that works on the web site will work here. This includes all the meta-tags
        :param limit: str ||How many posts you want to retrieve
        :param ID: int ||The post id.
        :param PID: int ||The page number.
        :param deleted: bool||If True, deleted posts will be included in the data
        :param rating: The rating of the images, defaults to explicit
        :param kwargs:
        :return: url string, or None

        All arguments that accept strings *can* accept int, but strings are recommended
        If none of these arguments are passed, None will be returned
        """
        # I have no intentions of adding "&last_id=" simply because its response can easily be massive, and all it returns is ``<post deleted="[ID]" md5="[String]"/>`` which has no use as far as im aware
        URL = "https://rule34.xxx/index.php?page=dapi&s=post&q=index"
        if PID is not None:
            if PID > 2000:
                raise Request_Rejected("Rule34 will reject PIDs over 2000")
            URL += "&pid={}".format(PID)
        if limit is not None:
            URL += "&limit={}".format(limit)
        if ID is not None:
            URL += "&id={}".format(ID)
        if tags is not None:
            tags = str(tags).replace(" ", "+")
            URL += "&tags={}".format(tags)
        if deleted:
            URL += "&deleted=show"
        if PID is not None or limit is not None or ID is not None or tags is not None:
            if ID is not None:
                return URL
            else:
                if rating:
                    return URL + "&rating:" + rating
                else:
                    return URL + "&rating:explicit"
        else:
            return None

    async def totalImages(self, tags):
        """Returns the total amount of images for the tag
        :param tags:
        :return: int
        """
        if self.session.closed:
            self.session = aiohttp.ClientSession(loop=self.loop)
        with async_timeout.timeout(10):
            url = self.urlGen(tags=tags, PID=0)
            async with self.session.get(url=url) as rawXML:
                rawXML = await rawXML.read()
                rawXML = ET.XML(rawXML)
                XML = self.ParseXML(rawXML)
            await self.session.close()
            return int(XML['posts']['@count'])
        return None

    async def getImages(self, tags, fuzzy=False, singlePage=True, randomPID=True, OverridePID=None, rating=None):
        """gatherers a list of image's and their respective data -- replacing getImageURLS
        :param tags: the tags you're searching
        :param fuzzy: enable or disable fuzzy search, default disabled
        :param singlePage: when enabled, limits the search to one page (100 images), default disabled
        :param randomPID: when enabled, a random pageID is used, if singlePage is disabled, this is disabled
        :param OverridePID: Allows you to specify a PID
        :param rating: The rating of the images, defaults to explicit
        :return: list
        """
        if self.session.closed:  # Verify we have an active session (avoids errors)
            self.session = aiohttp.ClientSession(loop=self.loop)
        if fuzzy:
            tags = tags.split(" ")
            for tag in tags:
                tag = tag + "~"
            temp = " "
            tags = temp.join(tags)
        if randomPID is True and singlePage is False:
            randomPID = False
        num = await self.totalImages(tags)

        if num != 0:
            if OverridePID is not None:
                if OverridePID >2000:
                    raise Request_Rejected("Rule34 will reject PIDs over 2000")
                PID = OverridePID
            elif randomPID:
                maxPID = 2000
                if math.floor(num/100) < maxPID:
                    maxPID = math.floor(num/100)
                PID = random.randint(0, maxPID)
            else:
                PID = 0
            imgList = []
            XML = None
            t = True
            while t:
                tempURL = self.urlGen(tags=tags, PID=PID, rating=rating)
                with async_timeout.timeout(self.timeout):
                    if self.session.closed:
                        self.session = aiohttp.ClientSession(loop=self.loop)
                    async with self.session.get(url=tempURL) as XML:
                        XML = await XML.read()
                        XML = ET.XML(XML)
                        XML = self.ParseXML(XML)
                if XML is None:
                    return None
                if len(imgList) >= int(XML['posts']['@count']):  # "if we're out of images to process"
                    t = False  # "end the loop"
                else:
                    for post in XML['posts'].items():
                        if post[0] == "post":
                            if isinstance(post[1], dict):
                                image = Rule34Post()
                                image.parse(post[1])
                                imgList.append(image)
                                continue
                            elif isinstance(post[1], list):
                                for _post in post[1]:
                                    image = Rule34Post()
                                    image.parse(_post)
                                    imgList.append(image)
                                    continue
                if singlePage:
                    await self.session.close()
                    return imgList
                PID += 1
            await self.session.close()
            return imgList
        else:
            await self.session.close()
            return None

    async def getPostData(self, PostID):
        """Returns a dict with all the information available about the post
        :param PostID: The ID of the post
        :return: dict
        """

        if self.session.closed:
            self.session = aiohttp.ClientSession(loop=self.loop)
        url = self.urlGen(ID=str(PostID))
        XML =None
        with async_timeout.timeout(10):
            async with self.session.get(url=url) as XML:
                XML = await XML.read()
            await self.session.close()
            try:
                XML = self.ParseXML(ET.XML(XML))
                data = XML['posts']['post']
            except ValueError:
                return None
            return data
        return None


    async def download(self, URL, destination=None):
        try:
            if self.session.closed:
                self.session = aiohttp.ClientSession(loop=self.loop)
            async with self.session.get(URL) as resp:
                assert resp.status == 200
                i = 7
                name = URL.split("/")[-1][-7:]
                if destination:
                    name = "destination" + "/" + name
                while os.path.isfile(name):
                    i += 1
                    name = URL.split("/")[-1][-i:]
                data = await resp.read()
            await self.session.close()
            with open(name, "wb") as f:
                f.write(data)
        except Exception as e:
            raise Rule34_Error(e)
            return None
        return name


class Sync:
    """Allows you to run the module without worrying about async"""
    def __init__(self):
        self.l = asyncio.get_event_loop()
        self.r = Rule34(self.l)

    def sessionClose(self):  # pragma: no cover
        if not self.r.session.closed:
            self.l.run_until_complete(self.r.session.close())

    def getImages(self, tags, fuzzy=False, singlePage=True, randomPID=True, OverridePID=None, rating=None):
        """gatherers a list of image's and their respective data -- replacing getImageURLS
        :param tags: the tags you're searching
        :param fuzzy: enable or disable fuzzy search, default disabled
        :param singlePage: when enabled, limits the search to one page (100 images), default disabled
        :param randomPID: when enabled, a random pageID is used, if singlePage is disabled, this is disabled
        :param rating: The rating of the images, defaults to explicit
        :param OverridePID: Allows you to specify a PID
        :return: list
        """
        data = self.l.run_until_complete(self.r.getImages(tags, fuzzy, singlePage, randomPID, OverridePID, rating))
        return data

    def getPostData(self, PostID):
        """Returns a dict with all the information available about the post
        :param PostID: The ID of the post
        :return: dict
        """
        return self.l.run_until_complete(self.r.getPostData(PostID))

    def totalImages(self, tags):
        """Returns the total amount of images for the tag
        :param tags:
        :return: int
        """
        return self.l.run_until_complete(self.r.totalImages(tags))

    @staticmethod
    def URLGen(tags=None, limit=None, id=None, PID=None, deleted=None, rating=None):
        """Generates a URL to access the api using your input:
        :param tags: str ||The tags to search for. Any tag combination that works on the web site will work here. This includes all the meta-tags
        :param limit: str ||How many posts you want to retrieve
        :param id: int ||The post id.
        :param PID: int ||The page number.
        :param deleted: bool||If True, deleted posts will be included in the data
        :param kwargs:
        :return: url string, or None
        All arguments that accept strings *can* accept int, but strings are recommended
        If none of these arguments are passed, None will be returned
        """
        return Rule34.urlGen(tags, limit, id, PID, deleted, rating)

    def download(self, url):
        return self.l.run_until_complete(self.r.download(url))