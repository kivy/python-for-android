
import os
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse
try:
    from urllib.request import Request, urlopen
except ImportError:
    from urllib2 import Request, urlopen
try:
    import http.client
except ImportError:
    pass
import socket
import sys
from sys import stdout
import time
try:
    from time import monotonic as monotonic_time
except ImportError:
    from time import time as monotonic_time


def download_without_retry(url, target):
    """
    Obtain a file without retrying. Raises OSError on failure.
    """
    parsed_url = urlparse(url)
    if parsed_url.scheme in ('http', 'https'):
        last_feedback_time = {"time": monotonic_time() - 100}

        # Helper function to print out the progress as we go:
        def report_hook(dl_bytes, total_bytes):
            if total_bytes <= 0:
                progression = '{0} bytes'.format(dl_bytes)
            else:
                progression = '{0:.2f}%'.format(
                    dl_bytes * 100. / float(total_bytes)
                )
            if "CI" not in os.environ:
                # Terminals can be slow. Write progress only in larger
                # intervals to not slow down the download speed too much:
                if last_feedback_time["time"] + 0.5 < monotonic_time():
                    stdout.write('- Download {}\r'.format(progression))
                    stdout.flush()
                    last_feedback_time["time"] = monotonic_time()

        if os.path.exists(target):
            os.unlink(target)

        # Construct request with user-agent:
        request = Request(url, headers={"User-agent": "Wget/1.17.1"})

        def download_request_object(req):
            progress = 0
            known_total = 0
            if "content-length" in req.headers:
                try:
                    known_total = max(0, int(req.headers["content-length"]))
                except (ValueError, TypeError):
                    pass

            with open(target, "wb") as f:
                while True:
                    if int(sys.version.split(".")[0]) >= 3:
                        try:
                            chunk = req.read(512)
                        except (socket.timeout, http.client.IncompleteRead):
                            raise OSError("reading timed out")
                    else:
                        # no http.client module in python 2
                        try:
                            chunk = req.read(512)
                        except socket.timeout:
                            raise OSError('reading timed out')
                    if len(chunk) == 0:
                        if known_total > 0 and progress < known_total:
                            raise OSError("EOF before reaching "
                                          "Content-Length")
                        break
                    progress += len(chunk)
                    f.write(chunk)
                    report_hook(progress, known_total)

        # Trigger actual download:
        try:
            with urlopen(request, timeout=25) as req:
                download_request_object(req)
        except TypeError:  # python 2 doesn't support timeout
            with urlopen(request) as req:
                download_request_object(req)
        return target
    elif parsed_url.scheme in ('git', 'git+file', 'git+ssh', 'git+http', 'git+https'):
        if isdir(target):
            with current_directory(target):
                shprint(sh.git, 'fetch', '--tags')
                if self.version:
                    shprint(sh.git, 'checkout', self.version)
                shprint(sh.git, 'pull')
                shprint(sh.git, 'pull', '--recurse-submodules')
                shprint(sh.git, 'submodule', 'update', '--recursive')
        else:
            if url.startswith('git+'):
                url = url[4:]
            shprint(sh.git, 'clone', '--recursive', url, target)
            if self.version:
                with current_directory(target):
                    shprint(sh.git, 'checkout', self.version)
                    shprint(sh.git, 'submodule', 'update', '--recursive')
        return target


def download_file(url, target, retries=5):
    """
    Download an ``url`` to a ``target``.
    """

    # Download item with multiple attempts (for bad connections):
    attempts = 0
    while True:
        try:
            return download_without_retry(url, target)
        except OSError as e:
            attempts += 1
            if attempts >= retries:
                raise e
            stdout.write('Download failed retrying in a moment...\n')
            stdout.flush()
            time.sleep(3)
            continue
