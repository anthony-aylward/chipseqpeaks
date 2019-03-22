# chipseqpeaks

A wrapper for MACS2 that abstracts out some things and makes it easier to use.
Thanks due to Joshua Chiou for inspiration and contributions.

## Installation

```sh
pip3 install chipseqpeaks
```

or

```sh
pip3 install --user chipseqpeaks
```

## Example API usage
```python
from chipseqpeaks import ChIPSeqPeaks
with ChIPSeqPeaks(<bytes object or path to BAM file>) as cp:
    cp.cleans_up = False
    cp.remove_blacklisted_peaks(<path/to/blacklist.bed>)
    cp.write(<output prefix>)
```

## Example command line usage

For help text, see:
```sh
chipseqpeaks-call -h
```
For ChIP-seq:
```sh
chipseqpeaks-call --control input.bam chip.bam
```

For ATAC-seq:
```sh
chipseqpeaks-call --atac-seq atac.bam
```
