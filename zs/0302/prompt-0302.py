## no deduplicate  but with clean json string
import os, time
import re
import csv
import torch
import pandas as pd
import requests
import numpy as np

os.environ["GROQ_API_KEY"] = "your api"
from groq import Groq
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
from difflib import SequenceMatcher

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
model = SentenceTransformer('all-MiniLM-L6-v2')
model = model.to('cpu')


def clean_json_string(json_string):
    """
    Attempts to clean and repair malformed JSON strings.
    """
    json_string = re.sub(r'(?<![\w])"\'|\'(?![\w])', '"', json_string)
    json_string = re.sub(r'(?<![\w])\'|\'(?![\w])', '"', json_string)

    json_string = json_string.replace("“", '"').replace("”", '"')

    json_string = re.sub(r',\s*([\]}])', r'\1', json_string)

    # Add missing commas between array elements
    json_string = re.sub(r'\]\s*\[', '],[', json_string)
    json_string = re.sub(r'}\s*{', '},{', json_string)

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
        return True
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error at position {e.pos}:")
        print(f"Problem area: {json_string[max(0, e.pos - 20):min(len(json_string), e.pos + 20)]}")
        print(f"Error message: {str(e)}")
        return False


##############################
# --- Phase 1: Entity Extraction Only

def extract_entities_only(abstract, doc_id, max_retries=1):
    partial_entities = []
    prompt = f"""
        Please extract ONLY the entities from the following text in strict JSON format.
        Output must look like:
        {{
          "entities": [
            ["Entity Text", "Entity Type"],
            ["Another Entity", "Another Type"]
          ]
        }}
        Do NOT include "relationships". Only the 'entities' key is expected.

        Text (Document {doc_id}):
        {abstract}
    """
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
                temperature=0.0,
                max_tokens=1024,
                top_p=1.0,
                seed=42
            )
            completion_text = response.choices[0].message.content
            print(f"Document {doc_id} - Raw LLM Response (Attempt {attempt + 1}):\n{completion_text}")

            json_match = re.search(r'\{.*\}', completion_text, re.DOTALL)
            if not json_match:
                print(f"Error: JSON not found in Document {doc_id} response. Retrying...")
                continue

            json_text = json_match.group(0).strip()
            json_text = clean_json_string(json_text)
            print(f"Document {doc_id} - Cleaned JSON (Attempt {attempt + 1}):\n{json_text}")

            data = json.loads(json_text)
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
        time.sleep(1)

    print(f"Failed to extract entities for Document {doc_id} after {max_retries} attempts.")
    return partial_entities


##############################
# --- Phase 2: Relationship Building from Known Entities; improve the relatioinship build that source and taget has to be among the extracted entitties

def is_similar(a, b, threshold=0.95):
    return SequenceMatcher(None, a, b).ratio() >= threshold


def is_valid_relationship(src, tgt, known_texts):
    src_norm = normalize_text(src)
    tgt_norm = normalize_text(tgt)
    valid_src = any(is_similar(src_norm, known) for known in known_texts)
    valid_tgt = any(is_similar(tgt_norm, known) for known in known_texts)

    if valid_src and valid_tgt and src_norm != tgt_norm:
        return True

    print(f"Potential issue: Relationship [{src}] -> [{tgt}] missing entity match.")
    return False

##delete this '    You are an expert in infectious diseases and epidemiology. Extract **only meaningful relationships** from the text.' in the relation build

def build_relationships_from_entities(abstract, doc_id, known_entities, max_retries=1):
    partial_relationships = []
    known_texts = {normalize_text(e["text"]) for e in known_entities}
    known_entity_list = json.dumps([e["text"] for e in known_entities], indent=2)

    prompt = f"""
    We have the following known entities (only these are allowed):
    {known_entity_list}

    From the following text, identify relationships ONLY between the provided entities.
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

    Text (Document {doc_id}):
    {abstract}
    """
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
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
                # Attempt to salvage partial relationships via regex:
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
    print(f"No relationships or partial data for Document {doc_id} after {max_retries} attempts.")
    return partial_relationships


#############################
# --- Post-Processing / Knowledge Graph
def get_latin_name_from_gbif(common_name):
    """
    Query the GBIF API to map a common name to its scientific (Latin) name.
    """
    # url = "https://api.gbif.org/v1/species/match"
    return None, None


def get_latin_name_from_wikidata(common_name):
    """
    Query Wikidata to find the scientific (Latin) name for a given common name.
    This query uses a UNION to look for matches in either the 'common name' (P1843)
    or the English rdfs:label.
    """
    # sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    # query = f"""
    # SELECT ?scientificName WHERE {{
    #   {{
    #     ?item wdt:P1843 ?name .
    #     ?item wdt:P225 ?scientificName .
    #     FILTER(CONTAINS(LCASE(?name), LCASE("{common_name}")))
    #   }}
    #   UNION
    #   {{
    #     ?item rdfs:label ?label .
    #     ?item wdt:P225 ?scientificName .
    #     FILTER(CONTAINS(LCASE(?label), LCASE("{common_name}")))
    #     FILTER(LANG(?label) = "en")
    #   }}
    # }}
    # LIMIT 1
    # """
    # sparql.setQuery(query)
    # sparql.setReturnFormat(JSON)
    # try:
    #     results = sparql.query().convert()
    #     bindings = results["results"]["bindings"]
    #     if bindings:
    #         return bindings[0]["scientificName"]["value"], "Wikidata"
    # except Exception as e:
    #     print(f"Error querying Wikidata for '{common_name}': {e}")
    return None, None


def get_latin_name_from_gnr(common_name):
    """
    Query the Global Names Resolver (GNR) API to map a common name to a scientific (Latin) name.
    """
    # url = "https://resolver.globalnames.org/name_resolvers.json"
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

    for entity in undefined_entities:
        entity_text = entity["text"]
        prompt = f"""
                You have one entity: {entity_text}.
                Please assign the most appropriate type for it based on your knowledge,
                but do NOT invent any new information not in the text. Output JSON:
                {{
                  "entity": "{entity_text}",
                  "type": "Your_Type_Here"
                }}
        """
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
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
        except Exception as e:
            print(f"Error reassigning entity type for {entity_text}: {e}")
    return entities


def get_embedding(text):
    """Generate an embedding for a given text using Sentence Transformers."""
    return model.encode(text, convert_to_tensor=True).cpu()


def add_embeddings_to_entities(entities):
    """Add embeddings to each entity."""
    for entity in entities:
        entity["embedding"] = get_embedding(entity["text"])


def add_embeddings_to_relationships(relationships):
    """Add embeddings to each relationship."""
    for rel in relationships:
        rel_text = f"{rel['src']} - {rel['relation']} -> {rel['tgt']}"
        rel["embedding"] = get_embedding(rel_text)


def normalize_text(text):
    if isinstance(text, list):
        text = " ".join(map(str, text))
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove special characters
    return text


def is_similar(a, b, threshold=0.9):
    return SequenceMatcher(None, a, b).ratio() >= threshold


def deduplicate_entities_list(entities, similarity_threshold=0.9):
    """
    Wraps deduplicate_entities to return a list of unique entities.
    """
    canonical_dict = deduplicate_entities(entities, similarity_threshold)
    return list(canonical_dict.values())


def deduplicate_entities(entities, similarity_threshold=0.9):
    canonical_entities = {}
    next_id = 1

    for e in entities:
        e["doc_id"] = int(e["doc_id"])
        e_norm = normalize_text(e["text"])
        found = False

        for cid, ce in canonical_entities.items():
            ce_norm = normalize_text(ce["text"])

            if is_similar(e_norm, ce_norm, threshold=similarity_threshold):
                ce.setdefault("doc_ids", set()).add(e["doc_id"])
                found = True
                break

            if (
                    ce.get("latin_name") and e.get("latin_name") and
                    normalize_text(ce["latin_name"]) == normalize_text(e["latin_name"])
            ):
                ce.setdefault("doc_ids", set()).add(e["doc_id"])
                found = True
                break

            # 3) Finally, compare embeddings if both have them
            if "embedding" in ce and "embedding" in e:
                emb1 = np.array(ce["embedding"]).reshape(1, -1)
                emb2 = np.array(e["embedding"]).reshape(1, -1)
                sim = cosine_similarity(emb1, emb2)[0][0]
                if sim > similarity_threshold:
                    ce.setdefault("doc_ids", set()).add(e["doc_id"])
                    found = True
                    break

        if not found:
            e["doc_ids"] = {e["doc_id"]}
            canonical_entities[next_id] = e
            next_id += 1

    return canonical_entities


def update_relationships_with_ids(relationships, canonical_entities):
    """
    For each relationship, attempt to map src/tgt to canonical entity IDs.
    If not found, store empty IDs but do NOT drop the relationship.
    """
    norm_to_id = {}
    for cid, ent in canonical_entities.items():
        norm_to_id[normalize_text(ent["text"])] = cid

    updated = []
    for rel in relationships:
        src_norm = normalize_text(rel["src"])
        tgt_norm = normalize_text(rel["tgt"])
        rel["src_id"] = norm_to_id.get(src_norm, "")
        rel["tgt_id"] = norm_to_id.get(tgt_norm, "")
        updated.append(rel)
    return updated


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


def remove_reversed_duplicates_across_docs(relationships):
    """
    Group relationships by the unordered pair of canonical IDs (ignoring doc_id),
    merge their document IDs, and remove duplicates (including reversed duplicates).
    """
    from collections import defaultdict

    grouped = defaultdict(list)
    for rel in relationships:
        # Group by frozenset of src_id and tgt_id so that A->B and B->A fall in the same group
        pair_ids = frozenset([rel["src_id"], rel["tgt_id"]])
        grouped[pair_ids].append(rel)

    final = []
    for pair_ids, rel_list in grouped.items():
        # Discard self-relationships (only one entity in the pair)
        if len(pair_ids) < 2:
            continue

        merged_doc_ids = set()
        for r in rel_list:
            merged_doc_ids.add(r["doc_id"])

        representative = rel_list[0].copy()
        representative["doc_id"] = ";".join(map(str, sorted(merged_doc_ids)))
        final.append(representative)
    return final


def fallback_relationships_from_entities(doc_entities, doc_id, max_retries=2):
    """
    Given a list of extracted entities for a document, call the LLM with a fallback prompt
    to produce at least one relationship among those entities.
    """
    known_entity_list = json.dumps([e["text"] for e in doc_entities], indent=2)

    fallback_prompt = f"""
    We have the following extracted entities (only these are allowed):
    {known_entity_list}

    Please output at least one relationship among these entities in strict JSON format.
    The output must be in the following format:
    {{
      "relationships": [
          ["Entity A", "relation", "Entity B"]
      ]
    }}
    Ensure that:
    - Only the entities provided above are used.
    - Do not produce any new or modified entity strings.
    - Do not output any relationship where the source and target are the same entity.
    """
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": fallback_prompt}],
                model="llama3-8b-8192",
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

    entities.extend(new_entities)
    return entities


#########Main
def main():
    df = pd.read_csv("validation_100.csv")
    abstracts = df["title_abs"].iloc[1:101].tolist()
    all_entities = []
    all_relationships = []

    for idx, abstract in enumerate(abstracts):
        doc_id = idx + 1
        print(f"\n=== Processing Document {doc_id} ===")

        doc_entities = extract_entities_only(abstract, doc_id)
        doc_entities = reassign_undefined_types_with_llm(doc_entities)
        doc_entities = post_process_entities(doc_entities)
        add_embeddings_to_entities(doc_entities)
        doc_entities = deduplicate_entities_list(doc_entities)
        all_entities.extend(doc_entities)

        doc_relationships = build_relationships_from_entities(abstract, doc_id, doc_entities)
        add_embeddings_to_relationships(doc_relationships)

        if not doc_relationships:
            print(f"Document {doc_id} has no relationships. Calling fallback LLM to create relationship.")
            doc_relationships = fallback_relationships_from_entities(doc_entities, doc_id)
            if not doc_relationships:
                print(f"Fallback LLM did not produce any relationships for Document {doc_id}.")

        all_relationships.extend(doc_relationships)


    all_entities = augment_entities_with_relationship_endpoints(all_entities, all_relationships)

    all_entities = recover_missing_entities(all_relationships, all_entities)

    all_entities = reassign_undefined_types_with_llm(all_entities)

    canonical_entities_dict = deduplicate_entities(all_entities)

    updated_relationships = update_relationships_with_ids(all_relationships, canonical_entities_dict)

    final_relationships = remove_reversed_duplicates_across_docs(updated_relationships)

    today_str = datetime.now().strftime("%m%d")
    entities_csv_path = f"entities_{today_str}_prompt5.csv"
    relationships_csv_path = f"relationships_{today_str}_prompt5.csv"

    try:
        with open(entities_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["entity_id", "entity", "type", "latin_name", "doc_ids"])
            for cid, ent in canonical_entities_dict.items():
                doc_ids_list = sorted(ent.get("doc_ids", []))
                writer.writerow([
                    cid,
                    ent["text"],
                    ent.get("type", ""),
                    ent.get("latin_name", ""),
                    ";".join(str(d) for d in doc_ids_list)
                ])
        print(f"Saved entities to {entities_csv_path}")
    except Exception as e:
        print(f"Error saving entities: {e}")

    try:
        with open(relationships_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["source_id", "source_text", "target_id", "target_text", "relation_type", "doc_id"])
            for rel in final_relationships:
                writer.writerow([
                    rel.get("src_id", ""),
                    rel.get("src", ""),
                    rel.get("tgt_id", ""),
                    rel.get("tgt", ""),
                    rel.get("relation", ""),
                    rel.get("doc_id", "")
                ])
        print(f"Saved relationships to {relationships_csv_path}")
    except Exception as e:
        print(f"Error saving relationships: {e}")


if __name__ == "__main__":
    main()

