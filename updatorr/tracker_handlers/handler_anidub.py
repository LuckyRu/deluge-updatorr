from updatorr.handler_base import GenericPrivateTrackerHandler
from updatorr.utils import register_tracker_handler
import urllib2
from bs4 import BeautifulSoup
from urllib import urlencode
from updatorr.utils import Cookies


class AnidubHandler(GenericPrivateTrackerHandler):
    """This class implements .torrent files downloads
    for http://tr.anidub.com tracker."""

    login_url = 'http://tr.anidub.com/'
    cookie_logged_in = 'dle_user_id'
    qualities = ['tv720', 'dvd480']

    def get_login_form_data(self, login, password):
        """Should return a dictionary with data to be pushed
        to authorization form.

        """
        return {'login_name': login, 'login_password': password, 'login':'submit'}

    def get_download_link(self):
        """Tries to find .torrent file download link at forum thread page
        and return that one."""
        download_link = None
        response, page_html = self.get_resource(self.resource_url)
        soup = BeautifulSoup(page_html)
        #test for logged in
        if soup.select('form input[name="login"]'):
            self.debug('Login is required to download torrent file.')
            if self.login(self.get_settings('login'), self.get_settings('password')):
                download_link = self.get_download_link()
        else:
            # try to find required download url
            divs = soup.select("div.torrent > div.torrent_c > div")
            for d in divs:
                self.debug('Found div whith quality id "%s"' % d['id'])
            for q in self.qualities:
                self.debug('Try to find quality "%s"' % q)
                selector = 'div.torrent > div.torrent_c > div#%s div.torrent_h a' % q
                self.debug('Selector is "%s"' % selector)
                d = soup.select(selector)
                if d:
                    if type(d) is list:
                        download_link = 'http://tr.anidub.com/%s' % d[0]['href']
                    else:
                        download_link = 'http://tr.anidub.com/%s' % d['href']
                    self.debug("Found download link %s" % download_link);
                    break
                else:
                    self.debug('quality "%s" not found' % q)
        return download_link

    def get_resource(self, url, form_data=None):
        """Returns an HTTP resource data from given URL.
        If a dictionary is passed in `form_data` POST HTTP method
        would be used to pass data to resource (even if that dictionary is empty).

        """
        self.debug('Getting page at %s ...' % url)

        if form_data is not None:
            form_data = urlencode(form_data)

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.get_cookies()))
        request = urllib2.Request(url, form_data,
                                  {'User-agent': 'Mozilla/5.0 (Ubuntu; X11; Linux i686; rv:8.0) Gecko/20100',
                                   'Referer' : self.resource_url})

        try:
            response = opener.open(request)
        except urllib2.URLError:
            return {}, ''

        return response.info(), response.read()

register_tracker_handler('tr.anidub.com', AnidubHandler)
