#!/usr/bin/env python3
#===============================================================================
# chipseqpeaks.py
#===============================================================================

"""Easy management of ChIP-seq peak calling data

A mini-module for managing ChIP-seq peak calling data. The language of this
module treats "ChIP-seq peaks" as an abstraction, but mostly handles them as 
MACS2 output stored in memory.

Example
-------
import chipseqpeaks
with chipseqpeaks.ChipSeqPeaks(<bytes object or path to BAM file>) as cp:
    cp.cleans_up = False
    cp.remove_blacklisted_peaks(<path/to/blacklist.bed>)
    cp.write(<output prefix>)

Classes
-------
ChipSeqPeaks
    object representing ChIP-seq peaks

Functions
---------
parse_input
    check that an input is str or bytes and return the bam file as a bytes
    object
"""




# Imports ======================================================================

import os
import os.path
import shutil
import subprocess
import socket
import sys
import tempfile



# Constants ====================================================================

MACS2_PATH = os.environ.get('MACS2_PATH', shutil.which('macs2'))




# Classes ======================================================================

class ChIPSeqPeaks():
    """ChIP-seq peaks
    
    Attributes
    ----------
    treatment_bam : bytes
        the treatment BAM file
    control_bam : bytes
        the control/input BAM file
    qvalue : float
        --qvalue parameter supplied to MACS2
    nomodel : bool
        if True, MACS2 is run with the --nomodel option [False]
    shift : int
        --shift parameter supplied to MACS2
    broad : bool
        if True, MACS2 is run with the --broad option [False]
    broad_cutoff : float
        --broad-cutoff parameter supplied to MACS2
    log
        file object to which logs will be writtern
    output_extensions : list
        the extensions for MACS2 output files
    """
    
    def __init__(
        self,
        treatment_bam,
        macs2_path=MACS2_PATH,
        atac_seq=False,
        control_bam=None,
        qvalue=0.05,
        nomodel=False,
        shift=0,
        broad=False,
        broad_cutoff=0.1,
        nolambda=False,
        call_summits=False,
        log=None,
        temp_file_dir=None
    ):
        """Collect object attributes and call peaks
        
        Parameters
        ----------
        treatment_bam : bytes
            the treatment BAM file
        atac_seq : bool
            if true, parameter defaults will be configured for ATAC-seq
        control_bam : bytes
            the control/input BAM file
        qvalue : float
            --qvalue parameter supplied to MACS2
        nomodel : bool
            if True, MACS2 is run with the --nomodel option [False]
        shift : int
            --shift parameter supplied to MACS2
        broad : bool
            if True, MACS2 is run with the --broad option [False]
        broad_cutoff : float
            --broad-cutoff parameter supplied to MACS2
        log
            file object to which logs will be writtern
        temp_file_dir
            directory name for temporary files
        """

        if not macs2_path:
            raise MissingMACS2Error(
                '''MACS2 was not found! Please provide the `macs2_path`
                parameter to ChIPSeqPeaks(), or set the `MACS2_PATH`
                environment variable, or make sure `macs2` is installed and
                can be found via the `PATH` environment variable.
                '''
            )
        self.treatment_bam = parse_input(treatment_bam)
        self.macs2_path = macs2_path
        self.control_bam = parse_input(control_bam) if control_bam else None
        self.qvalue = qvalue
        self.nomodel = True if atac_seq and not nomodel else nomodel
        self.shift = -100 if atac_seq and not shift else shift
        self.broad = broad
        self.broad_cutoff = broad_cutoff
        self.nolambda = nolambda
        self.call_summits = call_summits
        self.cleans_up = False
        self.cleanup_prefix = None
        self.log = log
        self.output_extensions = (
            ['peaks.xls', 'peaks.narrowPeak', 'summits.bed', 'treat_pileup.bdg']
            + bool(control_bam) * ['control_lambda.bdg']
            + broad * ['peaks.broadPeak', 'peaks.gappedPeak']
        )
        self.call_peaks(
            sample_name=os.path.basename(treatment_bam)
            temp_file_dir=temp_file_dir,
        )
    
    def __enter__(self):
        """When an instance of this class is used as a context manager, it is
        assumed that files written to disk should be removed after exiting
        context.
        """

        self.cleans_up = True
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Clean up a files on disk"""

        if self.cleans_up:
            for ext in self.output_extensions:
                self.clean_up('{}_{}'.format(self.cleanup_prefix, ext))
        return False
    
    def __repr__(self):
        """Show some of the peak calling parameters"""

        return '\n'.join(
            (
                'ChipPeaks(',
                ')'
            )
        ).format(self)
    
    def call_peaks(self, sample_name: str, temp_file_dir=None):
        """Perform peak calling with MACS2

        Parameters
        ----------
        temp_file_dir : str
            directory name for temporary files
        """

        with tempfile.NamedTemporaryFile(dir=temp_file_dir) as (
            temp_treatment_bam
        ), tempfile.NamedTemporaryFile(dir=temp_file_dir) as (
            temp_control_bam
        ), tempfile.TemporaryDirectory(dir=temp_file_dir) as (
            temp_dir_name
        ):
            temp_treatment_bam.write(self.treatment_bam)
            if self.control_bam:
                temp_control_bam.write(self.control_bam)
            with tempfile.NamedTemporaryFile(
                dir=temp_dir_name
            ) as temp:
                temp_name = temp.name
            subprocess.call(
                (
                    self.macs2_path, 'callpeak',
                    '-B',
                    '--extsize', '200',
                    '--keep-dup', 'all',
                    '--treatment', temp_treatment_bam.name,
                    '--name', sample_name,
                    '--qvalue', str(self.qvalue),
                    '--shift', str(self.shift),
                )
                + bool(self.control_bam) * ('--control', temp_control_bam.name)
                + self.nomodel * ('--nomodel',)
                + self.broad * (
                    '--broad',
                    '--broad-cutoff', str(self.broad_cutoff)
                )
                + self.nolambda * ('--nolambda')
                + self.call_summits * ('--call-summits'),
                stderr=self.log
            )
            for ext in self.output_extensions:
                with subprocess.Popen(
                    ('cat', '{}_{}'.format(temp_name, ext)),
                    stdout=subprocess.PIPE
                ) as cat:
                    output_file, _ = cat.communicate()
                    setattr(self, ext.replace('.', '_'), output_file)
    
    def bdgcmp(self):
        """Create a bedgraph"""

        self.output_extensions.append('ppois.bdg')
        with tempfile.NamedTemporaryFile() as (
            temp_treat_pileup
        ), tempfile.NamedTemporaryFile() as (
            temp_control_lambda
        ), tempfile.TemporaryDirectory() as (
            temp_dir_name
        ):
            temp_treat_pileup.write(self.treat_pileup_bdg)
            temp_control_lambda.write(self.control_lambda_bdg)
            with tempfile.NamedTemporaryFile(
                dir=temp_dir_name
            ) as temp:
                temp_name = temp.name
            subprocess.call(
                (
                    self.macs2_path, 'bdgcmp',
                    '-t', temp_treat_pileup.name,
                    '-c', temp_control_lambda.name,
                    '-m', 'ppois',
                    '--o-prefix', temp_name,
                    '-p', '0.00001'
                ),
                stderr=self.log
            )
            with subprocess.Popen(
                ('cat', '{}_ppois.bdg'.format(temp_name)),
                stdout=subprocess.PIPE
            ) as cat:
                self.ppois_bdg, _ = cat.communicate()
    
    def remove_blacklisted_peaks(self, blacklist_path: str):
        """Remove blacklisted peaks from the peak calls
        
        Parameters
        ----------
        blacklist_path : str
            path to the ENCODE blacklist file
        """

        for peaks in (self.peaks_narrowPeak,) + (
            (self.peaks_broadPeak, self.peaks_gappedPeak) if self.broad else ()
        ): 
            peaks = bedtools_intersect(peaks, blacklist_path, log=self.log)
    
    def write(self, prefix, *extensions):
        """Write MACS2 output to disk
        
        Parameters
        ----------
        prefix
            prefix for output files
        *extensions
            the extensions of the MACS2 output files to write
        """

        for ext in (extensions if extensions else self.output_extensions):
            with open('{}_{}'.format(prefix, ext), 'wb') as f:
                f.write(getattr(self, ext.replace('.', '_')))
        self.cleanup_prefix = prefix
    
    def clean_up(self, path):
        if (os.path.isfile(path) if path else False):
            os.remove(path)




# Exceptions ===================================================================

class Error(Exception):
   """Base class for other exceptions"""

   pass


class BadInputError(Error):
    """Bad input error"""
    
    pass


class MissingMACS2Error(Error):
    """Missing MACS2 error"""
    
    pass




# Functions ====================================================================

def parse_input(input_file):
    """Check that an input is str or byte
    
    Parameters
    ----------
    input_file
        the input to check
    
    Returns
    -------
    bytes
        the input file as a bytes object
    """
    
    if isinstance(input_file, bytes):
        bytes_obj = input_file
    elif isinstance(input_file, str):
        with open(input_file, 'rb') as f:
            bytes_obj = f.read()
    else:
        raise BadInputError('Input must be either str or bytes')
    return bytes_obj


def bedtools_intersect(peaks: bytes, blacklist_path: str, log=None):
    """Apply `bedtools intersect` to a file

    Parameters
    ----------
    peaks : bytes
        BED file containing peaks
    blacklist_path : str
        Path to ENCODE blacklist file
    log
        log file
    
    Returns
    -------
    bytes
        BED file with blacklisted peaks removed
    """

    with subprocess.Popen(
        (
            'bedtools', 'intersect',
            '-a', 'stdin',
            '-b', blacklist_path
            '-v',
        ),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=log
    ) as bedtools_intersect:
        return bedtools_intersect.communicate(input=peaks)[0]
