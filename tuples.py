from collections import namedtuple

SummaryInfo = namedtuple('SummaryInfo', ['count', 'text', 'checksum'])

ArchiveLink = namedtuple('ArchiveLink', ['link', 'label'])