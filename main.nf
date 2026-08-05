#!/usr/bin/env nextflow

/*
========================================================================================
    HELP
========================================================================================
*/

def logo = NextflowTool.logo(workflow, params.monochrome_logs)

log.info logo

NextflowTool.commandLineParams(workflow.commandLine, log, params.monochrome_logs)

def printHelp() {
    NextflowTool.help_message(
        "${workflow.ProjectDir}/schema.json",
        [
            "${workflow.ProjectDir}/assorted-sub-workflows/mixed_input/schema.json"
        ],
        params.monochrome_logs, log
    )
}

def validateParameters() {
    if (params.isolate && params.careful){
        throw new Exception("""The parameters `--isolate` and `--careful` are exclusive and cannot be specified together. You may need to use `--isolate false --careful` to turn off the default `isolate` value and enable `careful`.""")
    }
}

/*
========================================================================================
    IMPORT MODULES/SUBWORKFLOWS
========================================================================================
*/

//
// MODULES
//
include { TREPOGENO              } from './modules/trepogeno.nf'

//
// SUBWORKFLOWS
//

include { MIXED_INPUT         } from './assorted-sub-workflows/mixed_input/mixed_input.nf'

/*
========================================================================================
    RUN MAIN WORKFLOW
========================================================================================
*/

validateParameters()

workflow {
    if (params.help) {
        printHelp()
        exit(0)
    }

    MIXED_INPUT
    | TREPOGENO

}

/*
========================================================================================
    THE END
========================================================================================
*/
