process TREPOGENO {
    tag ${meta.ID}
    label "cpu_1"
    label "mem_1"
    label "time_12h"

    container  'quay.io/sangerpathogens/trepogeno:main'

    publishDir mode: 'copy', path: "${params.outdir}/${meta.ID}/trepogeno/"

    input:
    tuple val(meta), path(type_scheme), path(reference), val(probes_name), path(manifest)

    output:
    tuple val(meta), path(jsons),  emit: mykrobe_summary
    tuple val(meta), path(probes), emit: probes

    script:
    probes = "probes_and_lineage"
    jsons = "json_outputs"
    """
    trepogeno \
    --json_directory ${jsons} \ 
    --type_scheme ${type_scheme} \
    --genomic_reference ${reference} \
    --probe_and_lineage_dir ${probes} \ 
    --seq_manifest ${manifest} \
    --probe_lineage_name ${probes_name} \
    --make_probes \
    --tabulate_jsons \ 
    --lineage_call
    """
}