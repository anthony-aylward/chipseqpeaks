#===============================================================================
# call_peaks.py
#===============================================================================

"""Script to streamline the peak-calling pipeline"""




# Imports ======================================================================

import argparse
import os.path

from chipseqpeaks.chip_seq_peaks import ChIPSeqPeaks, HG38_BLACKLIST_PATH




# Functions ====================================================================

def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            'Pipeline for peak calling'
        )
    )
    io_group = parser.add_argument_group('I/O arguments')
    io_group.add_argument(
        'treatment',
        metavar='<path/to/treatment.bam>',
        help='path to treatment BAM file'
    )
    io_group.add_argument(
        '--output-dir',
        metavar='<path/to/output/dir/>',
        default='.',
        help='path to output directory [.]'
    )
    io_group.add_argument(
        '--control',
        metavar='<path/to/control.bam>',
        help='path to control BAM file'
    )
    io_group.add_argument(
        '--name',
        metavar='<name>',
        help='sample name'
    )

    macs2_group = parser.add_argument_group('MACS2 arguments')
    macs2_group.add_argument(
        '--atac-seq',
        action='store_true',
        help='configure MACS2 for ATAC-seq (--nomodel --shift -100)'
    )
    macs2_group.add_argument(
        '--qvalue',
        metavar='<float>',
        type=float,
        default=0.01,
        help='MACS2 callpeak qvalue cutoff [0.01]'
    )
    macs2_group.add_argument(
        '--broad',
        action='store_true',
        help='Broad peak option for MACS2 callpeak'
    )
    macs2_group.add_argument(
        '--broad-cutoff',
        metavar='<float>',
        type=float,
        default=0.05,
        help='MACS2 callpeak qvalue cutoff for broad regions [0.05]'
    )
    macs2_group.add_argument(
        '--nomodel',
        action='store_true',
        help='use MACS2 with the --nomodel option'
    )
    macs2_group.add_argument(
        '--shift',
        metavar='<int>',
        type=int,
        default=0,
        help='MACS2 shift (use -100 for ATAC-seq) [0]'
    )
    macs2_group.add_argument(
        '--color',
        metavar='<color>',
        default='0,0,0',
        help='Color in R,G,B format to display for genome browser track [0,0,0]'
    )
    
    blacklist_group = parser.add_argument_group('blacklist arguments')
    blacklist_group.add_argument(
        '--remove-blacklisted-peaks',
        action='store_true',
        help='remove blacklisted peaks after calling'
    )
    blacklist_group.add_argument(
        '--blacklist-file',
        metavar='<path/to/blacklist.bed>',
        default=HG38_BLACKLIST_PATH,
        help='path to ENCODE blacklist file '
    )
    blacklist_group.add_argument(
        '--genome',
        choices=('GRCh38', 'hg38', 'GRCh37', 'hg19', 'mm10'),
        default='GRCh38',
        help='genome assembly'
    )

    config_group = parser.add_argument_group('configuration arguments')
    config_group.add_argument(
        '--tmp-dir',
        metavar='<temp/file/dir/>',
        help='directory to use for temporary files'
    )
    args = parser.parse_args()
    if not args.name:
        args.name = os.path.basename(args.treatment).split('.')[0]
    return args


def main():
    args = parse_arguments()
    with open(
        os.path.join(args.output_dir, f'{args.name}.macs2_callpeaks.log'), 'w'
    ) as f:
        cp = ChIPSeqPeaks(
            args.treatment,
            atac_seq=args.atac_seq,
            control_bam=args.control,
            qvalue=args.qvalue,
	        broad=args.broad,
	        broad_cutoff=args.broad_cutoff,
            nomodel=args.nomodel,
            shift=args.shift,
	        log=f,
            temp_file_dir=args.tmp_dir
        )
        if args.remove_blacklisted_peaks:
            cp.remove_blacklisted_peaks(
                blacklist_path=args.blacklist_file,
                genome=args.genome
            )
    with open(
        os.path.join(args.output_dir, f'{args.name}.bdgcmp.log'), 'w'
    ) as g:
        cp.log = g
        if not args.atac_seq:
            cp.bdgcmp()
        cp.write(os.path.join(args.output_dir, args.name))
