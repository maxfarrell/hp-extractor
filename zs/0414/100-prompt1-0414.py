### use llama 70b
## no deduplicate  but with clean json string
## this version has no merge embedding and check similarity and no entitiy shows multiple doc, relation shows in multiple doc
import os, time
import re
import csv
import pandas as pd
import requests
import numpy as np

os.environ["GROQ_API_KEY"] = "api"
from groq import Groq
from datetime import datetime
#from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

from collections import Counter, defaultdict


def clean_json_string(json_string):
    """
    Attempts to clean and repair malformed JSON strings.
    """

    json_string = re.sub(r'(?<![\w])"\'|\'(?![\w])', '"', json_string)
    json_string = re.sub(r'(?<![\w])\'|\'(?![\w])', '"', json_string)

    json_string = json_string.replace("“", '"').replace("”", '"')

    # Remove trailing commas before closing brackets/braces
    json_string = re.sub(r',\s*([\]}])', r'\1', json_string)

    # Add missing commas between array elements
    json_string = re.sub(r'\]\s*\[', '],[', json_string)
    json_string = re.sub(r'}\s*{', '},{', json_string)

    # Ensure the JSON string starts and ends correctly
    json_string = json_string.strip()
    if not json_string.startswith("{"):
        json_string = "{" + json_string
    if not json_string.endswith("}"):
        json_string += "}"
    return json_string


def validate_json_structure(json_string):
    """
    Validates the structure of the JSON string to ensure it meets the expected format.
    """
    try:
        data = json.loads(json_string)
        if not isinstance(data, dict):
            print("Error: Root is not a dictionary")
            return False
        if "entities" not in data:
            print("Error: Missing 'entities' key")
            return False
        # In this 2-phase approach, we might not expect "relationships" in the entity extraction step.
        return True
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error at position {e.pos}:")
        print(f"Problem area: {json_string[max(0, e.pos - 20):min(len(json_string), e.pos + 20)]}")
        print(f"Error message: {str(e)}")
        return False


### add this for more than 3 attempt not consider json
def parse_bracketed_arrays_for_entities(llm_text, doc_id):
    """
    Fallback parser: finds bracketed arrays of length 2 in the LLM text.
    Returns a list of dicts like:
      [{"text": "...", "type": "...", "doc_id": doc_id}, ...]
    Example match: ["entity text", "entity type"]
    """
    pattern = r'\[\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\]'
    matches = re.finditer(pattern, llm_text)
    entities = []
    for match in matches:
        text_val = match.group(1).strip()
        type_val = match.group(2).strip()
        entities.append({"text": text_val, "type": type_val, "doc_id": doc_id})
    return entities


##############################
# --- Phase 1: Entity Extraction Only
##############################

def fallback_entity_parsing(json_text):
    """Emergency entity extraction from malformed JSON"""
    entities = []
    # Find all potential entity arrays using regex
    matches = re.finditer(r'\[?\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\]?', json_text)
    for match in matches:
        try:
            entity_text = match.group(1).strip()
            entity_type = match.group(2).strip()
            if entity_text and entity_type:
                entities.append([entity_text, entity_type])
        except:
            continue
    return entities


def extract_entities_only(abstract, doc_id, max_retries=1):
    partial_entities = []
    last_llm_response = ""  # Track the last LLM output

    example_abstract = (
        "Erysipelothrix rhusiopathiae infection in chukar partridge (Alectoris graeca). Erysipelas was diagnosed in chukar partridges (Alectoris graeca) kept as hunting stock. Mortality was 265 of 500 (53%) over a period of one week."
    )

    example_output = """
                {
                 "entities": [
                   ["Erysipelothrix rhusiopathiae", "Pathogen"]
                   ["chukar partridge", "Common name"]
                   ["Alectoris graeca", "Host"]
                   [“Erysipelas”, “Disease”]
                   [“hunting stock”, “Animal source”]
                   ["Mortality", "Symptom"]
                   ["one week", "Duration"]
                   [“265”, “Number of individuals that died”]
                   [“500”, “Number of individuals infected”]
                   ["53%", "Proportion of individuals that died"]

                 ],
                 "relationships": [
                   ["Erysipelothrix rhusiopathiae", "infects", "Alectoris graeca"]
                   ["Alectoris graeca", "hosts", "Erysipelothrix rhusiopathiae"]
                   ["chukar partridge", "common name of", "Alectoris graeca"]
                   ["Alectoris graeca", "Latin name of", "chukar partridge"]
                   [“Erysipelothrix rhusiopathiae”, “causes”, “Erysipelas”]
                   ["chukar partridge", “suffered from”, Mortality]
                   ["Erysipelothrix rhusiopathiae", “causes”, “Mortality]
                   [“265 of 500 (53%), “measurement”, “Mortality”]
                   ["one week", "duration of observation", "Mortality"]
                 ]
                }
                """

    prompt = f"""
                    You are an expert in epidemiology, infectious diseases, and ecology. Extract all entities and relationships mentioned in the text.

                    This extraction should mention at least one “infects” relation with a “Pathogen” entity that “infects” a “Host” entity. This extraction should mention at least one “hosts” relation with a “Host” entity that “hosts” a “Pathogen” entity. Pathogens can include bacteria, viruses, helminths, protozoa, or fungi. For both host and pathogen names, report the common name and scientific Latin binomial name if available.

                    Entities should represent organisms, species, locations, diseases, tissues, pathogens, events, measurements, units, processes, interactions, environments, properties, and any relevant concepts in addition to the examples given.

                    Relationships should capture interactions such as  "infects," "hosts," "lives in," "found in," "detected by," "affected by", “causes” or other relevant relations in addition to these examples.

                    This has to be Unbiased extraction - pull out all entities and relations in a strict JSON format.
                    Each entity should be represented as ["text", "type"], and each relationship as ["src", "relation", "tgt"], with exactly three elements for relationships.

                    When expressing relationships between entities:
                        - Do not use phrases like "exists between" or "relationship between"
                        - Instead, directly state the relationship from one entity to another
                        - Example: Instead of ["Relationship", "exists between", "A and B"]
                                  Write as ["A", "has relationship with", "B"]

                    Let's think step by step and think hard about this extraction problem. Use only information present in the text provided in this prompt.  Do not generate any entities or relations that are not in the provided text.

                    Format output as strict JSON



                Example:

                Abstract:
                {example_abstract}

                Output:
                {example_output}

                Now, for Document {doc_id}, please extract entities and relationships in the same format:

                Abstract:
                {abstract}
            """
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-70b-8192",
                temperature=0.0,
                max_tokens=1024,
                top_p=1.0,
                seed=42
            )
            completion_text = response.choices[0].message.content
            last_llm_response = completion_text  # Store the raw LLM output in case JSON fails

            print(f"Document {doc_id} - Raw LLM Response (Attempt {attempt + 1}):\n{completion_text}")

            json_match = re.search(r'\{.*\}', completion_text, re.DOTALL)
            if not json_match:
                print(f"Error: JSON not found in Document {doc_id} response. Retrying...")
                continue

            json_text = json_match.group(0).strip()
            json_text = clean_json_string(json_text)
            print(f"Document {doc_id} - Cleaned JSON (Attempt {attempt + 1}):\n{json_text}")

            try:
                data = json.loads(json_text)
            except json.JSONDecodeError as e:
                print(f"JSON parse failed, attempting fallback parsing: {e}")
                data = {"entities": fallback_entity_parsing(json_text)}

            raw_entities = data.get("entities", [])
            entities = [
                {"text": ent[0], "type": ent[1], "doc_id": doc_id}
                for ent in raw_entities
                if isinstance(ent, list) and len(ent) == 2
            ]
            partial_entities = entities
            if entities:
                return entities

        except Exception as e:
            print(f"Unexpected error extracting entities for Document {doc_id}: {e}")
            # If an error occurs, try fallback on the partial JSON text
            partial_entities += fallback_entity_parsing(last_llm_response)

        time.sleep(1)

    print(f"Failed to extract entities for Document {doc_id} after {max_retries} attempts.")

    # FINAL bracketed-array fallback on the LAST LLM RESPONSE
    # (re-using your fallback_entity_parsing, which also does bracket scanning)
    fallback_ents = fallback_entity_parsing(last_llm_response)
    if fallback_ents:
        print(f"Bracket fallback found {len(fallback_ents)} entities for doc {doc_id} after final attempt.")
        return [
            {"text": e[0], "type": e[1], "doc_id": doc_id}
            for e in fallback_ents
        ]

    # If fallback also yields nothing, return whatever partial we accumulated
    return partial_entities


##############################
# --- Phase 2: Relationship Building from Known Entities; improve the relatioinship build that source and taget has to be among the extracted entitties
## update source and target cannot be same otherwise has the problem : {"Perch rhabdovirus", "is classified as", "Perch rhabdovirus"}

### totally discard relation if one entity is missing

##
def is_valid_relationship(src, tgt, known_texts):
    src_norm = normalize_text(src)
    tgt_norm = normalize_text(tgt)
    valid_src = src_norm in known_texts
    valid_tgt = tgt_norm in known_texts
    if valid_src and valid_tgt and src_norm != tgt_norm:
        return True

    print(f"Potential issue: Relationship [{src}] -> [{tgt}] missing entity match.")
    return False



def build_relationships_from_entities(abstract, doc_id, known_entities, max_retries=1):
    partial_relationships = []
    # Build a set of normalized names from the known_entities for filtering.
    known_texts = {normalize_text(e["text"]) for e in known_entities}
    # Define known_entity_list using json.dumps so that the names appear exactly as extracted.
    known_entity_list = json.dumps([e["text"] for e in known_entities], indent=2)

    # Define an example known entity list and example relationship output.
    example_known_entities = """
    {
      "entities": [
        ["Erysipelothrix rhusiopathiae", "Pathogen"],
        ["chukar partridge", "Common name"],
        ["Alectoris graeca", "Host"],
        ["Erysipelas", "Disease"],
        ["hunting stock", "Animal source"],
        ["Mortality", "Symptom"],
        ["one week", "Duration"],
        ["265", "Number of individuals that died"],
        ["500", "Number of individuals infected"],
        ["53%", "Proportion of individuals that died"]
      ]
    }
    """
    example_relationship_output = """
    {
      "relationships": [
        ["Erysipelothrix rhusiopathiae", "infects", "Alectoris graeca"],
        ["Alectoris graeca", "hosts", "Erysipelothrix rhusiopathiae"],
        ["chukar partridge", "common name of", "Alectoris graeca"],
        ["Alectoris graeca", "Latin name of", "chukar partridge"],
        ["Erysipelothrix rhusiopathiae", "causes", "Erysipelas"],
        ["chukar partridge", "suffered from", "Mortality"],
        ["Erysipelothrix rhusiopathiae", "causes", "Mortality"],
        ["265 of 500 (53%)", "measurement", "Mortality"],
        ["one week", "duration of observation", "Mortality"]
      ]
    }
    """
    prompt = f"""
    You are an expert in infectious diseases and epidemiology. Extract only meaningful relationships from the text.

    We have the following known entities (only these are allowed):
    {known_entity_list}

    For example, here is an example known entity list:
    {example_known_entities}

    And here is how the relationships should be formatted exactly:
    {example_relationship_output}

    From the following text (Document {doc_id}), identify relationships ONLY between the provided entities.
    Return the output strictly as JSON with key "relationships", like:
    {{
      "relationships": [
        ["Entity A", "relation", "Entity B"],
        ...
      ]
    }}

    Ensure that:
    - Both "Entity A" and "Entity B" are exactly as provided above.
    - Do not output any relationship where the source and target are the same entity.
    - The relationship labels must be consistent in their formatting (i.e. use the same casing, punctuation, and wording as shown in the example).

    This relationship build should mention at least one “infects” relation with a “Pathogen” entity that “infects” a “Host” entity. This should mention at least one “hosts” relation with a “Host” entity that “hosts” a “Pathogen” entity. Pathogens can include bacteria, viruses, helminths, protozoa, or fungi. For both host and pathogen names, report the common name and scientific Latin binomial name if available.

                    Entities should represent organisms, species, locations, diseases, tissues, pathogens, events, measurements, units, processes, interactions, environments, properties, and any relevant concepts in addition to the examples given.

                    Relationships should capture interactions such as  "infects," "hosts," "lives in," "found in," "detected by," "affected by", “causes” or other relevant relations in addition to these examples.

                    This has to be Unbiased extraction - pull out all entities and relations in a strict JSON format.
                    Each entity should be represented as ["text", "type"], and each relationship as ["src", "relation", "tgt"], with exactly three elements for relationships.

                    When expressing relationships between entities:
                        - Do not use phrases like "exists between" or "relationship between"
                        - Instead, directly state the relationship from one entity to another
                        - Example: Instead of ["Relationship", "exists between", "A and B"]
                                  Write as ["A", "has relationship with", "B"]

                    Let's think step by step and think hard about this extraction problem. Use only information present in the text provided in this prompt.  Do not generate any entities or relations that are not in the provided text.


    Text (Document {doc_id}):
    {abstract}
    """
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-70b-8192",
                temperature=0.0,
                max_tokens=1024,
                top_p=1.0,
                seed=42
            )
            completion_text = response.choices[0].message.content
            print(f"Document {doc_id} - Relationship Raw Response (Attempt {attempt + 1}):\n{completion_text}")
            json_match = re.search(r'\{.*\}', completion_text, re.DOTALL)
            if not json_match:
                print(f"Error: No JSON found for relationships in Document {doc_id}. Retrying...")
                continue
            json_text = clean_json_string(json_match.group(0).strip())
            try:
                data = json.loads(json_text)
            except json.JSONDecodeError as e:
                print(f"JSON decode error in relationship building for Document {doc_id}: {e}")
                partial = re.findall(r'\[[^\]]+\]', json_text)
                rels = []
                for r in partial:
                    try:
                        items = json.loads(r)
                        if isinstance(items, list) and len(items) == 3:
                            if is_valid_relationship(items[0], items[2], known_texts):
                                rels.append(
                                    {"src": items[0], "relation": items[1].lower(), "tgt": items[2], "doc_id": doc_id})
                    except Exception:
                        continue
                if rels:
                    return rels
                else:
                    return partial_relationships
            raw_relationships = data.get("relationships", [])
            relationships = []
            for rel in raw_relationships:
                if isinstance(rel, list) and len(rel) == 3:
                    src, relation, tgt = rel[0], rel[1].lower(), rel[2]
                    if is_valid_relationship(src, tgt, known_texts):
                        relationships.append({"src": src, "relation": relation, "tgt": tgt, "doc_id": doc_id})
                    else:
                        print(f"Discarding relationship {rel} because one endpoint is not in the extracted entities.")
            partial_relationships = relationships
            return relationships
        except Exception as e:
            print(f"Unexpected error building relationships for Document {doc_id}: {e}")
        time.sleep(1)
    return partial_relationships  # Ensure relationships are returned, even if they are empty


#############################
# --- Post-Processing / Knowledge Graph
#############################

def deduplicate_and_unify_types(entities):
    entity_map = defaultdict(list)
    for e in entities:
        entity_map[(e["doc_id"], e["text"])].append(e["type"])

    final_entities = []
    for (doc_id, text), types in entity_map.items():
        most_common_type = Counter(types).most_common(1)[0][0]
        final_entities.append({"text": text, "type": most_common_type, "doc_id": doc_id})
    return final_entities

def get_latin_name_from_gbif(common_name):
    """
    Query the GBIF API to map a common name to its scientific (Latin) name.
    """

    return None, None


def get_latin_name_from_wikidata(common_name):
    """
    Query Wikidata to find the scientific (Latin) name for a given common name.
    This query uses a UNION to look for matches in either the 'common name' (P1843)
    or the English rdfs:label.
    """

    return None, None


def get_latin_name_from_gnr(common_name):
    """
    Query the Global Names Resolver (GNR) API to map a common name to a scientific (Latin) name.
    """

    return None, None


def map_common_to_latin(entity_text):
    """
    Map a common name to its Latin name by trying GBIF, then GNR, then Wikidata.
    Records the source used.
    """
    latin_name, source = get_latin_name_from_gbif(entity_text)
    if not latin_name:
        latin_name, source = get_latin_name_from_gnr(entity_text)
    if not latin_name:
        latin_name, source = get_latin_name_from_wikidata(entity_text)
    if latin_name:
        return latin_name, source
    else:
        return entity_text, "None"


def post_process_entities(entities):
    """
    If an entity is type 'host', 'disease', 'pathogen', or 'virus',
    add a 'latin_name' and record which source provided it.
    """
    for entity in entities:
        if entity["type"].lower() in ["host", "disease", "pathogen", "virus"]:
            latin_name, source = map_common_to_latin(entity["text"])
            entity["latin_name"] = latin_name
            entity["latin_name_source"] = source
    return entities


def reassign_undefined_types_with_llm(entities):
    """
    If an entity's type is 'Undefined', reassign it via an LLM prompt.
    """
    undefined_entities = [e for e in entities if e.get("type", "").lower() == "undefined"]
    if not undefined_entities:
        return entities

    # Optional: Define an example abstract and output as separate variables if you want to include them.
    example_abstract = "Erysipelothrix rhusiopathiae infection in chukar partridge (Alectoris graeca). Erysipelas was diagnosed in chukar partridges (Alectoris graeca) kept as hunting stock. Mortality was 265 of 500 (53%) over a period of one week."

    for entity in undefined_entities:
        entity_text = entity["text"]
        prompt = f"""
        You are an expert in epidemiology, infectious diseases, and ecology. Your task is to assign the most appropriate type to the following entity based solely on the provided text and your domain expertise. Do not invent new information—use only the context given.

        Entity: {entity_text}

        Output in strict JSON format:
        {{
          "entity": "{entity_text}",
          "type": "Your_Type_Here"
        }}

        For reference, here is an example abstract and its extracted entities:

        Example Abstract:
        "{example_abstract}"

        Example Entities Output:
        {{
          "entities": [
            ["Erysipelothrix rhusiopathiae", "Pathogen"],
            ["chukar partridge", "Common name"],
            ["Alectoris graeca", "Host"],
            ["Erysipelas", "Disease"],
            ["hunting stock", "Animal source"],
            ["Mortality", "Symptom"],
            ["one week", "Duration"],
            ["265", "Number of individuals that died"],
            ["500", "Number of individuals infected"],
            ["53%", "Proportion of individuals that died"]
          ]
        }}
        """
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-70b-8192",
                temperature=0.0,
                max_tokens=512,
                top_p=1.0,
                seed=42
            )
            completion_text = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', completion_text, re.DOTALL)
            if json_match:
                json_text = clean_json_string(json_match.group(0).strip())
                data = json.loads(json_text)
                new_label = data.get("type", "Undefined")
                entity["type"] = new_label
            else:
                print(f"No JSON found in response for entity: {entity_text}")
        except Exception as e:
            print(f"Error reassigning entity type for {entity_text}: {e}")
    return entities

### improve the normalise text
def normalize_text(text):
    if isinstance(text, list):
        text = " ".join(map(str, text))
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove special characters
    return text



def get_suspicious_types(entities):
    type_counts = Counter(e["type"].lower() for e in entities)
    suspicious_types = set()
    for e in entities:
        t = e["type"].lower()
        if (
            type_counts[t] < 3
            or any(word in t for word in ["of", "with", "in", "by", "from", "at", "on", "for", "to", "among", "between", "over",
                                          "below", "above"])
            or len(t.split()) > 2
        ):
            suspicious_types.add(t)
    return suspicious_types


### if a relationship is missing an entity, attempt a fallback entity extraction before discarding
def recover_missing_entities(relationships, known_entities):
    """
    If a relationship contains an entity that was not extracted, attempt to recover it.
    """
    known_texts = {normalize_text(e["text"]) for e in known_entities}
    recovered_entities = []

    for rel in relationships:
        for endpoint in [rel["src"], rel["tgt"]]:
            norm_ep = normalize_text(endpoint)
            if norm_ep not in known_texts:
                print(f"Recovering missing entity: {endpoint}")
                recovered_entities.append({"text": endpoint, "type": "Undefined", "doc_id": rel["doc_id"]})
                known_texts.add(norm_ep)

    known_entities.extend(recovered_entities)
    return known_entities



def fallback_relationships_from_entities(doc_entities, doc_id, max_retries=2):
    """
    Given a list of extracted entities for a document, call the LLM with a fallback prompt
    to produce at least one relationship among those entities.
    """
    # Build a strict JSON list of entity texts.
    known_entity_list = json.dumps([e["text"] for e in doc_entities], indent=2)

    fallback_prompt = f"""
        We have the following known entities (only these are allowed):
        {known_entity_list}

        From the following text, identify relationships ONLY between the provided entities.
        This has to be unbiased.

        Let's think step by step and think hard about this task, Use only information present in the text provided.
        Do not generate any relations that are not in the provided text
        Return the output strictly as JSON with key "relationships", like:
        {{
          "relationships": [
            ["Entity A", "relation", "Entity B"],
            ...
          ]
        }}
        Ensure that:
        - Both "Entity A" and "Entity B" are exactly as provided above.
        - Do not output any relationship where the source and target are the same entity.
        - The relationship must be consistent in their formatting (for example, use the same casing, punctuation and wording)

        Please output at least one relationship among these entities in strict JSON format.

        """
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": fallback_prompt}],
                model="llama3-70b-8192",
                temperature=0.0,
                max_tokens=1024,
                top_p=1.0,
                seed=42
            )
            completion_text = response.choices[0].message.content
            print(f"Document {doc_id} - Fallback Relationship Response (Attempt {attempt + 1}):\n{completion_text}")
            json_match = re.search(r'\{.*\}', completion_text, re.DOTALL)
            if not json_match:
                print(f"Error: JSON not found in fallback response for Document {doc_id}. Retrying fallback...")
                continue
            json_text = clean_json_string(json_match.group(0).strip())
            data = json.loads(json_text)
            fallback_rels = data.get("relationships", [])
            # Filter the fallback relationships for valid ones
            valid_fallbacks = []
            known_texts = {normalize_text(e["text"]) for e in doc_entities}
            for rel in fallback_rels:
                if isinstance(rel, list) and len(rel) == 3:
                    src, relation, tgt = rel[0], rel[1].lower(), rel[2]
                    if is_valid_relationship(src, tgt, known_texts):
                        valid_fallbacks.append({"src": src, "relation": relation, "tgt": tgt, "doc_id": doc_id})
            if valid_fallbacks:
                return valid_fallbacks
        except Exception as e:
            print(f"Error in fallback_relationships_from_entities for Document {doc_id}: {e}")
        time.sleep(1)
    return []


def augment_entities_with_relationship_endpoints(entities, relationships):
    """
    Ensures that all relationship endpoints exist as entities.
    If missing, adds the entity with type "Undefined".
    """
    existing = {normalize_text(e["text"]) for e in entities}
    new_entities = []

    for rel in relationships:
        for endpoint in [rel["src"], rel["tgt"]]:
            norm_ep = normalize_text(endpoint)
            if norm_ep not in existing:
                new_entity = {"text": endpoint, "type": "Undefined", "doc_id": rel["doc_id"]}
                new_entities.append(new_entity)
                existing.add(norm_ep)

    # Append new entities before further processing
    entities.extend(new_entities)
    return entities


###check missing data
def check_entities_and_relationships(df, all_entities, all_relationships):
    missing_data_info = []

    for idx, row in df.iterrows():
        abs_id = row['absID']

        entities_for_abs_id = [ent for ent in all_entities if ent['doc_id'] == abs_id]
        relationships_for_abs_id = [rel for rel in all_relationships if rel['doc_id'] == abs_id]

        if not entities_for_abs_id:
            missing_data_info.append((abs_id, 'entities missing'))

        if not relationships_for_abs_id:
            missing_data_info.append((abs_id, 'relationships missing'))

    return missing_data_info

def main():
    df = pd.read_csv("validation_100.csv")
    abstracts = df["title_abs"].tolist()
    abs_ids = df["absID"].tolist()

    all_entities = []
    all_relationships = []

    MAX_DOC_RETRIES = 2

    for idx, abstract in enumerate(abstracts):
        doc_id = abs_ids[idx]
        print(f"\n=== Processing Document {doc_id} ===")

        doc_entities = []
        doc_relationships = []

        for attempt in range(MAX_DOC_RETRIES):
            print(f"--- Attempt {attempt + 1} for Document {doc_id} ---")

            # Extract entities directly
            doc_entities = extract_entities_only(abstract, doc_id)

            # Extract relationships directly using extracted entities
            doc_relationships = build_relationships_from_entities(abstract, doc_id, doc_entities)

            # Fallback if no relationships
            if not doc_relationships:
                print(f"No relationships found. Attempting fallback for Document {doc_id}.")
                doc_relationships = fallback_relationships_from_entities(doc_entities, doc_id)

            if doc_entities or doc_relationships:
                print(f"Extraction succeeded for Document {doc_id} on attempt {attempt + 1}.")
                break
            else:
                print(f"No data extracted for Document {doc_id}. Retrying...")

        # Fallback for Entities (last resort)
        if not doc_entities:
            print(f"No entities found after retries. Using raw abstract for Document {doc_id}.")
            doc_entities = [{"text": abstract, "type": "Raw_Abstract", "doc_id": doc_id}]

        # Fallback for Relationships (last resort)
        if not doc_relationships:
            print(f"No relationships after retries. Using default fallback for Document {doc_id}.")
            fallback_text = doc_entities[0]["text"]
            doc_relationships = [
                {"src": fallback_text, "relation": "no_relationship", "tgt": fallback_text, "doc_id": doc_id}]

        doc_entities = augment_entities_with_relationship_endpoints(doc_entities, doc_relationships)

        suspicious_types = get_suspicious_types(doc_entities)
        for e in doc_entities:
            if e["type"].lower() in suspicious_types:
                e["type"] = "Undefined"

        doc_entities = reassign_undefined_types_with_llm(doc_entities)
        doc_entities = deduplicate_and_unify_types(doc_entities)

        all_entities.extend(doc_entities)
        all_relationships.extend(doc_relationships)

        # Check missing data (optional but helpful)
    missing_data = check_entities_and_relationships(df, all_entities, all_relationships)
    if missing_data:
        for abs_id, issue in missing_data:
            print(f"Warning: Document {abs_id} has missing {issue}.")

    # Save simplified results directly
    today_str = datetime.now().strftime("%m%d")
    entities_csv_path = f"entities_{today_str}_no_merge_single_id_llama70b.csv"
    relationships_csv_path = f"relationships_{today_str}_no_merge_single_id_llama70b.csv"

    # Save Entities
    with open(entities_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["entity_id", "entity", "type", "doc_id"])
        for idx, ent in enumerate(all_entities, 1):
            writer.writerow([idx, ent["text"], ent["type"], ent["doc_id"]])
    print(f"Saved entities to {entities_csv_path}")

    # Save Relationships
    with open(relationships_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["source_text", "target_text", "relation_type", "doc_id"])
        for rel in all_relationships:
            writer.writerow([rel["src"], rel["tgt"], rel["relation"], rel["doc_id"]])
    print(f"Saved relationships to {relationships_csv_path}")

    # Final check if every absID is included
    entity_doc_ids = set(e["doc_id"] for e in all_entities)
    relationship_doc_ids = set(r["doc_id"] for r in all_relationships)

    if missing_entities := set(abs_ids) - entity_doc_ids:
        print("Documents missing in entities CSV:", missing_entities)
    else:
        print("All documents present in entities CSV.")

    if missing_relationships := set(abs_ids) - relationship_doc_ids:
        print("Documents missing in relationships CSV:", missing_relationships)
    else:
        print("All documents present in relationships CSV.")

if __name__ == "__main__":
    main()

"""
Functions to delete entirely:
get_embedding(text)

add_embeddings_to_entities(entities)

add_embeddings_to_relationships(relationships)

deduplicate_entities(entities)

deduplicate_entities_list(entities)

update_relationships_with_ids(relationships, canonical_entities)

remove_reversed_duplicates_across_docs(relationships)

is_similar(a, b, threshold=0.9) (no longer needed)

recover_missing_entities(relationships, known_entities) (no longer needed)

augment_entities_with_relationship_endpoints(entities, relationships) (no longer needed)

"""