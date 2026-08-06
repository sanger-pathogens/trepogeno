import json
from pathlib import Path
import pandas as pd

#This function is imported for injecting java script into the html
from nextstrain.post_process_json.style import style_html

def get_all_lineage_calls_for_one_sample(json_dict,full_dictionary):
    """
    This function creates a dictionary which records the number of calls made vs the number of possible calls in a dictionary
    We only load one json into memory at a time so it shouldn't be too memory intensive 
    """
    keys = list(json_dict)
    sample_id = keys[0]
    lineage_list = list(json_dict[sample_id]["lineage_calls"]) #Access the "lineage calls" key and put it in a list
        
    single_sample_dictionary_full = {
        sample_id: {}
    }

    for lineage in lineage_list:
        possible_calls = 0
        calls_made = 0

        calls = json_dict[sample_id]["lineage_calls"].get(lineage, {})

        for probe_id, probe_data in calls.items():
            genotype = probe_data.get("genotype")
            if genotype == [0, 0]:
                possible_calls += 1
            elif genotype == [1, 1] or genotype == [0, 1]:
                possible_calls += 1
                calls_made += 1

        single_sample_dictionary_full[sample_id][lineage] = {
            "calls_made": calls_made,
            "possible_calls": possible_calls,
        }

    full_dictionary.update(single_sample_dictionary_full)
    return full_dictionary

def get_json_file_paths(json_directory_path):

    json_list = []
    for file in json_directory_path.glob("*.json"):
        json_list.append(file)
    return json_list

def filter_to_single_rows(call_summary_table, json_directory):
    """Blindly gets the lineage with the highest depth per sample, does not consider lineages of equal depth"""
    # Filter to supported lineages only
    call_summary_table_supported = call_summary_table[call_summary_table["Calls Made"] > 0].copy()

    # Calculate lineage depth by counting '.' in lineage name
    call_summary_table_supported["lineage_depth"] = call_summary_table_supported["Lineage"].str.count("\.")

    # Sort by Sample ID, then descending lineage depth
    call_summary_table_supported_sorted = call_summary_table_supported.sort_values(
        by=["Sample ID", "lineage_depth"],
        ascending=[True, False]
    )

    # Take the top lineage per Sample ID
    call_summary_supported_best = call_summary_table_supported_sorted.groupby("Sample ID").head(1)

    # Save or display
    call_summary_supported_best.to_csv(Path(json_directory) / "deepest_lineage_called_all.csv", index=False)

def create_and_write_table(full_dictionary, json_directory):
    data = []
    for sample_id, lineages in full_dictionary.items():
        for lineage, stats in lineages.items():
            data.append({
                "Sample ID": sample_id,
                "Lineage": lineage,
                "Calls Made": stats.get("calls_made", 0),
                "Possible Calls": stats.get("possible_calls", 0),
            })

    call_summary_table = pd.DataFrame(data)

    csv_path = Path(json_directory) / "snps_called.csv"
    html_path = Path(json_directory) / "snps_called.html"
    call_summary_table.to_csv(csv_path, index=False)
    call_summary_table.to_html(html_path, index=False)

    filter_to_single_rows(call_summary_table, json_directory)
    style_html(html_path)

    

def get_mykrobe_best_call(genotype,base_id):
    """
    This function below been written by the brilliant people over at genotyphi
    Minor changes have been made to fit into this script for example ignoring particular lineages
    The intention is to parse the lineage calls and get the 'best' call based on a score given to each lineage for each sample
    The score is based on the number of nodes in the lineage tree that are 'called'
    """
    full_lineage_data = genotype[base_id]["phylogenetics"]

    genotype_details = full_lineage_data['lineage']['calls_summary']
    genotype_list = list(genotype_details.keys())
    # intialise empty values for best score and corresponding genotype
    best_score = 0
    best_genotype = None
    # node support is the number of 'good nodes' called by mykrobe
    # needs to be X/Y, where Y is the total number of levels at that genotype

# loop through each genotype
    for genotype in genotype_list:
        # the maximum score we can get is the total depth of the heirarchy
        max_score = genotype_details[genotype]['tree_depth']
        # the actual score is a sum of the values within each levels call
        actual_score = sum(list(genotype_details[genotype]['genotypes'].values()))
        # if actual score is equal to the max score, then this is the best genotype
        if actual_score == max_score:
            best_score = actual_score
            best_genotype = genotype

        # if actual score is < max score, but is greater than the current best score,
        # then this is our best genotype for the moment
        elif actual_score < max_score and actual_score > best_score:
            best_score = actual_score
            best_genotype = genotype
            #node_support = genotype_details[best_genotype]['good_nodes']

    # determine any quality issues and split them amongst our various columns
    # if the node support for the best genotype is not '1' at all positions, we need to report that
    best_calls = genotype_details[best_genotype]['genotypes']
    # remove any calls that are prepended with "lineage", as these are fake levels in the hierarchy
    best_calls = dict([(x, y) for x, y in best_calls.items() if not x.startswith("lineage")])
    # get a list of all the calls for calculating confidence later
    best_calls_vals = list(best_calls.values())
    poorly_supported_markers = []
    # dict that keeps percentage supports, key=percent support; value=level
    lowest_within_genotype_percents = {}
    # list that gives supports for all markers in best call
    final_markers = []

    for level in best_calls.keys():
      # regardless of the call, get info
      call_details = full_lineage_data["lineage"]['calls'][best_genotype][level]
      # check that there is something there
      if call_details:
          # need to do this weird thing to grab the info without knowing the key name
          call_details = call_details[list(call_details.keys())[0]]
          ref = call_details['info']['coverage']['reference']['median_depth']
          alt = call_details['info']['coverage']['alternate']['median_depth']
          # calculate percent support for marker
          try:
              percent_support = alt / (alt + ref)
          except ZeroDivisionError:
              percent_support = 0
          # get the level name with the genotyphi call, ignoring any markers that don't exist
          if not level.startswith("lineage"):
              marker_string = level + ' (' + str(best_calls[level]) + '; ' + str(alt) + '/' + str(ref) + ')'
              final_markers.append(marker_string)
      # if the value is null, just report 0 (indicates that no SNV detected, either ref or alt?)
      else:
          lowest_within_genotype_percents[0] = level
          # get the level name with the genotyphi call, ignoring any markers that don't exist
          if not level.startswith("lineage"):
              marker_string = level + ' (0)'
              # its returned null so is therefore by definition poorly supported
              poorly_supported_markers.append(marker_string)
              # add to the final markers list too
              final_markers.append(marker_string)
              percent_support = 0
      # if call is 1 then that is fine, count to determine confidence later
      # if call is 0.5, then get info
      # if call is 0, there will be no info in the calls section, so just report 0s everywhere
      if best_calls[level] < 1:
          # then it must be a 0 or a 0.5
          # report the value (0/0.5), and also the depth compared to the reference
          # get the level name with the genotyphi call, ignoring any markers that don't exist
          if not level.startswith("lineage"):
              lowest_within_genotype_percents[percent_support] = level
              # add this to the list of poorly supported markers
              poorly_supported_markers.append(marker_string)

    # determining final confidence is based ONLY on the actual genotype, not incongruent genotype calls
    # strong = quality 1 for all calls
    if best_calls_vals.count(0) == 0 and best_calls_vals.count(0.5) == 0:
        confidence = 'strong'
        lowest_support_val = '-'
    # moderate = quality 1 for all calls bar 1 (which must be quality 0.5 with percent support > 0.5)
    elif best_calls_vals.count(0) == 0 and best_calls_vals.count(0.5) == 1:
        if min(lowest_within_genotype_percents.keys()) > 0.5:
            confidence = 'moderate'
        else:
            confidence = 'weak'
        lowest_support_val = round(min(lowest_within_genotype_percents.keys()), 3)
    # weak = more than one quality < 1, or the single 0.5 call is < 0.5% support
    else:
        confidence = 'weak'
        lowest_support_val = round(min(lowest_within_genotype_percents.keys()), 3)

    # make a list of all possible quality issues (incongruent markers, or not confident calls within the best geno)
    non_matching_markers = []
    non_matching_supports = []
    # we now want to report any additional markers that aren't congruent with our best genotype
    #ie if 3.6.1 is the best genotype, but we also have a 3.7.29 call, we need to report the 3.7 and 3.29 markers as incongruent
    if len(genotype_list) > 1:
        # remove the best genotype from the list
        genotype_list.remove(best_genotype)
        # loop through each incongruent phenotype
        for genotype in genotype_list:
            # extract the calls for that genotype
            other_calls = genotype_details[genotype]['genotypes']
            # for every call in our BEST calls, we're only interested
            # in calls that are incongruent
            for call in other_calls.keys():
                if call not in best_calls.keys():
                    call_info = full_lineage_data["lineage"]['calls'][genotype][call]
                    # check that there is something there (if the value is null, don't report it for incongruent calls)
                    if call_info:
                        # need to do this weird thing to grab the info without knowing the key name
                        call_info = call_info[list(call_info.keys())[0]]
                        ref_depth = call_info['info']['coverage']['reference']['median_depth']
                        alt_depth = call_info['info']['coverage']['alternate']['median_depth']
                        # only keep the call if the alternate has a depth of > 1
                        # this is because mykrobe fills in intermediate levels of the hierarchy with 0s
                        # if a lower level SNV marker is detected
                        if alt_depth >= 1:
                            percent_support = alt_depth / (alt_depth + ref_depth)
                            non_matching_supports.append(percent_support)
                            # get genotyphi call
                            if not call.startswith("lineage"):
                                marker_string = call + ' (' + str(other_calls[call]) + '; ' + str(alt_depth) + '/' + str(ref_depth) + ')'
                                non_matching_markers.append(marker_string)

    # get max value for non matching supports, if empty, return ''
    if len(non_matching_supports) > 0:
        max_non_matching = round(max(non_matching_supports), 3)
    else:
        max_non_matching = '-'
    # add '-' for those columns that are empty
    if len(poorly_supported_markers) == 0:
        poorly_supported_markers = ['-']
    if len(non_matching_markers) == 0:
        non_matching_markers = ['-']
    if len(final_markers) == 0:
        final_makers = ['-']

    print(f"best genotype for {base_id} is {best_genotype} with {confidence} confidence and lowest support {lowest_support_val}")

#    return best_genotype, confidence, lowest_support_val, poorly_supported_markers, max_non_matching, non_matching_markers, final_markers

def run_tabulate_json(json_directory):
    """
    Function controling the script execution
    """
    #First we get the paths to the json file and collect them in a list
    json_list = get_json_file_paths(json_directory)

    full_dictionary = {}
    #For each json path
    for path in json_list:
        
        with open(path) as json_path:
            genotype = json.load(json_path) #Load the json into a dictionary 

            base_id = path.stem #collect the Sample ID, this should also match the top level key of the nested dictionary we just initilised 

            full_dictionary = get_all_lineage_calls_for_one_sample(genotype,full_dictionary) #We create a dictionary for each lineage per sample and the number of calls possible vs made for each lineage 
            get_mykrobe_best_call(genotype,base_id) #This just parses the 'full' dictionary to get the deepest lineage called for each sample
            
    create_and_write_table(full_dictionary, json_directory) #write out the 'best' calls (which lineage for each sample had the highest proportion of calls made)
