## Tabulate 
## Function:
This script is made for the purpose of collecting the json files produced by mykrobe, collating important information, and outputting it in a more human-readable and easily parsable form.

### Argument Example

```
trepogeno --json_directory /path/to/json/files/directory/
```

### Inputs
A path to a directory containing the .json files produced by mykrobe 
supplied by the --json_directory flag

#### Run time function 
This nested dictionary structure is created internally during processing.  
Each json file is a top level key, with each containing sets of dictionaries for each lineage present in that sample's output — recording how many SNPs were called versus how many were possible, not just the lineages with support.
```
   single_sample_dictionary_full = { 
        ERR9768236{ 
            TPE{ 
                calls_made:668,possible_calls:700 
            }, 
            TPE.1.3{ 
                calls_made:0,possible_calls:90 
            } 
            ... 
        }, 
        SRR14277265{ 
            TPE{ 
                calls_made:1,possible_calls:700 
            }, 
            TPE.1.3{ 
                calls_made:0,possible_calls:0 
            } 
            ... 
        } 
    } 
```
### Output

snps_called.csv:
```

Sample_id   |Lineage |Calls made |Possible calls| 
----------- |--------|-----------|--------------|
SRR14277265 |TPE     |  33       |      42      |     
----------- |--------|-----------|--------------|
ERR9768236  |TPE.3.1 |  30       |      38      |
```

And an accompanying snps_called.html with built in filtering for easier manual inspections

![Trepogeno_htmlfile](images_examples/html_table.png)

### summarise_trepogeno_lineage_calls.py
Alongside snps_called.csv/html, `--tabulate_jsons` also runs `summarise_trepogeno_lineage_calls.py`, which writes `lineage_call_summary.csv` to the same `--json_directory`.
This performs a more rigorous primary-call selection than the calls-made/possible-calls table above: mykrobe's own path score (good_nodes/tree_depth) is a best-single-marker metric, so a spurious path built on a few stray markers can tie a genuine call.
This script instead computes `path_concordance`, the mean fraction of concordant markers across all nodes of a path, and uses that (with tree_depth as tiebreaker) to pick the primary lineage per sample. It also reports per-marker confidence stats for the called terminal lineage and flags low-confidence calls (prefixing `called_lineage` with `*`).

If `--type_scheme` is supplied to trepogeno it is passed through as the scheme TSV so the script can read the true `use_ref_allele` flag (the `*` prefix on a lineage) rather than inferring it from the dominant genotype, which is unreliable for cross-branch nodes.

It can also be run standalone outside of trepogeno on any set of mykrobe JSONs:
```
python3 -m trepogeno.post_process_json.summarise_trepogeno_lineage_calls \
  -o summary.csv -s files/scheme.tsv results/*.json
```

