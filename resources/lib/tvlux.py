import cookielib
import urllib2
import urlparse
import re
import time

import util
from provider import ContentProvider

class TVLuxContentProvider(ContentProvider):
    DATE_REGEX = re.compile("^[0-9]+\.[0-9]+\.[0-9]+$")
    listing_iter_re = re.compile(r"""<a\ .*href=\"(?P<url>[^\"]+)\".*>""")
    pager_begin = '<div class="pager">'

    def __init__(self, username=None, password=None, filter=None, tmp_dir='/tmp'):
        ContentProvider.__init__(self, 'tvlux', 'http://www.tvlux.sk/', username, password, filter, tmp_dir)
        self.cp = urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar())
        self.init_urllib()

    def init_urllib(self):
        opener = urllib2.build_opener(self.cp)
        urllib2.install_opener(opener)

    def capabilities(self):
        return ['categories',
                'resolve',
                '!download']

    def normalize_url(self, url):
        if url.startswith("//"):
            return "http:" + url
        elif url.startswith("/"):
            return "http:/" + url
        return url

    ##
    #  Initial screen showing categories
    def categories(self):
        result = []

        # the first category is video item pointing to live stream
        item = self.video_item()
        item['title'] = 'TV Lux Live'
        item['url'] = self.base_url + "nazivo/#live"
        item['year'] = time.strftime("%Y")
        result.append(item)

        # the second category is directory item pointing to list of programs from archive
        result.append(self.dir_item('Relacie', self.base_url + 'videoarchiv#mycat'))

        # directory item - list of new videos
        result.append(self.dir_item("Nove", self.base_url + 'videoarchiv#nove'))

        # directory item - list of most viewed videos
        result.append(self.dir_item("Najpozeranejsie", self.base_url + 'videoarchiv#pozerane'))
        return result


    def _list_mycat(self, page):
        # this is just Relacie page, need to list all TV programs
        result = []
        prog_list_start = '<select id="archivSelectRel"'
        prog_select = util.substr(page, prog_list_start, '</select>')
        for m in re.finditer('<option\ value=\"(?P<id>\d+)\">(?P<title>[^<]+)</option>', prog_select):
            # filter out categories with invalid ID
            try:
                int(m.group('id'))
            except ValueError:
                continue

            item = self.dir_item()
            # set url with markup #program
            item['url'] = self.normalize_url(self.base_url + \
                                             "archiv/listing/&type=relacia&id=" + \
                                             m.group('id') + \
                                             "#program")
            item['title'] = m.group('title')
            self._filter(result, item)
        return result

    def _resolve_parts(self, part_list):
        result = []

        # walk all parts listed
        for part in part_list:
            url_match = re.search(self.listing_iter_re, part)
            if not url_match:
                continue

            item = self.video_item()
            item['url'] = self.normalize_url(url_match.group('url'))
            item['title_num'] = "0"
            item['date'] = "0.0.0"
            info_list = part.split("\n")

            # walk information about the current video
            for info in info_list:
                info = info.strip()
                if info.startswith('<div class="archiveItemTitle">'):
                    # set title and parse the part number from the title (the number is used for sorting)
                    title = info[info.find(">") + 1:info.rfind("<")]
                    item["title"] = title
                    left = title.find('(')
                    right = title.find(')')
                    if left >= 0 and left < right:
                        num = title[(left + 1): right]
                        try:
                            num = int(num)
                            item['title_num'] = "%05d" % num
                        except ValueError:
                            # invalid value
                            item['title_num'] = num
                    else:
                        item['title_num'] = ''
                elif info.startswith('<div class="archiveItemDesc">'):
                    # set description
                    item["plot"] = info[info.find(">") + 1:info.rfind("<")]
                elif info.startswith('<div class="date">'):
                    # set data (for sorting purposes only)
                    info_date = info[info.find(">") + 1: info.rfind("<")]
                    if self.DATE_REGEX.match(info_date):
                        item["date"] = info_date
                        item["year"] = info_date.split(".")[2]

            self._filter(result, item)

        return result

    def _sort_programs(self, result):
        # Sort results according to found information used in this order:
        #   1. Number from the video title (if exists)
        #   2. Date (in reverse format -> yyyy.mm.dd)
        #   3. Title (lower case)
        result = sorted(result, key=lambda x: ((x['title_num']) +
                                               (str.join(".", x['date'].split(".")[::-1])) +
                                               (x['title'].lower())), reverse=True)
        return result

    def _resolve_pager(self, page, result):
        # Parse and store URL to next listing page if exists
        pages = util.substr(page, '<div class="pages">', '</div>')
        next_page_match = re.search(r'<a href="(?P<url>[^"]+)" class="nextPage active"', pages)
        if next_page_match:
            self.info("Next page match URL: " + next_page_match.group('url').replace('&amp;', '&'))
            item = self.dir_item()
            item['type'] = 'next'
            item['url'] = self.normalize_url(next_page_match.group('url').replace('&amp;', '&') + "#program")
            item['title'] = "Dalsie"
            self._filter(result, item)

    def _list_program(self, page):
        # need to list all parts of the same program
        part_list_start = '<div class="archivListing">'
        part_list = util.substr(page, part_list_start, '<div class="clr"></div>')
        part_list = part_list.split("</a>")
        result = self._resolve_parts(part_list)
        result = self._sort_programs(result)

        self._resolve_pager(page, result)
        return result

    def _sort_nove(self, result):
        # Sort results according to found information used in this order:
        #   1. Date (in reverse format -> yyyy.mm.dd)
        #   2. Title (lower case)
        result = sorted(result, key=lambda x: ((str.join(".", x['date'].split(".")[::-1])) +
                                               (x['title'].lower())), reverse=True)
        return result

    def _list_nove(self, page):
        result = []
        page = util.substr(page, '<div class="tab" id="tabcontent-4">', '<div class="programBanners">')

        part_list_start = '<div class="archivListing">'
        part_list = util.substr(page, part_list_start, self.pager_begin)
        part_list = part_list.split("</a>")

        result = self._resolve_parts(part_list)
        result = self._sort_nove(result)

        self._resolve_pager(page, result)
        return result

    def _list_pozerane(self, page):
        result = []
        page = util.substr(page, '<div class="tab" id="tabcontent-3">', '<div class="tab" id="tabcontent-4">')

        part_list_start = '<div class="archivListing">'
        part_list = util.substr(page, part_list_start, self.pager_begin)
        part_list = part_list.split("</a>")

        result = self._resolve_parts(part_list)
        # not needed to sort ?
        self._resolve_pager(page, result)
        return result

    ##
    # Method called for URLs of selected directory item
    def list(self, url):

        # try to find my markups starting with '#'
        purl = urlparse.urlparse(url)
        if (url.find("#") != -1):
            # remove markup from the URL
            url=url[:url.find("#")]

        page = util.request(url)

        if purl.fragment == "mycat":
            return self._list_mycat(page)

        elif purl.fragment == "program":
            return self._list_program(page)

        elif purl.fragment == "nove":
            return self._list_nove(page)

        elif purl.fragment == "pozerane":
            return self._list_pozerane(page)

        return []

    ##
    # Method is called for video items, can be used to provide multiple choices
    # according to video quality
    def resolve(self, item, captcha_cb=None, select_cb=None):
        # Cler the URL, remove markups if exists
        url = item['url']
        purl = urlparse.urlparse(url)
        if (url.find("#") != -1):
            url=url[:url.find("#")]

        # prepare new video item
        item = self.video_item()
        item['surl'] = item['title']
        video_page = util.request(url)

        if purl.fragment == "live":
            # resolve live video
            liveMobile = util.substr(video_page, '<div id="mobileDeviceSwitch">', '</div>')
            stream_re = r"""<a class=\"android\" href=\"(?P<url>[^\"]+)\""""
            match = re.search(stream_re, liveMobile)
            item['url'] = match.group('url')
            return item

        # resolve video of program from archive
        video_tag = util.substr(video_page, '<video>', '</video>')
        video_re = r"""<source.*src=\"(?P<url>[^\"]+)\".*>"""
        match = re.search(video_re, video_tag)
        item['url'] = self.normalize_url(match.group('url'))

        return item