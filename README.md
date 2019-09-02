# chipseqpeaks

A wrapper for MACS2 that abstracts out some things and makes it easier to use.
Thanks due to Joshua Chiou for inspiration and contributions.

> **Warning:** Before using chipseqpeaks, please make sure that one of the
> environment variables TMPDIR, TEMP, or TMP is set to an appropriate path.
> This is the only way to ensure MACS2 writes temporary files to the correct
> location, and failing to do so may cause errors on some systems. (ง •̀_•́)ง

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
