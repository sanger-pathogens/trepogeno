This repo contains scripts that intend to wrap around mykrobe for the lineage calling of treponema strains.
The tool, currently nicknamed trepogeno, can be installed as a system wide package with the below instructions:

To set up functionality you must first: 
1. git clone --recursive https://gitlab.internal.sanger.ac.uk/sanger-pathogens/nextstrain.git
2. cd nextstrain/trepogeno/
3. pip3 install -e . 

Next to ensure mccortex binaries for mykrobe complie correctly

1. cd mykrobe
2. git clone --recursive -b geno_kmer_count https://github.com/Mykrobe-tools/mccortex mccortex
3. cd mccortex
4. make
5. cp bin/mccortex31 ../src/mykrobe/cortex

## Trepogeno.py
This is the main script, once installed system wide as detailed above can be called anywhere with `trepogeno --agrument 1` 

## create_typing_scheme
This subdirectory contains scripts relating to creating a typing scheme through use of Rpinecone, a vcf, and a reference.
These scripts are deprectated and not used in normal execution of the tool.

## Create probes lineage files
To create a probe and lineage file, which is requried for lineage calling, you need a typing scheme and genomic reference.
For more information of creating a typing scheme refer to the typing scheme rule book in the trepogeno directory.

trepogeno \\    
--json_directory files/json_outputs \\  
--type_scheme files/2026-05-12__07_masked_snpsAF09DP5_n10.diagnostic_SNPs_Mykrobe_2026-08-04_b.tsv \\   
--genomic_reference files/reference/Treponema_pallidum_subsp_pallidum_SS14_v2.fa \\  
--probe_prefix files/probes/custom_probe_name \\     
--make_probes

## Lineage calling
Required are the lineage and probe files made by mykrobe, and a manifest containing paths to the reads you want called.

trepogeno \\    
--json_directory files/json_outputs \\  
--probe_prefix files/probes/custom_probe_name \\     
--seq_manifest /data/nexstrain/manifest.csv \\  
--lineage_call


## Process and summarise the mykrobe json outputs
Required is the path to the directory containing the mykrobe output jsons.

trepogeno \\    
--json_directory files/json_outputs \\  
--tabulate_jsons

## Example full run execution

trepogeno \\    
--json_directory files/json_outputs \\
--type_scheme files/2026-05-12__07_masked_snpsAF09DP5_n10.diagnostic_SNPs_Mykrobe_2026-08-04_b.tsv \\  
--genomic_reference files/reference/Treponema_pallidum_subsp_pallidum_SS14_v2.fa \\  
--probe_prefix files/probes/custom_probes \\ 
--make_probes \\    
--seq_manifest /data/nexstrain/manifest.csv \\  
--tabulate_jsons \\ 
--lineage_call

## All paramaters 

Make Probes
-----------
--make_probes   
    Used to indicate you wish to generate a new set of probes during the work flow

--type_scheme   
    Path to the file that maps snps to specific genomic coordiantes to lineages, to learn more review mykrobe custom lineage calling documentation.

--genomic_reference 
    A fasta file that acts as the genomic reference, must match the reference in the type scheme

--probe_prefix
    Path prefix (without extension) for the probe and lineage files to write, e.g. files/probes/custom writes files/probes/custom.fa and files/probes/custom.json. Defaults to ./probes

--kmer_size 
    what kmer size to use when creating the probes. defaults to 21

Lineage Calling
-----------
--lineage_call  
    Used to indicate you wish to execute the lineage calling workflow

--json_directory    
    A path to the directory for mykrobe to save its json files after calling a lineage. These will be named based on the ID supplied in the manifest e.g SRR567232.json

--seq_manifest  
    A manifest of Sample ID and sequences, the heading should be ID,Read1,Read2. If you are not using paired end fastqs and only have one read leave a trailing , e.g. 'ReadID,/fastq/ReadID1.fastq,'

--probe_prefix
    Path prefix (without extension) of the probe.fa and lineage.json files to read, e.g. files/probes/custom reads files/probes/custom.fa and files/probes/custom.json. Defaults to ./probes. The kmer size used is read automatically from the probe file, it does not need to be supplied separately.

Json Processing
-----------
--tabulate_jsons    
    Used to indicate you wish to execute the workflow to tabulate the output from mykrobe

--json_directory    
    Supply a path to the directory containing mykrobe summary json's, theses should be in the format mykrobe uses when `--report_all_calls` is used in mykrobe (The default if you only use trepogeno)



### Tool Overview
![Trepogeno_pipline](images_examples/pipeline-flow.png)
