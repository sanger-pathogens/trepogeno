# This script is called from the main script of genotreponema
from types import SimpleNamespace as Namespace  
import os
from contextlib import redirect_stdout

#mykrobe functions
from trepogeno.mykrobe.src.mykrobe.cmds.makeprobes import run as run_make_variant_probes

def create_probes(reference_coordinate_filepath, reference_filepath, probe_prefix, kmer_size):
    probe_prefix = str(probe_prefix)
    lineage_path = f"{probe_prefix}.json"
    probes_path = f"{probe_prefix}.fa"

    args = Namespace(
        no_backgrounds=True,
        database=False,
        vcf=None,
        genbank=None,
        text_file=reference_coordinate_filepath,
        kmer=kmer_size,
        lineage=lineage_path, # Mykrobe requries a path to store the lineage json
        reference_filepath=reference_filepath
    )

    # Mykrobe doesn't take the probe path as an argument instead relying on users redirecting standard out with >
    # As such we need to redirect standard out when using the function to the probe path
    os.makedirs(os.path.dirname(probes_path) or ".", exist_ok=True)

    with open(probes_path, "w") as f:
        with redirect_stdout(f):  # Redirects all sys.stdout writes
            run_make_variant_probes(None, args)

