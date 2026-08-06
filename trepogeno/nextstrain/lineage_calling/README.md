This directory contains the scripts that are used for lineage calling using mykrobe and for outputting the sample.json files for each sample containing the call information.

### Argument Example
```
trepogeno \
--json_directory files/json_outputs \
--probe_prefix files/probes/custom_probes \
--seq_manifest /data/nexstrain/manifest.csv \
--lineage_call
```

Or, to call a single sample directly without a manifest:
```
trepogeno \
--json_directory files/json_outputs \
--probe_prefix files/probes/custom_probes \
--read1 /data/nexstrain/sample_1.fastq.gz \
--read2 /data/nexstrain/sample_2.fastq.gz \
--sample_id sample_name \
--lineage_call
```

### Output
sample.json (one json for each sample used in calling)

### run time execution:
This script mostly consists of parsing the manifest, matching sample IDs to their reads, retrieving the probe.fa and lineage.json files, and then mocking up an args namespace to supply to the mykrobe call.

## All parameters 

``` 
--lineage_call (required if you wish to call lineages)
    Used to indicate you wish to call lineages

--json_directory (required)
    A path to the directory for mykrobe to save JSON files after calling a lineage

--seq_manifest (required, unless using --read1)
    A manifest of Sample ID sequences as a CSV, the heading should be ID,Read1,Read2. If you are not using paired-end fastqs and only have one read, leave a trailing comma, e.g. 'ReadID,/fastq/ReadID1.fastq,'

--read1 (required, unless using --seq_manifest)
    Path to a fastq file to call a single sample directly, instead of via a manifest. Alternative to --seq_manifest; provide either one or the other, not both.

--read2 (optional)
    Path to the second fastq of a pair, if using --read1. Omit for single-end reads.

--sample_id (required if using --read1)
    Sample ID to use when calling a single sample directly with --read1/--read2.

--probe_prefix (optional; Default './probes')
    Path prefix (without extension) of the probe.fa and lineage.json files to read, e.g. files/probes/custom_probes reads files/probes/custom_probes.fa and files/probes/custom_probes.json. The kmer size is read automatically from the probe file, so it does not need to be supplied here and cannot drift from what was used at probe-creation time.
```

Further details can be found here:
https://github.com/Mykrobe-tools/mykrobe/wiki/Custom-Panels
https://github.com/Mykrobe-tools/mykrobe/wiki/Custom-Lineage-Calling
