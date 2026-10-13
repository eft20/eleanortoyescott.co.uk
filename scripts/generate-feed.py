"""Generate RSS summaries from local post cards on the Writing page."""
from datetime import datetime, timezone
from email.utils import format_datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin
import xml.etree.ElementTree as ET
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://' + (ROOT / 'CNAME').read_text().strip() + '/'

class Posts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.posts, self.post, self.field = [], None, None
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a' and 'post-card' in attrs.get('class', '').split():
            self.post = {'url': attrs['href'], 'title': '', 'date': '', 'summary': ''}
        if self.post is not None:
            if tag == 'h2': self.field = 'title'
            elif tag == 'p': self.field = 'summary'
            elif tag == 'span' and 'post-meta' in attrs.get('class', '').split(): self.field = 'date'
    def handle_data(self, data):
        if self.post is not None and self.field:
            self.post[self.field] += data
    def handle_endtag(self, tag):
        if tag in ('h2', 'p', 'span'): self.field = None
        if tag == 'a' and self.post is not None:
            if self.post['url'].startswith('posts/'):
                self.posts.append(self.post)
            self.post, self.field = None, None

parser = Posts()
parser.feed((ROOT / 'blog/index.html').read_text())
ET.register_namespace('atom', 'http://www.w3.org/2005/Atom')
rss = ET.Element('rss', version='2.0')
channel = ET.SubElement(rss, 'channel')
for name, value in [('title', 'Eleanor Toye Scott — Writing'), ('link', BASE + 'blog/'),
                    ('description', 'Personal essays and writing about climate, education and public life.'),
                    ('language', 'en-gb')]:
    ET.SubElement(channel, name).text = value
ET.SubElement(channel, '{http://www.w3.org/2005/Atom}link', href=BASE+'blog/feed.xml', rel='self', type='application/rss+xml')
posts = sorted(parser.posts, key=lambda p: datetime.strptime(p['date'].strip(), '%d %B %Y'), reverse=True)
for post in posts:
    item = ET.SubElement(channel, 'item')
    url = urljoin(BASE + 'blog/', post['url'])
    date = format_datetime(datetime.strptime(post['date'].strip(), '%d %B %Y').replace(tzinfo=timezone.utc))
    for name, value in [('title', post['title'].strip()), ('link', url), ('description', post['summary'].strip()), ('pubDate', date)]:
        ET.SubElement(item, name).text = value
    ET.SubElement(item, 'guid', isPermaLink='true').text = url
ET.indent(rss, space='  ')
output = ET.tostring(rss, encoding='utf-8', xml_declaration=True) + b'\n'
path = ROOT / 'blog/feed.xml'
if '--check' in sys.argv:
    if not path.exists() or path.read_bytes() != output:
        sys.exit('RSS is out of date. Run python3 scripts/generate-feed.py and commit blog/feed.xml.')
else:
    path.write_bytes(output)
