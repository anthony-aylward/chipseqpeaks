# chipseqpeaks

Easy management of ChIP-seq peak calling data

A mini-module for managing ChIP-seq peak calling data. The language of this
module treats "ChIP-seq peaks" as an abstraction, but mostly handles them as 
MACS2 output stored in memory.

```
Example
-------
import chipseqpeaks
with chipseqpeaks.ChIPSeqPeaks(<bytes object or path to BAM file>) as cp:
    cp.cleans_up = False
    cp.remove_blacklisted_peaks(<path/to/blacklist.bed>)
    cp.write(<output prefix>)

Classes
-------
ChIPSeqPeaks
    object representing ChIP-seq peaks

Functions
---------
parse_input
    check that an input is str or bytes and return the bam file as a bytes
    object
```