from types import SimpleNamespace as Namespace
from  trepogeno.mykrobe.src.mykrobe.cmds.amr import run as run_lineage_call
from collections import Counter
import os

def check_lineage_file(json_directory,):
    os.makedirs(json_directory, exist_ok=True)


def infer_kmer_size_from_probes(probe_fasta_path):
    """Probe length is (2*kmer - 1), not kmer itself, so back it out from the most common probe length in the file."""
    lengths = Counter()
    sequence_length = 0
    started = False
    with open(probe_fasta_path) as fasta:
        for line in fasta:
            line = line.strip()
            if line.startswith(">"):
                if started and sequence_length:
                    lengths[sequence_length] += 1
                sequence_length = 0
                started = True
                continue
            if started:
                sequence_length += len(line)
    if started and sequence_length:
        lengths[sequence_length] += 1

    if not lengths:
        raise ValueError(f"Could not determine kmer size: no sequence found in {probe_fasta_path}")

    most_common_probe_length = lengths.most_common(1)[0][0]
    return (most_common_probe_length + 1) // 2


def call_single_sample(sample_id, sequences, probe_path, lineage_path, kmer_size, json_directory):
    #Mykrobe has many different arguments captured from the user, we mockup this namespace below so we can use it in our function call
    args = Namespace(
        custom_probe_set_path=probe_path,
        custom_lineage_json=lineage_path,
        species="custom",
        report_all_calls=True,
        sample=sample_id,
        output_format="json",
        output=f"{json_directory}/{sample_id}.json",
        seq=sequences,
        kmer=kmer_size,

        tmp=None, #This tmp variable and below are the defaults used when running lineage calling although most are never used
        ont=False,
        force=False, # Must add argument to override
        threads=2, # Must add argument to override
        skeleton_dir="mykrobe/data/skeletons/",
        memory="2GB", # Must add argument to override
        filters=['MISSING_WT', 'LOW_PERCENT_COVERAGE', 'LOW_GT_CONF', 'LOW_TOTAL_DEPTH'],
        min_variant_conf=150,
        min_gene_conf=1,
        model="kmer_count",
        min_proportion_expected_depth=0.3,
        ploidy=None, # This is only in use if using args.ONT is set (would otherwise be set to diploid by defualt)
        conf_percent_cutoff=100,
        min_depth=1,
        ignore_minor_calls=False,
        keep_tmp=False,# Must add argument to override
        ncbi_names=None,
        custom_variant_to_resistance_json=None,
        expected_error_rate=0.05,
        guess_sequence_method=False,
        ctx=None,
        ignore_filtered=False,
        dump_species_covgs=None,
        min_gene_percent_covg_threshold=100
    )

    run_lineage_call(None, args) #Runs the function imported from mykrobe, the first variable is unused in the function the second contains our mocked arguments


def run_mykrobe_lineage_call(probe_prefix, json_directory, sequence_manifest=None, sample_id=None, read1=None, read2=None):
    check_lineage_file(json_directory)

    probe_path = f"{probe_prefix}.fa"
    lineage_path = f"{probe_prefix}.json"
    kmer_size = infer_kmer_size_from_probes(probe_path)

    if sequence_manifest:
        with open(sequence_manifest, "r") as manifest: #This is loop is for parsing a manifest with the structure ID,Read1,Read2
            next(manifest)  # Skip header line
            for line in manifest: # For each new unique sample
                if not line.strip():
                    continue  # Skip empty lines
                if line.startswith("#"): # Skip comments
                      continue

                ID, sequence1, sequence2 = line.strip().split(",") #Get each part
                sequences = [sequence1]
                if sequence2: #The fastq does not have to be paired if it in't we can continute with the first fastq (validation of the file suffix should be added)
                    sequences.append(sequence2)

                call_single_sample(ID, sequences, probe_path, lineage_path, kmer_size, json_directory)
    else:
        sequences = [str(read1)]
        if read2:
            sequences.append(str(read2))

        call_single_sample(sample_id, sequences, probe_path, lineage_path, kmer_size, json_directory)