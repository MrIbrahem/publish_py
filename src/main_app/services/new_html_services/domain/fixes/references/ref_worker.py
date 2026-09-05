"""
Reference quality checking utilities.

Port of ``src/Domain/Fixes/References/RefWorkerFixture.php``. Removes
low-quality/unreliable references (predatory journals, self-published
sources) from wikitext.

See also:
    https://en.wikipedia.org/wiki/Special:AbuseFilter/894
    https://en.wikipedia.org/wiki/Special:AbuseFilter/891
    https://en.wikipedia.org/wiki/Special:AbuseLog/38203012
"""

from __future__ import annotations

import re

from ...parser.citations_parser import get_citations

#: Matches DOIs from known predatory/low-quality publishers.
DOI_LIST = [
    11648,
    1166,
    1234,
    12677,
    12692,
    12720,
    12988,
    13005,
    13172,
    13188,
    14218,
    14257,
    14303,
    14419,
    14445,
    1453,
    14569,
    14662,
    14738,
    15373,
    15406,
    15415,
    15680,
    15761,
    17265,
    18005,
    18052,
    18311,
    18775,
    19030,
    19044,
    19070,
    19080,
    1999,
    20319,
    20431,
    20472,
    20849,
    20902,
    21102,
    21767,
    22158,
    23937,
    2495,
    30845,
    35841,
    36648,
    3844,
    3923,
    3968,
    4018,
    4156,
    4172,
    4236,
    4303,
    5267,
    5296,
    5376,
    5430,
    5455,
    5539,
    5567,
    5580,
    5772,
    5812,
    5815,
    5829,
    5897,
    5899,
    5923,
    5963,
    6007,
    7243,
    7439,
    7537,
    7575,
    7718,
    7763,
    9734,
]

doi_join_pattern = r"|".join(str(x) for x in DOI_LIST)

DOI_PATTERN = re.compile(rf"doi[ ]*?[=\|:][ ]*?10\.({doi_join_pattern})", re.IGNORECASE)

#: Matches domains of known predatory/low-quality open-access journals.
OPEN_ACCESS_JOURNALS_LIST = [
    "academicjournals.com",
    "academicjournals.net",
    "academicjournals.org",
    "academicpub.org",
    "academicresearchjournals.org",
    "aiac.org.au",
    "aicit.org",
    "alliedacademies.org",
    "arcjournals.org",
    "ashdin.com",
    "aspbs.com",
    "avensonline.org",
    "biomedres.info",
    "biopublisher.ca",
    "bowenpublishing.com",
    "ccsenet.org",
    "cennser.org",
    "clinmedjournals.org",
    "cluteinstitute.com",
    "conferenceseries.com",
    "cpinet.info",
    "cscanada.net",
    "davidpublisher.org",
    "etpub.com",
    "eujournal.org",
    "growingscience.com",
    "grdspublishing.org",
    "hanspub.org",
    "hoajonline.com",
    "hrmars.com",
    "iacsit.org",
    "iamure.com",
    ".idosi.org",
    "igi-global.com",
    "iises.net",
    "imedpub.com",
    "informaticsjournals.com",
    "innspub.net",
    "intechopen.com",
    "intechweb.org",
    "interesjournals.org",
    "internationaljournalssrg.org",
    "ispacs.com",
    "ispub.com",
    "julypress.com",
    "juniperpublishers.com",
    "kowsarpub.com",
    "kspjournals.org",
    "longdom.org",
    "m-hikari.com",
    "macrothink.org",
    "mecs-press.org",
    "medcraveonline.com",
    "oapublishinglondon.com",
    "oatext.com",
    "omicsonline.org",
    "ospcindia.org",
    "researchleap.com",
    "sapub.org",
    "scholink.org",
    "scialert.net",
    "scidoc.org",
    "sciencedomain.org",
    "sciencedomains.org",
    "sciedu.ca",
    "sciencepg.com",
    "sciencepub.net",
    "sciencepubco.com",
    "sciencepublication.org",
    "sciencepublishinggroup.com",
    "scipg.net",
    "scipress.com",
    "scirp.org",
    "scopemed.com",
    "sersc.org",
    "sphinxsai.com",
    "scholarpublishing.org",
    ".ssjournals.com",
    "thesai.org",
    "waset.org",
    "witpress.com",
    "worldwidejournals.com",
    "xandhpublishing.com",
    "xiahepublishing.com",
    "zantworldpress.com",
]

OPEN_ACCESS_JOURNALS_PATTERN = re.compile(
    r"(" + "|".join(re.escape(domain) for domain in OPEN_ACCESS_JOURNALS_LIST) + r")",
    re.IGNORECASE,
)

#: Matches known self-publishing services in citation publisher/work fields.
SELFPUB_PATTERN = re.compile(
    r"(publisher|work)\s*[=,:]\s*"
    r"(Author\s*House|CreateSpace|Trafford\s*Publishing|iUniverse\s*|Lulu|"
    r"XLibris|Edwin\s*Mellen\s*Press|Grosvenor\s*House\s*Publishing)",
    re.IGNORECASE,
)

#: Matches domains of known self-publishing services in URLs.
SELFPUB_URL_PATTERN = re.compile(
    r"(authorhouse\.com|createspace\.\w{2,3}|grosvenorhousepublishing\.com|"
    r"iuniverse\.com|lulu\.com|mellenpress\.com|trafford\.com|xlibris\.com)",
    re.IGNORECASE,
)

_BAD_CITATION_PATTERNS = (
    DOI_PATTERN,
    OPEN_ACCESS_JOURNALS_PATTERN,
    SELFPUB_PATTERN,
    SELFPUB_URL_PATTERN,
)


def check_one_cite(cite: str) -> bool:
    """Check whether a citation matches any "bad source" pattern.

    :param cite: The citation text to check.
    :return: True if the citation matches a predatory/self-published
        pattern (and should be removed), False otherwise.
    """
    cite_d = cite
    for pattern in _BAD_CITATION_PATTERNS:
        cite_d = pattern.sub("", cite_d)

    return cite != cite_d


def remove_bad_refs(text: str) -> str:
    """Remove bad (predatory/self-published) references from text.

    :param text: The text containing references to check and potentially remove.
    :return: The text with bad references removed.
    """
    for citation in get_citations(text):
        citation_tag = citation.tag
        if check_one_cite(citation_tag):
            text = text.replace(citation_tag, "")

    return text


__all__ = [
    "check_one_cite",
    "remove_bad_refs",
]
