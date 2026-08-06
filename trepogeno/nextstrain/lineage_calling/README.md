This directory contains the scripts that are used for lineage calling using mykrobe and for outputting the sample.json files for each sample containg the call information.

### Argument Example
trepogeno \
--json_directory files/json_outputs \
--genomic_reference files/reference/Treponema_pallidum_subsp_pallidum_SS14_v2.fa \
--probe_and_lineage_dir files/probes \
--seq_manifest /data/nexstrain/manifest.csv \
--lineage_call \
--probe_lineage_name custom_probes

### Output
sample.json (one json for each sample used in calling)

### run time execution:
This script is mostly consists of parsing the manifest matching, getting the probe.fa and lineage.json files and then mocking up a args namespace to supply to the mykrobe call.

## All paramaters 

``` 
--lineage_call (required if you wish to call lineages)
    Used to indicate you wish to call lineages

--json_directory (required)
    A path to the directory for mykrobe to save json files after calling a lineage

--seq_manifest (required)
    A manifest of Sample ID sequences as a CSV, the heading should be ID,Read1,Read2. If you are not using paired end fastqs and only have one Read leave a trailing , e.g. 'ReadID,/fastq/ReadID1.fastq,'

--genomic_reference (required)
    A fasta file that acts as the genomic reference, must match the reference in the type scheme

--probe_and_lineage_dir (required)
    This is the directory in which to save the probe and lineage file during probe creation

--probe_lineage_name (optional if your probe/lineage names were left as the deafult probe.fa and lineage.json)
    The name of the probe.fa and lineage.json files

--kmer_size (optional; Deafult '21'. Must match kmer size in previous create_probes step)
    what kmer size to use when lineage calling, must match what was used when creating probes
```

Further details can be found here:
https://github.com/Mykrobe-tools/mykrobe/wiki/Custom-Panels
https://github.com/Mykrobe-tools/mykrobe/wiki/Custom-Lineage-Calling
