import requests
import re
import json


def get_uniprot(ids: list):
    endpoint = 'https://rest.uniprot.org/uniprotkb/accessions'
    return requests.get(endpoint, params={'accessions': ids})


def get_ensembl(ids: list):
    endpoint = 'https://rest.ensembl.org/lookup/id'
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    return requests.post(endpoint, headers=headers, data=json.dumps({'ids': ids}))


def parse_response_uniprot(response: dict):
    protein_data = {}
    if response:
        for entry in response.json()['results']:
            # print(entry)
            accession = entry['primaryAccession']
            species = entry['organism']['scientificName']
            gene = entry['genes']
            seq = entry['sequence']

            function = 'NA'
            if 'comments' in entry:
                function_match = re.search(
                    r"value\": \"([^\"]+)(?=\"\}\],\s\"commentType\": \"FUNCTION\")",
                    json.dumps(entry['comments']))
                if function_match:
                    function = function_match.group(1)

            protein_data[accession] = {
                'organism': species,
                'gene_info': gene,
                'function': function,
                'sequence_info': seq
            }

    return protein_data


def parse_response_ensembl(response: dict):
    output = {}
    for entry, annotations in response.json().items():
        if annotations:
            coordinates = f"{annotations['seq_region_name']}:{annotations['start']}-{annotations['end']}"
            output[entry] = {
                'species': annotations['species'],
                'object_type': annotations['object_type'],
                'biotype': annotations['biotype'],
                'assembly_name': annotations['assembly_name'],
                'strand': annotations['strand'],
                'coordinates': coordinates
            }

            if 'display_name' in annotations:
                output[entry]['display_name'] = annotations['display_name']
            if 'description' in annotations:
                output[entry]['description'] = annotations['description'],
        else:
            output[entry] = None
    return output


def get_db_id_info(ids: list):

    # The regex is taken from here https://www.uniprot.org/help/accession_numbers

    uniprot_accession_regex = re.compile(
        '[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}'
    )

    # Ensembl ID description is taken from
    # https://www.ensembl.org/info/genome/stable_ids/index.html
    # MGP prefixes were ignored

    ensembl_id_regex = re.compile(
        'ENS(\w{3})?\w{1,2}\d{11}'
    )

    # Assume that all IDs come from a single DB
    # and check from which one by the first id

    if re.fullmatch(uniprot_accession_regex, ids[0]):
        id_info = parse_response_uniprot(get_uniprot(ids))
    elif re.fullmatch(ensembl_id_regex, ids[0]):
        id_info = parse_response_ensembl(get_ensembl(ids))
    else:
        raise ValueError(
            f"ID {ids[0]} doesn't match any supported DB accession types")
    return id_info


_uniprot_test_accessions = ['A2BC19', 'P12345', 'Q9Y2H6']
_ensembl_test_accessions = [
    'ENSMUSG00000031201', 'ENSG00000012048', 'ENSGGOT00000013330', 'ENSGT00560000077204']
_wrong_accession = ['ABOBABA32282']


if __name__ == '__main__':

    print(get_db_id_info(_ensembl_test_accessions))
    print(get_db_id_info(_uniprot_test_accessions))
    get_db_id_info(_wrong_accession)  # Error
