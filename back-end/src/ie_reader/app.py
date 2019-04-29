from pathlib import Path

from flask import Flask, request, abort
from allennlp.predictors.predictor import Predictor
import spacy
from spacy.lang.en.stop_words import STOP_WORDS

from pandas.io.json import json_normalize

import json

import csv
from Levenshtein import distance

from itertools import product


model_path = Path(Path(__file__).parent) / '..' / '..' / 'model'

nlp = spacy.load('en_core_web_sm')

coref_archive = 'coref-model-2018.02.05.tar.gz'
coref_predictor = Predictor.from_path(model_path / coref_archive)

openie_archive = 'openie-model.2018-08-20.tar.gz'
openie_sentence_predictor = Predictor.from_path(model_path / openie_archive)


class OpenieDocumentPredictor:
    @staticmethod
    def predict(doc):
        prediction = []
        for sent in doc.sents:
            prediction.append(openie_sentence_predictor.predict(sent.text))
        return prediction


openie_document_predictor = OpenieDocumentPredictor()


app = Flask(__name__)


@app.route('/api/iepredict/', methods=["POST"])
def predict_req():
    payload = request.get_json(force=True)
    text = payload.get('text')
    model = payload.get('model')

    if model == 'rnnie.coref':
        options = {
            LEVENSHTEIN_DISTANCE_PARAM: payload.get('levenshtein', 0.2)
        }

        _, _, nodes, edges = open_ie_with_coreference(text.replace('\n', ""), options=options)
        return json.dumps(dict(nodes=nodes, edges=edges))
    # Add additional model pipelines here
    abort(404)


def cluster_to_strings(coref_prediction):
    output = []
    document = coref_prediction['document']
    for cluster in coref_prediction['clusters']:
        output.append([' '.join(document[i:j + 1]) for i, j in cluster])
    return output


def bio_tag_array_to_pos_dict(bio_str_array, offset=0):
    output = {}
    for i_init, elem in enumerate(bio_str_array):
        i = i_init + offset
        if len(elem) > 1:
            tag = elem[2:]
            if tag not in output:
                output[tag] = [i, i]
            else:
                output[tag][1] = i
    return output


OVERLAP_EXACT = "OVERLAP_EXACT"
OVERLAP_PARTIAL = "OVERLAP_PARTIAL"
OVERLAP_CONTAINS = "OVERLAP_CONTAINS"
OVERLAP_SAME_START = "OVERLAP_SAME_START"
OVERLAP_SAME_ROOT = "OVERLAP_SAME_ROOT"

SOURCE_COREF = 'SOURCE_COREF'
SOURCE_OPENIE = "SOURCE_OPENIE"

LEVENSHTEIN_DISTANCE_PARAM = 'levenshtein'


class Entity():
    def __init__(self, spans=None, source=None):
        self.spans = {}
        if spans is not None:
            self.add_spans(spans, source)

    def add_spans(self, spans, source):
        for span in spans:
            self.spans[tuple(span)] = source

    def check_overlap(self, test_span, doc):
        overlaps = []
        test_low, test_high = test_span
        # only checks for exact matches -- consider expanding
        for span_low, span_high in self.spans:
            if test_low == span_low and test_high == span_high:
                overlaps.append([[span_low, span_high], OVERLAP_EXACT])
            # check for same root
            # elif doc[span_low: span_high + 1].root == doc[test_low: test_high + 1].root:
            #     overlaps.append([[span_low, span_high], OVERLAP_SAME_ROOT])
            # check for intersection
            elif span_low <= test_high and test_low <= span_high:
                # test for contained
                if span_low == test_low:
                    overlaps.append([[span_low, span_high], OVERLAP_SAME_START])
                elif span_low <= test_high and span_high >= test_high:
                    overlaps.append([[span_low, span_high], OVERLAP_CONTAINS])
                else:
                    overlaps.append([[span_low, span_high], OVERLAP_PARTIAL])

        return overlaps

    def add_span_if_overlap(self, test_span, tag, doc):
        overlaps = self.check_overlap(test_span, doc)
        OVERLAP_TYPES = [overlap[1] for overlap in overlaps]
        TYPES_TO_ADD = set([OVERLAP_SAME_ROOT, OVERLAP_SAME_START])
        if OVERLAP_EXACT in OVERLAP_TYPES:
            return True
        if len(TYPES_TO_ADD.intersection(set(OVERLAP_TYPES))):
            if OVERLAP_SAME_START in OVERLAP_TYPES:
                self.add_spans([test_span], f'{tag}-{OVERLAP_SAME_START}')
            elif OVERLAP_SAME_ROOT in OVERLAP_TYPES:
                self.add_spans([test_span], f'{tag}-{OVERLAP_SAME_ROOT}')
            return True
            # elif OVERLAP_PARTIAL in OVERLAP_TYPES and OVERLAP_EXACT not in OVERLAP_TYPES:
            #     self.add_spans([test_span], f'{tag}-{OVERLAP_PARTIAL}')
        return False

    def to_string(self, document):
        output = []
        output_set = set()
        for i, j in self.spans:
            span_str = ' '.join([word for word in document[i: j + 1] if word])
            if len(span_str) and span_str not in output_set and span_str not in STOP_WORDS:
                added = False
                for index, string in enumerate(output):
                    if span_str.startswith(string):
                        # replace the string in the list with this longer representation
                        output[index] = span_str
                        added = True
                    elif string.startswith(span_str):
                        # do nothing already added
                        added = True
                if not added:
                    output.append(span_str)
                output_set.add(span_str)

        return '\n'.join(dedupe(output))

    def to_string_list(self, document):
        output = []
        output_set = set()
        for i, j in self.spans:
            span_str = " ".join([word for word in document[i: j + 1]])
            if span_str not in output_set:
                output.append(span_str)
            output_set.add(span_str)
        return output

    def merge_entity(self, other):
        for span in other.spans:
            self.add_spans([span], 'LEVENSHTEIN')

    def __str__(self):
        return self.spans


def dedupe(seq, idfun=None):
   # order preserving
   if idfun is None:
       def idfun(x): return x
   seen = {}
   result = []
   for item in seq:
       marker = idfun(item)
       # in old Python versions:
       # if seen.has_key(marker)
       # but in new ones:
       if marker in seen: continue
       seen[marker] = 1
       result.append(item)
   return result


def get_entity_for_span(entities, span):
    for i, entity in enumerate(entities):
        if tuple(span) in entity.spans:
            return i, entity
    print('no entity')
    return None, None


def get_str_from_span(document, span):
    return ' '.join(document[span[0]: span[1] + 1])


def collect_normalized_verbs(triples, entities, document):
    # parse the verbs 1 entity at a time
    # get first entity
    verbs = []
    for triple in triples:
        verb = {}
        for arg in ("ARG0", "ARG1", "ARG2"):
            if arg in triple:
                arg_span = triple[arg]
                arg_i, _ = get_entity_for_span(entities, arg_span)
                if arg_i is not None:
                    arg_str = get_str_from_span(document, arg_span)
                    verb[arg] = dict(
                        span=arg_span,
                        entity=arg_i,
                        string=arg_str,
                        entity_str=entities[arg_i].to_string(document)
                    )

        verb_phr = {}
        verb_spans = []
        for k in triple.keys():
            if k[-1] == "V":
                verb_spans.append(triple[k])
                verb_phr[tuple(triple[k])] = 1
        verb_str = ' '.join([get_str_from_span(document, k) for k in sorted(verb_phr.keys())])
        verb['VERB'] = dict(
            spans=verb_spans,
            string=verb_str
        )

        verbs.append(verb)
    return verbs


def create_nodes(entities, document, entity_set):
    """
    These need to be of the form :
    {
        id: 1
        label: "multi\nline\label",
        shape: 'text' // shape of the node
        title: "node tooltip"
    }

    :return:
    """

    return [dict(id=index, label=entity.to_string(document)) for index, entity in enumerate(entities) if index in entity_set]


def create_edges(verbs):
    output = []
    entity_set = set()
    for verb in verbs:
        if verb.get('ARG0'):
            entity_set.add(verb['ARG0']['entity'])
            if verb.get('ARG1'):
                entity_set.add(verb['ARG1']['entity'])
                output.append({
                    'from': verb['ARG0']['entity'],
                    'label': verb['VERB']['string'],
                    'to': verb['ARG1']['entity'],
                })
        if verb.get('ARG2') and verb.get('ARG1'):
            entity_set.add(verb['ARG2']['entity'])
            output.append({
                'from': verb['ARG1']['entity'],
                'label': '~',
                'to': verb['ARG2']['entity'],
            })

    return output, entity_set


def remove_stop_words(string):
    return ' '.join([word for word in string.split(' ') if word not in STOP_WORDS])


def merge_entities(entities, document, levenshtein_distance=0.2):
    merged_entities = []
    used_entities = set()

    for e1_i, entity1 in enumerate(entities):
        if e1_i not in used_entities:
            used_entities.add(e1_i)
            for e2_i, entity2 in enumerate(entities[e1_i:]):
                if e2_i not in used_entities:
                    e1_strs = entity1.to_string_list(document)
                    e2_strs = entity2.to_string_list(document)
                    for e1_str, e2_str in product(e1_strs, e2_strs):
                        e1_str = remove_stop_words(e1_str)
                        e2_str = remove_stop_words(e2_str)
                        if len(e1_str) and len(e2_str):
                            if distance(e1_str, e2_str) / max(len(e1_str), len(e2_str)) < levenshtein_distance:
                                entity1.merge_entity(entity2)
                                used_entities.add(e2_i)
            merged_entities.append(entity1)
    return merged_entities


def open_ie_with_coreference(text, options):
    doc = nlp(text)
    ## make a cleaned up text from the doc to create a unified input

    coref_prediction = coref_predictor.predict(text)##' '.join([sent.text for sent in doc.sents]))
    openie_prediction = openie_document_predictor.predict(doc)
    # cluster_strings = cluster_to_strings(coref_prediction)

    entities = []
    doc_normalized_verbs = []
    for span_list in coref_prediction['clusters']:
        entities.append(Entity(span_list, SOURCE_COREF))
    for sentence_i, sentence_prediction in enumerate(openie_prediction):
        if sentence_i > 0:
            index_offset = sum([len(s['words']) for s in openie_prediction[:sentence_i]])
        else:
            index_offset = 0
        print(f'sentence {sentence_i} offset {index_offset}')
        # ensure the offset is working

        # for i in range(3):
        #     print('coref', coref_prediction['document'][index_offset + i])
        #     print('sentence', sentence_prediction['words'][0 + i])

        assert coref_prediction['document'][index_offset] == sentence_prediction['words'][0]
        for verb_i, verb in enumerate(sentence_prediction['verbs']):
            arg_pos_dict = bio_tag_array_to_pos_dict(verb['tags'], index_offset)
            doc_normalized_verbs.append(arg_pos_dict)

            for arg, span in arg_pos_dict.items():
                tag = f'openie-{sentence_i}-{verb_i}-{arg}'
                added_entity = False
                for entity in entities:
                    if not added_entity:
                        added_entity = entity.add_span_if_overlap(span, tag, doc)
                    # if exact_ntity_match:
                    #     exact_match = True
                if not added_entity:
                    entities.append(Entity([span], tag))

    entities = merge_entities(entities, coref_prediction['document'], levenshtein_distance=options[LEVENSHTEIN_DISTANCE_PARAM])

    reprs = []
    for entity in entities:
        string_repr = entity.to_string(coref_prediction['document'])
        reprs.append(string_repr)

    normalized_verbs = collect_normalized_verbs(doc_normalized_verbs, entities, coref_prediction['document'])

    # df = json_normalize(normalized_verbs)
    # df = df.set_index(["ARG0.entity", "ARG1.entity"])
    # df.sort_index(inplace=True)

    edges, entity_set = create_edges(normalized_verbs)
    nodes = create_nodes(entities, coref_prediction['document'], entity_set)

    return entities, coref_prediction['document'], nodes, edges


def write_graph(nodes, edges, path):
    with open(path, 'w') as f:
        json.dump(dict(nodes=nodes, edges=edges), f)


def write_csv(df, path):
    output = []
    with open(path + '.tsv', 'w') as f:
        writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_ALL)
        writer.writerow(
            ['Subject',
             "S index",
            "s mention",
            "Verb",
             "o mention",
            "Object",
            "o mention",
            "Modifier"]
        )
        for arg0_e, new_df in df.groupby(level=0):
            for arg1_e, row in new_df.iterrows():
                output_row = []
                arg0_e_str = row['ARG0.entity_str']
                # only add string representation of the entity one time
                # if not len(output) or output[-1][1] != arg0_e:
                output_row.append(arg0_e_str)
                # else:
                #     output_row.append('')
                output_row.append(arg0_e)
                output_row.append(row["ARG0.string"])
                output_row.append(row['VERB.string'])
                output_row.append(row['ARG1.string'])
                output_row.append(row['ARG1.entity_str'])
                output_row.append(row['ARG2.string'])
                output.append(output_row)
                writer.writerow(row)


def run_analysis(text, path):
    df, entities, document, nodes, edges = open_ie_with_coreference(text)
    # write_csv(df, path)
    write_graph(nodes, edges, path)


# if __name__ == '__main__':
#     text1 = "It is likely that a multicomponent, adaptive immune system arose with the first vertebrates, as invertebrates do not generate lymphocytes or an antibody-based humoral response. Many species, however, utilize mechanisms that appear to be precursors of these aspects of vertebrate immunity. Immune systems appear even in the structurally most simple forms of life, with bacteria using a unique defense mechanism, called the restriction modification system to protect themselves from viral pathogens, called bacteriophages. Prokaryotes also possess acquired immunity, through a system that uses CRISPR sequences to retain fragments of the genomes of phage that they have come into contact with in the past, which allows them to block virus replication through a form of RNA interference. Offensive elements of the immune systems are also present in unicellular eukaryotes, but studies of their roles in defense are few."
#     text2 = "When a T-cell encounters a foreign pathogen, it extends a vitamin D receptor. This is essentially a signaling device that allows the T-cell to bind to the active form of vitamin D, the steroid hormone calcitriol. T-cells have a symbiotic relationship with vitamin D. Not only does the T-cell extend a vitamin D receptor, in essence asking to bind to the steroid hormone version of vitamin D, calcitriol, but the T-cell expresses the gene CYP27B1, which is the gene responsible for converting the pre-hormone version of vitamin D, calcidiol into the steroid hormone version, calcitriol. Only after binding to calcitriol can T-cells perform their intended function. Other immune system cells that are known to express CYP27B1 and thus activate vitamin D calcidiol, are dendritic cells, keratinocytes and macrophages."
#     run_analysis(text1, 'text1.json')
#     run_analysis(text2, 'text2.json')
#
#     # verbs, entities, document = open_ie_with_coreference(text2)
#     # with open('text2-openie.tsv', 'w') as f:
#     #     writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_ALL)
#     #     writer.riterow(
#     #         ['Subject',
#     #          "S index",
#     #         "s mention",
#     #         "Verb",
#     #         "Object",
#     #         "o mention",
#     #         "Modifier"]
#     #     )
#     #
#     #     for row in verbs:
#     #         writer.writerow(row)

