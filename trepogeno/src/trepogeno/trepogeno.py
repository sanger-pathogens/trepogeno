import argparse
from pathlib import Path
import logging
import sys

# Dynamically add mykrobe source to sys.path
#This is to make importing funcitons from the mykrobe submodule easier
mykrobe_src = Path(__file__).resolve().parent / "mykrobe" / "src"
if mykrobe_src.exists():
    sys.path.insert(0, str(mykrobe_src))
else:
    raise ImportError(f"Expected mykrobe src at {mykrobe_src}, but it was not found.")


#Custom functions, these import functions from other script to keep things modular
from trepogeno.post_process_json.tabulate_json import run_tabulate_json
from trepogeno.post_process_json.summarise_trepogeno_lineage_calls import run_summarise_lineage_calls
from trepogeno.create_probes.create_probes import create_probes
from trepogeno.lineage_calling.run_mykrobe_lineage_calling import run_mykrobe_lineage_call

def positive_int(value):
    try:
        ivalue = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"kmer_size must be an integer, got '{value}'")
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(f"kmer_size must be a positive integer, got '{value}'")
    return ivalue

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="script to summarise lineage calls across output json's from mykrobe"
    )
    parser.add_argument(
        "--json_directory",
        help="Path to the directory in which to save and read the mykrobe .json files",
        type=Path
    )

    parser.add_argument(
        "--make_probes",
        help="Provide this flag if you want to create a new set of probes before running the lineage calling",
        action="store_true",
    )

    parser.add_argument(
        "--tabulate_jsons",
        help="Provide this flag to if you want to tabulate the json outputs produced by mykrobe",
        action="store_true",
    )

    parser.add_argument(
        "--lineage_call",
        help="Provide this flag to preform the custom lineage calling with mykrobe",
        action="store_true",
    )

    parser.add_argument(
        "--type_scheme",
        help="The reference coordinate file mapping snps and lineages to genomic positions",
        type=Path
    )

    parser.add_argument(
        "--genomic_reference",
        help="The path to the genomic reference fasta",
        type=Path
    )

    parser.add_argument(
        "--kmer_size",
        help="The kmer size to use when creating probes with --make_probes, defaults to 21. Not needed for --lineage_call, the kmer size is inferred automatically from the probe file.",
        type=positive_int,
        default=21,
    )

    parser.add_argument(
        "--seq_manifest",
        help="A manifest of Sample ID sequences as a CSV, the heading should be ID,Read1,Read2. Alternative to --read1/--read2 for calling a single sample directly.",
        type=Path,
    )

    parser.add_argument(
        "--read1",
        help="Path to a fastq file to call a single sample directly, instead of via --seq_manifest. Requires --sample_id.",
        type=Path,
    )

    parser.add_argument(
        "--read2",
        help="Path to the second fastq of a pair, if using --read1. Optional, omit for single-end reads.",
        type=Path,
    )

    parser.add_argument(
        "--sample_id",
        help="Sample ID to use when calling a single sample directly with --read1/--read2.",
    )

    parser.add_argument(
        "--probe_prefix",
        help="Path prefix (without extension) for the probe and lineage files, e.g. files/probes/custom writes/reads files/probes/custom.fa and files/probes/custom.json. Defaults to ./probes",
        type=Path,
        default=Path("./probes"),
    )

    args = parser.parse_args()

    if not (args.make_probes or args.lineage_call or args.tabulate_jsons):
        parser.error("No action specified: provide at least one of --make_probes, --lineage_call, --tabulate_jsons")

    if  args.tabulate_jsons and args.json_directory is None:
        parser.error("The json_directory was not found or provided correctly for processing!")

    #Ensure arguments are correctly provided some operating modes require other arguments to be set
    if args.make_probes:
        if not args.type_scheme:
            parser.error("The typing scheme was not provided but is required for making probes")
        elif not args.type_scheme.exists():
            parser.error(f"--type_scheme file not found: {args.type_scheme}")

        if not args.genomic_reference:
            parser.error("The genomic reference was not provided but is required for making probes")
        elif not args.genomic_reference.exists():
            parser.error(f"--genomic_reference file not found: {args.genomic_reference}")

    if args.lineage_call:
        if args.seq_manifest and args.read1:
            parser.error("Provide either --seq_manifest or --read1, not both")
        if not args.seq_manifest and not args.read1:
            parser.error("Either --seq_manifest or --read1 must be provided for calling lineages")
        if args.read1 and not args.sample_id:
            parser.error("--sample_id is required when calling a single sample directly with --read1")
        if args.seq_manifest and not args.seq_manifest.exists():
            parser.error(f"--seq_manifest file not found: {args.seq_manifest}")
        if args.read1 and not args.read1.exists():
            parser.error(f"--read1 file not found: {args.read1}")
        if args.read2 and not args.read2.exists():
            parser.error(f"--read2 file not found: {args.read2}")
        if not args.json_directory:
            parser.error("A direcory to store jsons was not provided but is required for calling lineages")

        probe_fasta = Path(f"{args.probe_prefix}.fa")
        probe_lineage_json = Path(f"{args.probe_prefix}.json")
        if not probe_fasta.exists():
            parser.error(f"Probe file not found: {probe_fasta}")
        if not probe_lineage_json.exists():
            parser.error(f"Lineage file not found: {probe_lineage_json}")
    return args

def create_probes_from_type_scheme(type_scheme,genomic_reference,probe_prefix,kmer_size):
    create_probes(type_scheme,genomic_reference,probe_prefix,kmer_size)

def run_lineage_call(probe_prefix,json_directory,sequence_manifest=None,sample_id=None,read1=None,read2=None):
    run_mykrobe_lineage_call(probe_prefix,json_directory,sequence_manifest=sequence_manifest,sample_id=sample_id,read1=read1,read2=read2)

def concatenate_and_read_json(json_directory, type_scheme=None):
    run_tabulate_json(json_directory)
    run_summarise_lineage_calls(json_directory, scheme_tsv=type_scheme)

def main():
    args = parse_arguments()

    if args.make_probes:
        create_probes_from_type_scheme( args.type_scheme, args.genomic_reference, args.probe_prefix, args.kmer_size)

    if args.lineage_call:
        run_lineage_call(args.probe_prefix,args.json_directory,sequence_manifest=args.seq_manifest,sample_id=args.sample_id,read1=args.read1,read2=args.read2)

    if args.tabulate_jsons:
        concatenate_and_read_json(args.json_directory, args.type_scheme)

if __name__ == "__main__":
    main()
