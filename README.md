<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/trepogeno-logo-dark.svg">
    <img alt="trepogeno" src="assets/trepogeno-logo-light.svg" width="420">
  </picture>
</p>

# Trepogeno

This repo contains scripts that wrap around mykrobe for the lineage calling of *Treponema pallidum* strains.
The tool, named trepogeno, can be installed as a system-wide package with the below instructions:

To set up the tool you must first:
```
git clone --recursive https://gitlab.internal.sanger.ac.uk/sanger-pathogens/trepogeno.git
cd trepogeno/trepogeno
```

Create a conda environment with python 3.8 and install trepogeno into it:
```
conda create -n trepogeno python=3.8
conda activate trepogeno
pip3 install -e .
```

Next, to ensure the mccortex binaries for mykrobe compile correctly:

```
cd src/trepogeno/mykrobe
git clone --recursive -b geno_kmer_count https://github.com/Mykrobe-tools/mccortex mccortex
cd mccortex
make
cp bin/mccortex31 ../src/mykrobe/cortex
```

Confirm the install worked:
```
trepogeno --help
```

## trepogeno
This is the main script; once installed system-wide as detailed above, it can be called from anywhere with `trepogeno --argument 1`

## create_typing_scheme
The `deprecated/old_create_typing_scheme` subdirectory contains scripts relating to creating a typing scheme through use of rPinecone, a VCF, and a reference.
These scripts are deprecated and not used in normal execution of the tool.

## Create probe and lineage files
To create a probe and lineage file, which is required for lineage calling, you need a typing scheme and genomic reference.
For more information on creating a typing scheme, refer to the typing scheme rule book in the trepogeno directory (trepogeno/README.md).

```
trepogeno \
--json_directory files/json_outputs \
--type_scheme data/2026-05-12__07_masked_snpsAF09DP5_n10.diagnostic_SNPs_Mykrobe_2026-08-04_b.tsv \
--genomic_reference data/Treponema_pallidum_subsp_pallidum_SS14_v2.fa \
--probe_prefix files/probes/custom_probe_name \
--make_probes
```

## Lineage calling
You need the lineage and probe files made by mykrobe, and either a manifest containing paths to the reads you want called, or a single --read1/--read2 pair.

```
trepogeno \
--json_directory files/json_outputs \
--probe_prefix files/probes/custom_probe_name \
--seq_manifest /data/nexstrain/manifest.csv \
--lineage_call
```

Or, to call a single sample directly without a manifest:
```
trepogeno \
--json_directory files/json_outputs \
--probe_prefix files/probes/custom_probe_name \
--read1 /data/nexstrain/sample_1.fastq.gz \
--read2 /data/nexstrain/sample_2.fastq.gz \
--sample_id sample_name \
--lineage_call
```

## Process and summarise the mykrobe json outputs
You need to supply the path to the directory containing the mykrobe output JSON files.

```
trepogeno \
--json_directory files/json_outputs \
--tabulate_jsons
```

## Example full run execution

```
trepogeno \
--json_directory files/json_outputs \
--type_scheme data/2026-05-12__07_masked_snpsAF09DP5_n10.diagnostic_SNPs_Mykrobe_2026-08-04_b.tsv \
--genomic_reference data/Treponema_pallidum_subsp_pallidum_SS14_v2.fa \
--probe_prefix files/probes/custom_probes \
--make_probes \
--seq_manifest /data/nexstrain/manifest.csv \
--tabulate_jsons \
--lineage_call
```

## All parameters

```
Make Probes
-----------
--make_probes   
    Used to indicate you wish to generate a new set of probes during the work flow

--type_scheme   
    Path to the file that maps SNPs to specific genomic coordinates and lineages, to learn more review mykrobe's custom lineage calling documentation.

--genomic_reference 
    A FASTA file that acts as the genomic reference; must match the reference used in the typing scheme

--probe_prefix
    Path prefix (without extension) for the probe and lineage files to write, e.g. files/probes/custom writes files/probes/custom.fa and files/probes/custom.json. Defaults to ./probes

--kmer_size 
    what kmer size to use when creating the probes. defaults to 21

Lineage Calling
-----------
--lineage_call  
    Used to indicate you wish to execute the lineage calling workflow

--json_directory    
    A path to the directory for mykrobe to save its JSON files after calling a lineage. These will be named based on the ID supplied in the manifest, e.g. SRR567232.json

--seq_manifest (required, unless using --read1)
    A manifest of Sample ID and sequences, the heading should be ID,Read1,Read2. If you are not using paired-end fastqs and only have one read, leave a trailing comma, e.g. 'ReadID,/fastq/ReadID1.fastq,'

--read1 (required, unless using --seq_manifest)
    Path to a fastq file to call a single sample directly, instead of via a manifest. Provide either --seq_manifest or --read1, not both.

--read2 (optional)
    Path to the second fastq of a pair, if using --read1. Omit for single-end reads.

--sample_id (required if using --read1)
    Sample ID to use when calling a single sample directly with --read1/--read2.

--probe_prefix
    Path prefix (without extension) of the probe.fa and lineage.json files to read, e.g. files/probes/custom reads files/probes/custom.fa and files/probes/custom.json. Defaults to ./probes. The kmer size used is read automatically from the probe file, so it does not need to be supplied separately.

Json Processing
-----------
--tabulate_jsons    
    Used to indicate you wish to execute the workflow to tabulate the output from mykrobe

--json_directory    
    Supply a path to the directory containing mykrobe summary JSON files; these should be in the format mykrobe uses when `--report_all_calls` is used in mykrobe (the default if you only use trepogeno)
```



### Tool Overview
![Trepogeno_pipline](images_examples/pipeline-flow.png)
