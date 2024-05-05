'''
This script uses fasta file to collect its summary stats and
enrich sequences with info from either Uniprot or Ensembl
depending on the sequence type.

Requirements:

- Python 3.10+
- seqkit installed in the same shell

It accepts one positional argument - path to a .fasta file.

python HW2_2.py ./my_fasta.fa > results.json
'''

import json
import re
import requests
import subprocess
import traceback
from dataclasses import dataclass, field, fields, asdict
from sys import argv, exit
from Bio import SeqIO


@dataclass
class FastaStats:
    file: str
    format: str
    type: str
    num_seqs: int
    sum_len: int
    min_len: int
    avg_len: float
    max_len: int

    def __post_init__(self):
        for fld in fields(self):
            new_str = getattr(self, fld.name).replace(',', '')
            if fld.type == int:
                setattr(self, fld.name, int(new_str))
            elif fld.type == float:
                setattr(self, fld.name, float(new_str))


@dataclass
class SeqInfo:
    description: str
    seq: str
    db_id: str
    db: str
    db_info: dict = field(default_factory=dict)


def collect_fasta_stats(fasta: str) -> tuple[bool, SeqInfo]:

    subprocess.call(f'seqkit stats {fasta} > seqkit.stats', shell=True)

    with open('seqkit.stats', 'r') as f:
        try:

            f.readline()  # skip header
            stats = FastaStats(*f.readline().strip().split())
            return True, stats

        except Exception:

            # I would prefer just to raise the exception here,
            # but if it is asked to return it as a final output
            # I would like to save all the info about the exception

            error = traceback.format_exc()
            return False, error


def parse_fasta(fasta: str, db_name: str) -> tuple[list[SeqInfo], list[str | None]]:
    regex_mapping = {
        'Uniprot': re.compile(
            '[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}'),
        'Ensembl': re.compile('ENS(\w{3})?\w{1,2}\d{11}')
    }

    with open(fasta) as handle:
        fasta_info = []
        ids = []
        regex = regex_mapping[db_name]
        for seq in SeqIO.parse(handle, 'fasta'):
            id_match = re.search(regex, seq.description)
            if id_match:
                id_match = id_match.group(0)
                ids.append(id_match)
            seq_info = SeqInfo(seq.description, str(seq.seq), id_match, db_name)
            fasta_info.append(seq_info)
        return fasta_info, ids


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


def get_db_info(ids, db_name: str):
    if db_name == 'Uniprot':
        db_info = parse_response_uniprot(get_uniprot(ids))
    elif db_name == 'Ensembl':
        db_info = parse_response_ensembl(get_ensembl(ids))
    return db_info


if __name__ == '__main__':
    fasta = argv[1]

    status, stats = collect_fasta_stats(fasta)
    if not status:
        print(stats)
        exit(1)
    db_name = 'Uniprot' if stats.type == 'Protein' else 'Ensembl'
    fasta_info, ids = parse_fasta(fasta, db_name)
    db_info = get_db_info(ids, db_name)
    final_info = {
        'fasta_info': asdict(stats),
        'seq_info': []
        }
    for seq_info in fasta_info:
        if seq_info.db_id:
            seq_info.db_info = db_info[seq_info.db_id]
        final_info['seq_info'].append(asdict(seq_info))
    print(json.dumps(final_info))
