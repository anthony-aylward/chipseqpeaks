"""A wrapper for MACS2 that abstracts out some things and makes it easier to use

Blacklist data source: https://www.encodeproject.org/annotations/ENCSR636HFF/

Example
-------
from chipseqpeaks import ChIPSeqPeaks
with ChIPSeqPeaks(<bytes object or path to BAM file>) as cp:
    cp.cleans_up = False
    cp.remove_blacklisted_peaks(<path/to/blacklist.bed>)
    cp.write(<output prefix>)

Classes
-------
ChIPSeqPeaks
    object representing ChIP-seq peaks
"""

from chipseqpeaks.chip_seq_peaks import (
    ChIPSeqPeaks, MACS2_PATH, BEDTOOLS_PATH, HG38_BLACKLIST_PATH,
    HG19_BLACKLIST_PATH, MM10_BLACKLIST_PATH
)