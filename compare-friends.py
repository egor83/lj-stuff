import os
import logging
import sys

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

import comparer
import compare_multi


class MainPage(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(open(path).read())

class CommonFriends(webapp.RequestHandler):
    def get(self):
        path = get_page(self.request, 'common_friends.html')
        self.response.out.write(open(path).read())

class CommonMulti(webapp.RequestHandler):
    def get(self):
        path = get_page(self.request, 'compare_multi.html')
        self.response.out.write(open(path).read())


class ErrorPage(webapp.RequestHandler):
    def get(self):
        # using bilingual error page for now
        # will change it later to select the language depending on cookies
        path = os.path.join(os.path.dirname(__file__), 'error.html')
        self.response.out.write(open(path).read())


profile_link = ('<a href="http://%s.livejournal.com/profile?mode=full">'
                '%s</a>')
        
class Calculate(webapp.RequestHandler):
    def post(self):
        username1 = self.request.get('username1')
        username2 = self.request.get('username2')

        fs1, fofs1 = comparer.get_friends(username1)
        fs2, fofs2 = comparer.get_friends(username2)

        common_fs = comparer.find_common(fs1, fs2)
        common_fs.sort()

        common_fofs = comparer.find_common(fofs1, fofs2)
        common_fofs.sort()

        # the rest of the function should be replaced with the code taken
        # from multi version
        
        common_fs_links = [profile_link % (fr, fr) for fr in common_fs]
        render_common_fs = ", ".join(common_fs_links)
        common_fofs_links = [profile_link % (fr, fr) for fr in common_fofs]
        render_common_fofs = ", ".join(common_fofs_links)
        
        template_values = {
            'username1': profile_link % (username1,username1),
            'f1_len': len(fs1),
            'fof1_len': len(fofs1),
            'username2': profile_link % (username2,username2),
            'f2_len': len(fs2),
            'fof2_len': len(fofs2),
            'common_fs_len': len(common_fs),
            'common_friends': render_common_fs,
            'common_fofs_len': len(common_fofs),
            'common_friendofs': render_common_fofs
            }
        
        path = get_page(self.request, 'results.html')
        self.response.out.write(template.render(path, template_values))

    def handle_exception(self, exception, mode):
        # from http://bit.ly/gZLnrk
        
        webapp.RequestHandler.handle_exception(self, exception, mode)
        logging.error("Exception has occured while comparing "
                      "friends lists: %s", repr(sys.exc_info()[1]))
        self.redirect("/error.html")
        return


class CalculateMulti(webapp.RequestHandler):
    def post(self):
##        print self.request.get('usernames')
        usernames = self.request.get('usernames')
        common_fs, common_fofs = compare_multi.comp_lj(usernames)

        common_fs_links = [profile_link % (fr, fr) for fr in common_fs]
        render_common_fs = ", ".join(common_fs_links)
        common_fofs_links = [profile_link % (fr, fr) for fr in common_fofs]
        render_common_fofs = ", ".join(common_fofs_links)

        template_values = {
            'usernames': usernames,
            'common_friends': render_common_fs,
            'common_fs_len': len(common_fs),
            'common_friendofs': render_common_fofs,
            'common_fofs_len': len(common_fofs)
            }

        path = get_page(self.request, 'results_multi.html')
        self.response.out.write(template.render(path, template_values))


def get_page(request, page):
    """Pick the translated page based on the language passed along with the
request.

Use default page if no language is set or (TBD) if the language that was sent
is not supported."""
    
    dirname = os.path.dirname(__file__)

    lang = request.get('lang')
    if lang != '':
        dirname = os.path.join(dirname, 'translations', lang)
        # TODO - add try/except for non-existing translations

    path = os.path.join(dirname, page)
    return path


application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/common.html', CommonFriends),
                                      ('/compare_multi.html', CommonMulti),
                                      ('/results.html', Calculate),
                                      ('/results_multi.html', CalculateMulti),
                                      ('/error.html', ErrorPage)],
                                     debug=True)


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(application)


if __name__ == "__main__":
    main()
