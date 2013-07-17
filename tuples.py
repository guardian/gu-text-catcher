from collections import namedtuple

SummaryInfo = namedtuple('SummaryInfo', ['count', 'text', 'checksum', 'length'])

ArchiveLink = namedtuple('ArchiveLink', ['link', 'label'])