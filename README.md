<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/trepogeno-logo-dark.svg">
    <img alt="trepogeno" src="assets/trepogeno-logo-light.svg" width="420">
  </picture>
</p>

`trepogeno` is a molecular typing scheme and tool for classifying *Treponema pallidum* genomic data.

## Overview
Most genomic data available for *Treponema pallidum* was generated directly from clinical specimens using hybrid capture enriched metagenomic sequencing methods. Sequencing depth is typically low and uneven, such that standard assembly methods often produce low quality assemblies. 

Although molecular typing tools exist for *T. pallidum* (e.g. Multilocus sequence typing schemes; MLST), the clusters assigned are not always consistent with whole genome phylogeny. Moreover, typing methods such as MLST require recovery of complete locus sequences which is often not possible from *T. pallidum* assemblies (which may contain contig breaks or low quality base calls within target regions, even if the base present is the reference allele). A hierarchical SNP based typing scheme (based on the [GenoTyphi](https://github.com/typhoidgenomics/genotyphi) model) that requires only specific SNPs to be detected may therefore enable more consistent and robust typing from genomic data. 

### Hierarchical SNP types
As part of the *T. pallidum* NextStrain project, we used an initial dataset of 2313 genomes to delineate clusters at three hierarchical levels using [fastBAPS](https://github.com/gtonkinhill/fastbaps).

- Level 1 corresponds to the *T. pallidum* subspecies *pallidum* (TPA), *pertenue* (TPE), and *endemicum* (TEN). An additional group of genomes corresponding to outliers recovered from ancient DNA was left unclassified (Other).

- Level 2 corresponds to deep branches in the phylogeny, e.g. SS14 (TPA-1) and Nichols (TPA-2) lineages within TPA. Similarly deep branching lineages were observed within TPE. Numerical designations are applied to each group (largest group at each hierarchical level first).

- Level 3 corresponds to sublineages closer to the tips. Since these were defined using BAPS, these are not uniformly diverse, and represent statistically robust genetic groups but not necessarily epidemiologically robust groups. Note that these clusters are generally more genetically diverse than those defined using SNP thresholds (e.g. [Beale 2021](https://www.nature.com/articles/s41564-021-01000-z)).

![Figure_1_full_phylogeny](assets/p.full.pyjar.tree_plot_lineages_2026-08-13.svg)

<p align="center"><sub><i>Whole genome phylogeny of 2313 T. pallidum genomes, showing <code>trepogeno</code> hierarchical lineages.</i></sub></p>


<br>

![Figure_2_collapsed_phylogeny](assets/p.collapsed.pyjar.tree_plot_highlights_barh_2026-08-13.svg)

<p align="center"><sub><i>Collapsed phylogeny showing relationships between hierarchical clusters. Bar plots show genome counts for each sublineage.</i></sub></p>

<br>

### Discriminatory SNP typing
After defining hierarchical lineages, we identified highly discriminatory SNPs delineating the phylogenetic branches of each lineage and sublineage. Genomes containing these SNPs can thus be classified into the hierarchical scheme.


`trepogeno` wraps around and builds upon the well established tool [Mykrobe](https://github.com/Mykrobe-tools/mykrobe), and detects discriminatory SNPs to facilitate lineage calling of *Treponema pallidum* strains directly from sequencing reads. It can be installed as per the below instructions.

<br>

## Installation
### From source code
Note: this requires a way of creating an environment (e.g. conda, mamba) and a way to compile C (for macOS/Ubuntu: clang or gcc and make, Ubuntu will further require zlib1g-dev).

First clone the repository and its Mykrobe submodule:
```
git clone --recurse-submodules https://github.com/sanger-pathogens/trepogeno.git
cd trepogeno/trepogeno
```

Create an environment with Python 3.8 and install the dependencies defined in the pyproject.toml into it, for example with `conda`:
```
conda create -n trepogeno python=3.8
conda activate trepogeno
pip3 install -e .
```

Next, to ensure the McCortex binaries for Mykrobe compile correctly clone from the `geno_kmer_count` branch as below:

```
cd src/trepogeno/mykrobe
git clone --recurse-submodules -b geno_kmer_count https://github.com/Mykrobe-tools/mccortex mccortex
cd mccortex
make
cp bin/mccortex31 ../src/mykrobe/cortex
```

The trepogeno command should now be executable from anywhere, as long as the environment the dependencies are installed into is _activated_. You may check the installation by the help message:
```
trepogeno --help
```

## Usage
### Create typing scheme (deprecated)
The `deprecated/old_create_typing_scheme` subdirectory contains scripts relating to creating a typing scheme through use of rPinecone, a VCF, and a reference.
These scripts are deprecated and not used in normal execution of the tool.

### Create probe and lineage files
To create a probe and lineage file, required for lineage calling, you need a typing scheme and genomic reference.
For more information on creating a typing scheme, refer to the [Typing Scheme Guide](./docs/typing_scheme_guide.md).


Example command:
```
trepogeno \
--json_directory files/json_outputs \
--type_scheme data/2026-05-12__07_masked_snpsAF09DP5_n10.diagnostic_SNPs_Mykrobe_2026-08-04_b.tsv \
--genomic_reference data/Treponema_pallidum_subsp_pallidum_SS14_v2.fa \
--probe_prefix files/probes/custom_probe_name \
--make_probes
```
Expected outputs:
- custom_typing.fa
- custom_typing.json

### Lineage calling
You will need the lineage and probe files made by Mykrobe, and either a manifest containing paths to the reads you want called, or a single --read1/--read2 pair.

Example manifest with two query inputs:
```
ID,R1,R2
sampleA,/data/sampleA_1.fastq.gz,/data/sampleA_2.fastq.gz
sampleB,/data/sampleB_1.fastq.gz,/data/sampleB_2.fastq.gz
```

Example commands:
```
trepogeno \
--json_directory files/json_outputs \
--probe_prefix files/probes/custom_probe_name \
--seq_manifest /data/manifest.csv \
--lineage_call
```

Or, to call a single sample directly without a manifest:
```
trepogeno \
--json_directory files/json_outputs \
--probe_prefix files/probes/custom_probe_name \
--read1 /data/sample_1.fastq.gz \
--read2 /data/sample_2.fastq.gz \
--sample_id sample_name \
--lineage_call
```

Expected outputs:
- sample.json (one per sample)

### Process and summarise the Mykrobe outputs
You need to supply the path to the directory containing the Mykrobe output JSON files.

```
trepogeno \
--json_directory files/json_outputs \
--tabulate_jsons
```

### Example full run execution

```
trepogeno \
--json_directory files/json_outputs \
--type_scheme data/2026-05-12__07_masked_snpsAF09DP5_n10.diagnostic_SNPs_Mykrobe_2026-08-04_b.tsv \
--genomic_reference data/Treponema_pallidum_subsp_pallidum_SS14_v2.fa \
--probe_prefix files/probes/custom_probes \
--make_probes \
--seq_manifest /data/manifest.csv \
--tabulate_jsons \
--lineage_call
```

## Parameters

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
    A 3-column comma-separated value (CSV) table file of Sample ID, path to read 1 and path to read 2, with header. If using single-end reads, leave a trailing comma, e.g. 'ReadID,/fastq/ReadID1.fastq,'

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

### Schematic Overview
![Trepogeno_pipline](assets/pipeline-flow.png)

<br>

## Results
The JSON files contain detailed information about each SNP called for each sample tested. When using `--tabulate_jsons`, several summary files are produced which summarise findings across all JSON files provided. 

`lineage_call_summary.csv`

| sample | called_lineage | n_called_lineages | all_called_lineages | primary_path_concordance | flag_reason | sublineage_resolved | path_support | node_scores | terminal_use_ref_allele | terminal_n_markers | terminal_n_concordant | terminal_n_het | terminal_n_discordant | terminal_node_concordance | terminal_mean_conf | terminal_min_conf | terminal_conf_qual | genome_depth |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ERR5210584 | TPA.1.6 | 1 | TPA.1.6(1.0) | 1.0 | | yes | 3/3 | TPA=1;TPA.1=1;TPA.1.6=1 | False | 1 | 1 | 0 | 0 | 1.0 | 24524 | 24524 | high | 226 |
| ERR13170795 | TPA.1.6 | 1 | TPA.1.6(1.0) | 1.0 | | yes | 3/3 | TPA=1;TPA.1=1;TPA.1.6=1 | False | 1 | 1 | 0 | 0 | 1.0 | 87315 | 87315 | high | 457 |

### Interpreting the output
Both samples above were called as **TPA.1.6** with full confidence: `primary_path_concordance` is `1.0` (every marker along the called path was concordant with the expected allele), `sublineage_resolved` is `yes` (the call reached a genuine terminal leaf rather than stopping at an internal node with an unresolved sub-lineage), and `terminal_conf_qual` is `high`, backed by strong per-marker evidence (`terminal_min_conf` in the tens of thousands). `flag_reason` is empty for both (low coverage or anomalous SNPs would lead to a flag here).

A weaker or more ambiguous call would look different: `flag_reason` may show `low_node_concordance` (the terminal call rests on a minority of its markers, e.g. via a shared/homoplasic SNP) or `low_conf` (weak overall evidence, e.g. a single marker at low sequencing depth). For ambiguous or uncertain calls, `called_lineage` is prefixed with `*`. `all_called_lineages` lists every lineage mykrobe found any support for, each with its own `path_concordance` score in parentheses — this may be useful for spotting cases where a sample matches more than one path.


## Scheme Updates
We anticipate that as new genomes are published, new sublineages may need to be designated. Substantially divergent phylogenetic outliers will be identified through community maintenance of the Nextstrain build, and will be discussed before designated a new lineage or sublineage. Updated schemes will be made available. The latest can be downloaded [here](https://raw.githubusercontent.com/sanger-pathogens/trepogeno/main/data/scheme_updates/Trepogeno_scheme_build_2026-08-04.tar.gz).