import re

from html import escape
from urllib.parse import urljoin


OGP_TEMPLATE = """
    <meta property="og:site_name" content="{}" />
    <meta property="og:title" content="{}" />
    <meta property="og:url" content="{}" />
    <meta property="og:description" content="{}" />
    <meta property="og:image" content="" />
    <meta property="twitter:card" content="summary" />
"""


def append_ogp(app, pagename, templatename, ctx, doctree):
    if doctree:
        if ctx["pagename"] == "index":
            page_url = app.config["html_baseurl"]
        else:
            page_url = urljoin(app.config["html_baseurl"], ctx["pagename"])

        if 'posts' in page_url and not page_url.endswith("/"):
            page_url += "/"

        m = re.match(r'<meta content="(.*?)" name="description" />', ctx["metatags"])
        description = m.groups()[0] if m else ""

        site = ctx["docstitle"]
        title = f'{ctx["title"]} — {site}'
        ctx["metatags"] += OGP_TEMPLATE.format(
            escape(site),
            escape(title),
            escape(page_url),
            escape(description),
        )


def setup(app):
    app.connect('html-page-context', append_ogp)
    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
