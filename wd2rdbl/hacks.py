import re
from urllib.request import Request, urlopen

from .common import USER_AGENT

COMMONS_FILEPATH_RE = re.compile(
    r"^https?://commons\.wikimedia\.org/wiki/Special:FilePath/(.*?)$"
)

def commons2dataurl(
    url: str, mediatype='text/turtle', user_agent=USER_AGENT
) -> str | None:
    for fname in COMMONS_FILEPATH_RE.findall(url):
        break
    else:
        return None

    url = f"https://commons.wikimedia.org/wiki/File:{fname}"
    req = Request(url, headers={'User-Agent': user_agent})
    with urlopen(req) as f:
        for b in f:
            l = b.decode('UTF-8')
            if '<link' in l and ' rel="alternate"' in l and f' type="{mediatype}"' in l:
                for data_url in re.findall(r'\shref="([^"]+)"', l):
                    return data_url

    return None


if __name__ == '__main__':
    import sys

    for url in sys.argv[1:]:
        eurl = commons2dataurl(url)
        if eurl:
            print(eurl)
