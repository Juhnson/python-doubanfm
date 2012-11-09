# copy from _MozillaCookieJar.py

import re, time
import datetime
import cookielib

from cookielib import (_warn_unhandled_exception, FileCookieJar, LoadError,
                       Cookie, MISSING_FILENAME_TEXT)

class FirecookieCookieJar(FileCookieJar):

    timeformat = '%a, %d %b %Y %H:%M:%S %Z'

    def _really_load(self, f, filename, ignore_discard, ignore_expires):
        now = time.time()

        try:
            while 1:
                line = f.readline()
                if line == "": break

                # last field may be absent, so keep any trailing tab
                if line.endswith("\n"): line = line[:-1]

                # skip comments and blank lines XXX what is $ for?
                if (line.strip().startswith(("#", "$")) or
                    line.strip() == ""):
                    continue

#                domain, domain_specified, path, secure, expires, name, value = \
#                        line.split("\t")

                arr = line.strip().split("\t")
                arr.reverse()

                domain = arr.pop()
                domain_specified = arr.pop()
                path = arr.pop()
                secure = arr.pop()
                expires = arr.pop()

                try:
                    d = datetime.datetime.strptime(expires, self.timeformat)
                    t = d.timetuple()
                    expires = time.mktime(t)
                except:
                    continue

                name = arr.pop()
                if arr:
                    value = arr.pop()

                secure = (secure == "TRUE")
                domain_specified = (domain_specified == "TRUE")

                initial_dot = domain.startswith(".")
                assert domain_specified == initial_dot

                discard = False
                if expires == None:
                    expires = None
                    discard = True

                # assume path_specified is false
                c = Cookie(0, name, value,
                           None, False,
                           domain, domain_specified, initial_dot,
                           path, False,
                           secure,
                           expires,
                           discard,
                           None,
                           None,
                           {})
                if not ignore_discard and c.discard:
                    continue
                if not ignore_expires and c.is_expired(now):
                    continue
                self.set_cookie(c)

        except IOError:
            raise
        except Exception:
            _warn_unhandled_exception()
            raise LoadError("invalid Netscape format cookies file %r: %r" %
                            (filename, line))

    def save(self, filename=None, ignore_discard=False, ignore_expires=False):
        if filename is None:
            if self.filename is not None: filename = self.filename
            else: raise ValueError(MISSING_FILENAME_TEXT)

        f = open(filename, "w")
        try:
            f.write(self.header)
            now = time.time()
            for cookie in self:
                if not ignore_discard and cookie.discard:
                    continue
                if not ignore_expires and cookie.is_expired(now):
                    continue
                if cookie.secure: secure = "TRUE"
                else: secure = "FALSE"
                if cookie.domain.startswith("."): initial_dot = "TRUE"
                else: initial_dot = "FALSE"
                if cookie.expires is not None:
                    # expires = str(cookie.expires)
                    d = datetime.datetime.fromtimestamp(expires)
                    expires = d.strftime(self.timeformat)
                else:
                    expires = ""
                if cookie.value is None:
                    # cookies.txt regards 'Set-Cookie: foo' as a cookie
                    # with no name, whereas cookielib regards it as a
                    # cookie with no value.
                    name = ""
                    value = cookie.name
                else:
                    name = cookie.name
                    value = cookie.value
                f.write(
                    "\t".join([a for a in [cookie.domain, initial_dot, cookie.path,
                               secure, expires, name, value] if a ])+
                    "\n")
        finally:
            f.close()
