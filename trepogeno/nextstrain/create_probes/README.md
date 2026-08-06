This directory contains the scripts that are used for making calls to mykrobe and for outputting the probe and taxonomy files that are latter used for lineage calling.

### Argument Example
trepogeno \
--json_directory files/json_outputs \
--type_scheme files/2026-05-12__07_masked_snpsAF09DP5_n10.diagnostic_SNPs_Mykrobe_2026-08-04_b.tsv \
--genomic_reference files/reference/Treponema_pallidum_subsp_pallidum_SS14_v2.fa \
--probe_prefix files/probes/custom_typing \
--make_probes

### Output
custom_typing.fa
custom_typing.json


### run time execution:
This script is very simple and mosly consists of importing the requried function from mykrobe and executing it with our own captured arguments.
There is a little juggling with the probe.fa file as mykrobe doesn't take the probe name as a argument instead making users redirect standard out with > and saving to the current directory
Instead we use redirect_stdout from contextlib to save to a file and can then save the lineage.json and probe.fa to where ever the use supplied

## All paramaters 

``` 
-----------
--make_probes (required if you want to make probes)
    Used to indicate you wish to generate a new set of probes during the work flow

--type_scheme (required)
    Path to the file that maps snps to specific genomic coordiantes and lineages, to learn more review the mykrobe custom lineage calling documentation.

--genomic_reference (required)
    Path to a fasta file that acts as the genomic reference, must match the reference used in the typing scheme

--probe_prefix (optional; Deafult './probes')
    Path prefix (without extension) for the probe.fa and lineage.json files to write, e.g. files/probes/custom_typing writes files/probes/custom_typing.fa and files/probes/custom_typing.json

--kmer_size (optional; Deafult '21')
    what kmer size to use when creating the probes
```

Further details can be found here:
https://github.com/Mykrobe-tools/mykrobe/wiki/Custom-Panels
https://github.com/Mykrobe-tools/mykrobe/wiki/Custom-Lineage-Calling
