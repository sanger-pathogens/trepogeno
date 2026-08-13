<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../../assets/trepogeno-logo-dark.svg">
    <img alt="trepogeno" src="../../assets/trepogeno-logo-light.svg" width="420">
  </picture>
</p>

# **THESE SCRIPTS ARE SEPARATE FROM THE MAIN TOOL AND UNUSED**

## The following scripts are _one_ way you can make a typing scheme required by mykrobe custom lineage calling
## This is one methodology in which you could produce a similar scheme using rPinecone and a VCF if one wished
## **It is recommended to use the provided typing scheme**


This repo contains scripts for creating a basic typing scheme, referred to as a reference coordinate file by mykrobe for mykrobe's lineage calling.  
Mykrobe requires a typing scheme to make a probes.fa and lineage.json with the `mykrobe variants make-probes` command.  
The outputs from the make-probes command are used for lineage calling with `mykrobe predict`.  
These scripts require a VCF and pinecone.bootstrap.table.csv from rPinecone containing clusters and lineage cluster assignments against samples.  
With these, the scripts should work out which SNPs define a lineage by checking which SNPs are present in all members of a lineage cluster while being absent from all other samples.

# create_probes.sh
## Function:
This is a bash script that will execute the below two scripts in order and will then run mykrobe make-probes automatically. This is offered as a streamlined way to process the files and create mykrobe probes and lineage file for calling.
The script requires a path to the VCF, path to the pinecone clusters file, pinecone threshold number, and a path to the reference FASTA of the same sample used in the VCF. 

### Argument Example
```
./create_probes.sh \
-v /data/pam/team230/jb71/scratch/NextStrain/files/2025-01-31_masked_snps.vcf \
-c /data/pam/team230/jb71/scratch/NextStrain/rPinecone/Results/rPineCone20-5.pinecone.bootstrap.table.csv \
-p 95 \
-r /data/pam/team230/jb71/scratch/NextStrain/files/reference/NC/nc_021508.fasta
```

### Output
lineage_defining_snps.csv (see below).  
lineage_coordinate_output.txt (see below).  
test_probes.fa (mykrobe probes file used for lineage calling).  
lineage95.json (mykrobe lineage file used for lineage calling).  


# create_matrix_get_lineage_defining_snps.py:
## Function:
This script creates a 'SNP matrix' from a VCF file where genomic positions are the columns while the index rows are samples.
The value will contain either the ref or alt allele, depending on if a 0 or 1 is in the first position in the VCF.
It then takes the VCF and the 'SNP matrix' and uses them to determine which SNPs at which genomic positions define the lineage clusters calculated by rPinecone.

### Argument Example 
```
--vcf path/2025-01-31_masked_snps.vcf (Required)
--cluster_file path/PineCone2-2.pinecone.bootstrap.table.csv (Required)
--output . (Required)
--pinecone_threshold 95 (Optional, default is 50 will only work with values 95, 80, 50, 20, or 5)
```

### Output
lineage_defining_snps.csv

```
Cluster, SNP_Position, Allele
    671,       651723, A
    671,       657912, T
    671,       994070, C
    723,        24485, A
    723,       290357, T
    723,       699367, A
    723,       785674, A
```

# create_full_reference_coordinate_file.py:
## Function:
This script takes a VCF, path to the previously created lineage defining SNP file, pinecone lineage clusters CSV, as well as optionally a pinecone threshold and output path/name. It produces a reference coordinate file, as detailed above, with lineages annotating the file depending on which SNP defines them.
Further details can be found here:
https://github.com/Mykrobe-tools/mykrobe/wiki/Custom-Panels
https://github.com/Mykrobe-tools/mykrobe/wiki/Custom-Lineage-Calling

### Argument Example 
```
--vcf path/2025-01-31_masked_snps.vcf (Required)
--lineage_defining_snps path/lineage_defining_snps.csv(Required)
--cluster_file path/PineCone2-2.pinecone.bootstrap.table.csv (Required)
--pinecone_threshold 95 (Optional, default is 50 only works with values 95, 80, 50, 20, or 5)
--output lineage_coordinate_output.txt (Optional, default is './lineage_coordinate_output.txt')
```

### Output
lineage_coordinate_output.txt

```
ref	1000	A	T	DNA	lineage1
ref	2000	C	A	DNA	lineage1.1
ref	3000	G	C	DNA	lineage1.2
ref	4000	T	A	DNA	lineage2
```

#### Improvements
This script does not yet consider the situation where all samples carry the alternative allele relative to the reference used in the VCF, which may itself be lineage defining. 