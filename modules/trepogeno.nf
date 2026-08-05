process TREPOGENO {
    tag ${meta.ID}
    label "cpu_1"
    label "mem_1"
    label "time_12h"

    container  'quay.io/sangerpathogens/trepogeno:main'

    publishDir mode: 'copy', path: "${params.outdir}/${meta.ID}/trepogeno/${probes}", pattern: "${probes}/*"
    publishDir mode: 'copy', path: "${params.outdir}/${meta.ID}/trepogeno/${jsons}", pattern: "${jsons}/*"

    input:
    tuple val(meta), path(reads_1), path(reads_2)

    output:
    tuple val(meta), path(jsons),  emit: mykrobe_summary
    tuple val(meta), path(probes), emit: probes

    script:
    probes = "probes_and_lineage"
    jsons = "json_outputs"
    manifest = "manifest.csv"
    probes_name = params.probes_name ? "--probe_lineage_name ${params.probes_name}" : ""
    """
    echo "ID,reads_1,reads_2" > ${manifest}
    echo "${meta.ID},${reads_1},${reads_2}" >> ${manifest}

    trepogeno \
    --json_directory ${jsons} \ 
    --type_scheme ${params.type_scheme} \
    --genomic_reference ${params.reference} \
    --probe_and_lineage_dir ${probes} \ 
    --seq_manifest ${manifest} \
    ${probes_name} \
    --kmer_size ${params.kmer_size} \
    --make_probes \
    --tabulate_jsons \ 
    --lineage_call
    """
}