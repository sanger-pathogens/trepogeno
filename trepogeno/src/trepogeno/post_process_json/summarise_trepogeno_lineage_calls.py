#!/usr/bin/env python3
"""
summarise_trepogeno_lineage_calls.py

Summarise lineage calls and confidence from JSON files produced by trepogeno.

Each row is one sample. Columns prefixed 'terminal_' describe the diagnostic
markers of the called terminal lineage node only (e.g. the TPA.1.3-specific
markers), not the full marker set used across all lineages.

Primary call selection
----------------------
mykrobe can return more than one lineage for a sample. Its own path score
(good_nodes/tree_depth) is a *best-single-marker* metric: a node passes if even
one of its markers is concordant, so a spurious path built on 1-3 stray markers
can score a perfect 3/3 and tie a genuine call. To break this we compute
path_concordance: the mean, over the nodes of a path, of the fraction of that
node's markers that are concordant (using the scheme's true use_ref_allele).
A genuine path scores ~1.0; a noise path scores near 0.

The primary call is chosen by path_concordance first, tree_depth as tiebreaker.
(To prefer depth first instead, swap the sort key in pick_primary_call.)
All called lineages are retained with their scores in 'all_called_lineages'.

use_ref_allele
--------------
A '*' prefix on a lineage in the scheme TSV marks use_ref_allele=True (the
reference/ancestral allele is lineage-defining; concordant genotype is [0,0]).
Pass the scheme TSV with --scheme-tsv to use the true flags. Without it, the
flag is inferred by majority genotype, which is unreliable for cross-branch
nodes (e.g. *TPA markers look alt-dominant in a TEN sample).
"""

import argparse
import json
import sys
import csv
import statistics
from pathlib import Path

# Qualitative bands for terminal_min_conf (the weakest-link marker LLR).
# conf scales with depth/evidence, so these flag calls resting on thin evidence.
# Thresholds set from the empirical distribution across ~1900 samples
# (min_conf: Q1 ~10000, median ~26000); tune here if your dataset differs.
CONF_HIGH = 10000   # >= this -> "high"
CONF_LOW  = 1000    # <  this -> "low"; in between -> "moderate"

# Low-confidence flag: called_lineage is prefixed with '*' (mlst-style) when a
# terminal call is untrustworthy on either axis below. Tune here.
MIN_NODE_CONCORDANCE = 0.5    # < this -> call rests on a minority of its markers
MIN_MEAN_CONF        = 1000   # terminal_mean_conf < this -> weak overall evidence


def conf_qual(min_conf):
    """Map terminal_min_conf to a qualitative band. None if no conf available."""
    if min_conf is None:
        return None
    if min_conf >= CONF_HIGH:
        return "high"
    if min_conf < CONF_LOW:
        return "low"
    return "moderate"


def low_confidence_reason(node_concordance, mean_conf):
    """
    Return a reason string if the terminal call is low-confidence, else "".
    Two independent triggers:
      - node_concordance < MIN_NODE_CONCORDANCE: call sits on a minority of its
        markers (spurious descent via a shared/homoplasic SNP), e.g. TPE.3.2 0.1.
      - mean_conf < MIN_MEAN_CONF: weak overall evidence, e.g. a single-marker
        call at low depth (TPA.1.4 at 16x, conf ~700).
    """
    reasons = []
    if node_concordance is not None and node_concordance < MIN_NODE_CONCORDANCE:
        reasons.append("low_node_concordance")
    if mean_conf is not None and mean_conf < MIN_MEAN_CONF:
        reasons.append("low_conf")
    return ";".join(reasons)


def load_json(path, name_delimiter=None):
    """
    Load a trepogeno JSON file. Sample name is taken from the filename stem
    (equivalent to the JSON key). Optional name_delimiter trims any suffix after
    the first occurrence of that character, e.g. '.' strips '.Treponema.ds...'.
    """
    sample = Path(path).stem
    if name_delimiter:
        sample = sample.split(name_delimiter)[0]
    with open(path) as f:
        d = json.load(f)
    return sample, d[list(d.keys())[0]]


def load_use_ref_map(tsv_path):
    """
    Build {lineage_name: use_ref_allele} from the scheme TSV. Lineage is column
    6; a leading '*' marks use_ref_allele=True. Keys are stored without the '*'
    so they match the node names in the JSON (e.g. 'TPA', 'TPA.1').
    """
    use_ref = {}
    with open(tsv_path) as f:
        for line in f:
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 6:
                continue
            name = fields[5]
            use_ref[name.lstrip("*")] = name.startswith("*")
    return use_ref


def infer_use_ref(node_calls):
    """Fallback: infer use_ref_allele from the dominant genotype."""
    n_ref = sum(1 for c in node_calls.values() if sorted(c.get("genotype", [])) == [0, 0])
    n_alt = sum(1 for c in node_calls.values() if sorted(c.get("genotype", [])) == [1, 1])
    return n_ref > n_alt


def node_use_ref(node, node_calls, use_ref_map):
    if use_ref_map is not None and node in use_ref_map:
        return use_ref_map[node]
    return infer_use_ref(node_calls)


def concordant_fraction(node_calls, use_ref):
    """
    Fraction of a node's markers concordant with the expected allele direction,
    counting het ([0,1]) as 0.5. Returns None for an empty node.
    """
    n = len(node_calls)
    if n == 0:
        return None
    concordant_gt = [0, 0] if use_ref else [1, 1]
    score = 0.0
    for c in node_calls.values():
        gt = sorted(c.get("genotype", []))
        if gt == concordant_gt:
            score += 1.0
        elif gt == [0, 1]:
            score += 0.5
    return score / n


def path_concordance(lineage_calls, path_nodes, use_ref_map):
    """
    Mean concordant_fraction across the nodes of a path (e.g. TPA, TPA.2,
    TPA.2.6). This is the full-marker analogue of mykrobe's best-single-marker
    good_nodes score, and distinguishes genuine paths from noise paths.
    """
    fracs = []
    for node in path_nodes:
        calls = lineage_calls.get(node, {})
        f = concordant_fraction(calls, node_use_ref(node, calls, use_ref_map))
        if f is not None:
            fracs.append(f)
    return round(statistics.mean(fracs), 3) if fracs else None


def terminal_marker_stats(terminal_calls, use_ref=None):
    """
    Per-marker statistics for the called terminal lineage. use_ref is taken from
    the scheme when provided, else inferred from the dominant genotype.

    Concordance is relative to the expected direction:
      concordant  — expected genotype present ([1,1] for alt; [0,0] for ref)  → 1.0
      het         — [0,1]; alt allele partially present                        → 0.5
      discordant  — expected genotype absent                                   → 0.0

    terminal_node_concordance = (n_concordant + 0.5 * n_het) / n_markers
    (the concordance of the terminal node's own markers; low values flag a call
    that descended on a minority of its markers, e.g. via a shared/homoplasic SNP).

    conf = abs(LL[ref] - LL[alt]) — LLR for the called genotype; collected for
    concordant and het calls only. terminal_conf_qual bins terminal_min_conf into
    high/moderate/low as an at-a-glance evidence-strength flag.
    """
    n_total = len(terminal_calls)
    if n_total == 0:
        return {k: None for k in [
            "terminal_use_ref_allele", "terminal_n_markers",
            "terminal_n_concordant", "terminal_n_het", "terminal_n_discordant",
            "terminal_node_concordance", "terminal_mean_conf", "terminal_min_conf",
            "terminal_conf_qual",
        ]}

    if use_ref is None:
        use_ref = infer_use_ref(terminal_calls)
    concordant_gt = [0, 0] if use_ref else [1, 1]

    n_concordant = n_het = n_discordant = 0
    confs = []
    for call in terminal_calls.values():
        gt = sorted(call.get("genotype", []))
        conf = call.get("info", {}).get("conf")
        if gt == concordant_gt:
            n_concordant += 1
            if conf is not None:
                confs.append(conf)
        elif gt == [0, 1]:
            n_het += 1
            if conf is not None:
                confs.append(conf)
        else:
            n_discordant += 1

    node_concordance = (n_concordant * 1.0 + n_het * 0.5) / n_total
    min_conf = round(min(confs)) if confs else None

    return {
        "terminal_use_ref_allele":    use_ref,
        "terminal_n_markers":         n_total,
        "terminal_n_concordant":      n_concordant,
        "terminal_n_het":             n_het,
        "terminal_n_discordant":      n_discordant,
        "terminal_node_concordance":  round(node_concordance, 3),
        "terminal_mean_conf":         round(statistics.mean(confs)) if confs else None,
        "terminal_min_conf":          min_conf,
        "terminal_conf_qual":         conf_qual(min_conf),
    }


def has_child_lineages(lineage, scheme_lineages):
    """
    True if the scheme defines any deeper lineage under `lineage`
    (e.g. TPA.1 has children TPA.1.1, TPA.1.2, ...). Used to distinguish a
    call that stopped at an internal node (sub-lineage undetermined) from a
    genuine terminal-leaf call.
    """
    prefix = lineage + "."
    return any(s.startswith(prefix) for s in scheme_lineages)


def pick_primary_call(candidates):
    """
    candidates: list of (lineage, tree_depth, path_concordance).
    Primary = highest path_concordance, tree_depth as tiebreaker.
    (Swap the key tuple order to prefer depth first.)
    """
    return max(candidates, key=lambda c: (c[2] if c[2] is not None else -1, c[1]))


def summarise_sample(sample, data, use_ref_map=None):
    lineage_calls = data.get("lineage_calls", {})
    phylo = data.get("phylogenetics", {}).get("lineage", {})
    genome_depth = median_genome_depth(lineage_calls)

    called = phylo.get("lineage", [])
    calls_summary = phylo.get("calls_summary", {})

    null_row = {
        "sample":                        sample,
        "called_lineage":                "no_call",
        "n_called_lineages":             0,
        "all_called_lineages":           None,
        "primary_path_concordance":      None,
        "flag_reason":                   None,
        "sublineage_resolved":           None,
        "path_support":                  None,
        "node_scores":                   None,
        "terminal_use_ref_allele":       None,
        "terminal_n_markers":            None,
        "terminal_n_concordant":         None,
        "terminal_n_het":                None,
        "terminal_n_discordant":         None,
        "terminal_node_concordance":     None,
        "terminal_mean_conf":            None,
        "terminal_min_conf":             None,
        "terminal_conf_qual":            None,
        "genome_depth":                  genome_depth,
    }
    if not called:
        return null_row

    # Score every called path by full-marker concordance
    candidates = []
    for lin in called:
        cs = calls_summary.get(lin, {})
        depth = cs.get("tree_depth", 0)
        path_nodes = list(cs.get("genotypes", {}).keys())  # e.g. [TPA, TPA.2, TPA.2.6]
        pc = path_concordance(lineage_calls, path_nodes, use_ref_map)
        candidates.append((lin, depth, pc))

    primary_lineage, _, primary_pc = pick_primary_call(candidates)
    cs = calls_summary.get(primary_lineage, {})

    # All calls listed with their concordance, best first
    ordered = sorted(candidates, key=lambda c: (c[2] if c[2] is not None else -1, c[1]), reverse=True)
    all_called_str = ";".join(f"{lin}({pc})" for lin, _, pc in ordered)

    good_nodes  = cs.get("good_nodes")
    tree_depth  = cs.get("tree_depth")
    node_scores_str = ";".join(f"{k}={v}" for k, v in cs.get("genotypes", {}).items())

    primary_calls = lineage_calls.get(primary_lineage, {})
    term_use_ref = node_use_ref(primary_lineage, primary_calls, use_ref_map)
    stats = terminal_marker_stats(primary_calls, use_ref=term_use_ref)

    # "no" if the call stopped at an internal node that has child lineages in
    # the scheme (sub-lineage undetermined — no child markers present); "yes"
    # if the call is a genuine terminal leaf.
    sublineage_resolved = "no" if has_child_lineages(primary_lineage, lineage_calls.keys()) else "yes"

    # Low-confidence flag (mlst-style): prefix called_lineage with '*' when the
    # terminal call is weak. flag_reason records why (empty if confident).
    flag_reason = low_confidence_reason(stats["terminal_node_concordance"],
                                        stats["terminal_mean_conf"])
    display_lineage = ("*" + primary_lineage) if flag_reason else primary_lineage

    return {
        "sample":                   sample,
        "called_lineage":           display_lineage,
        "n_called_lineages":        len(called),
        "all_called_lineages":      all_called_str,
        "primary_path_concordance": primary_pc,
        "flag_reason":              flag_reason,
        "sublineage_resolved":      sublineage_resolved,
        "path_support":             f"{good_nodes}/{tree_depth}" if good_nodes is not None else None,
        "node_scores":              node_scores_str,
        **stats,
        "genome_depth":             genome_depth,
    }


def median_genome_depth(lineage_calls):
    """
    Estimate genome-wide kmer depth from info.expected_depths (constant across
    call objects, so one entry per lineage suffices).
    """
    depths = []
    for calls in lineage_calls.values():
        for call in calls.values():
            ed = call.get("info", {}).get("expected_depths", [])
            if ed:
                depths.append(ed[0])
            break
    return int(statistics.median(depths)) if depths else None


def run_summarise_lineage_calls(json_directory, scheme_tsv=None, output_csv=None, name_delimiter=None):
    """
    Programmatic entry point used by trepogeno's --tabulate_jsons workflow.
    Globs json_directory for *.json, summarises each, and writes the result CSV.
    """
    json_directory = Path(json_directory)
    json_files = sorted(json_directory.glob("*.json"))
    if not json_files:
        print(f"Warning: no .json files found in {json_directory}", file=sys.stderr)
        return

    use_ref_map = load_use_ref_map(scheme_tsv) if scheme_tsv else None

    rows = []
    for path in json_files:
        try:
            sample, data = load_json(path, name_delimiter=name_delimiter)
            rows.append(summarise_sample(sample, data, use_ref_map=use_ref_map))
        except Exception as e:
            print(f"Warning: skipping {path}: {e}", file=sys.stderr)

    if not rows:
        print("No valid JSON files processed.", file=sys.stderr)
        return

    output_csv = Path(output_csv) if output_csv else json_directory / "lineage_call_summary.csv"
    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} samples -> {output_csv}")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Summarise lineage calls and confidence metrics from trepogeno JSON output. "
            "The primary 'called_lineage' is chosen by full-marker path concordance "
            "(tree_depth as tiebreaker); all calls are listed with scores in "
            "'all_called_lineages'. Pass --scheme-tsv for correct use_ref_allele flags."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  %(prog)s -o summary.csv -s scheme.tsv -d . results/*.json\n"
            "  %(prog)s -o summary.csv results/*.json   (use_ref_allele inferred)"
        ),
    )
    parser.add_argument("json_files", nargs="+", metavar="JSON",
                        help="trepogeno output JSON file(s), one per sample")
    parser.add_argument("-o", "--output", required=True, metavar="CSV",
                        help="output CSV file path")
    parser.add_argument("-s", "--scheme-tsv", default=None, metavar="TSV",
                        help="scheme TSV to read true use_ref_allele flags "
                             "(lineage in column 6, '*' prefix = use_ref_allele=True)")
    parser.add_argument("-d", "--name-delimiter", default=None, metavar="CHAR",
                        help="trim the sample name at the first occurrence of this "
                             "character (e.g. '.' to strip species/downsampling suffixes)")
    args = parser.parse_args()

    use_ref_map = load_use_ref_map(args.scheme_tsv) if args.scheme_tsv else None

    rows = []
    for path in args.json_files:
        try:
            sample, data = load_json(path, name_delimiter=args.name_delimiter)
            rows.append(summarise_sample(sample, data, use_ref_map=use_ref_map))
        except Exception as e:
            print(f"Warning: skipping {path}: {e}", file=sys.stderr)

    if not rows:
        print("No valid JSON files processed.", file=sys.stderr)
        sys.exit(1)

    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} samples → {args.output}")


if __name__ == "__main__":
    main()
