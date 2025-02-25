## no deduplicate  but with clean json string
import os, time
import requests
import re
import csv
import pandas as pd
import requests
import numpy as np
os.environ["GROQ_API_KEY"] = "Put your api key"
from groq import Groq
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
model = SentenceTransformer('all-MiniLM-L6-v2')
model = model.to('cpu')  # if no gpu


def clean_json_string(json_string):
    """
    Attempts to clean and repair malformed JSON strings.
    """

    json_string = re.sub(r'(?<![\w])"\'|\'(?![\w])', '"', json_string)
    json_string = re.sub(r'(?<![\w])\'|\'(?![\w])', '"', json_string)

    # Replace curly quotes with straight quotes
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
        return True
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error at position {e.pos}:")
        print(f"Problem area: {json_string[max(0, e.pos - 20):min(len(json_string), e.pos + 20)]}")
        print(f"Error message: {str(e)}")
        return False


##############################
# --- Phase 1: Entity Extraction Only
##############################

def extract_entities_only(abstract, doc_id, max_retries=1):
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
    partial_entities = []

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

            try:
                data = json.loads(json_text)
            except json.JSONDecodeError as e:
                print(f"JSON decode error in entity extraction for Document {doc_id}: {e}")
                partial = re.findall(r'\[[^\]]+\]', json_text)
                ent_list = []
                for r in partial:
                    try:
                        items = json.loads(r)
                        if isinstance(items, list) and len(items) == 2:
                            ent_list.append(items)
                    except Exception:
                        continue
                if ent_list:
                    entities = [{"text": ent[0], "type": ent[1], "doc_id": doc_id} for ent in ent_list]
                    return entities
                else:
                    return partial_entities

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
# --- Phase 2: Relationship Building from Known Entities
##############################

def build_relationships_from_entities(abstract, doc_id, known_entities, max_retries=1):
    """
    Build relationships among known entities.
    Only the entities in 'known_entities' are allowed.
    Returns a list of dicts:
    [{"src": ..., "relation": ..., "tgt": ..., "doc_id": ...}, ...]
    """
    partial_relationships = []
    entity_list_str = "\n".join([f"- {e['text']}" for e in known_entities])
    prompt = f"""
    We have the following known entities (only these are allowed):
    {entity_list_str}

    From the following text, identify relationships ONLY between these known entities.
    Return the output strictly as JSON with key "relationships", like:
    {{
      "relationships": [
        ["Entity A", "relation", "Entity B"],
        ...
      ]
    }}

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
            print(f"Document {doc_id} - Relationship Raw Response (Attempt {attempt+1}):\n{completion_text}")
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
                            rels.append({"src": items[0], "relation": items[1].lower(), "tgt": items[2], "doc_id": doc_id})
                    except Exception:
                        continue
                if rels:
                    return rels
                else:
                    return partial_relationships
            raw_relationships = data.get("relationships", [])
            relationships = [
                {"src": rel[0], "relation": rel[1].lower(), "tgt": rel[2], "doc_id": doc_id}
                for rel in raw_relationships if isinstance(rel, list) and len(rel) == 3
            ]
            partial_relationships = relationships
            return relationships
        except Exception as e:
            print(f"Unexpected error building relationships for Document {doc_id}: {e}")
        time.sleep(1)
    print(f"No relationships or partial data for Document {doc_id} after {max_retries} attempts.")
    return partial_relationships


#############################
# --- Post-Processing / Knowledge Graph
#############################

def get_latin_name_from_itis(common_name):
    """
    Dynamically query to map a common name to a Latin name.
    """
    url = "find better one external web"
    params = {"srchKey": common_name}
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if data.get("commonNames"):
            first_result = data["commonNames"][0]
            return first_result.get("scientificName")
    except Exception as e:
        print(f"Error querying ITIS for '{common_name}': {e}")
    return None


def map_common_to_latin(entity_text):
    """
    If the entity is a 'host', try to map the text to a Latin name.
    """
    latin_name = get_latin_name_from_itis(entity_text)
    return latin_name if latin_name else entity_text


def post_process_entities(entities):
    """
    If an entity is type 'host', add a 'latin_name'.
    """
    for entity in entities:
        if entity["type"].lower() == "host":
            entity["latin_name"] = map_common_to_latin(entity["text"])
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
                        You are an expert in epidemiology, infectious diseases, and ecology. Extract all entities and relationships mentioned in the text.

                        This extraction should mention at least one “infects” relation with a “Pathogen” entity that “infects” a “Host” entity. This extraction should mention at least one “hosts” relation with a “Host” entity that “hosts” a “Pathogen” entity. Pathogens can include bacteria, viruses, helminths, protozoa, or fungi. For both host and pathogen names, report the common name and scientific Latin binomial name if available.

                        Entities should represent organisms, species, locations, diseases, tissues, pathogens, events, measurements, units, processes, interactions, environments, properties, and any relevant concepts in addition to the examples given.

                        Relationships should capture interactions such as  "infects," "hosts," "lives in," "found in," "detected by," "affected by", “causes” or other relevant relations in addition to these examples.

                        This has to be Unbiased extraction - pull out all entities and relations in a strict JSON format.
                        Each entity should be represented as ["text", "type"], and each relationship as ["src", "relation", "tgt"], with exactly three elements for relationships.

                        Let's think step by step and think hard about this extraction problem. Use only information present in the text provided in this prompt.  Do not generate any entities or relations that are not in the provided text.


                        Please assign the most appropriate entity type to the following entity:

                        Entity: {entity_text}

                        Be as specific as possible and choose a category that best describes the given entity use your knowledge. 

                        Output in JSON format:


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
    return text.strip().lower()


def deduplicate_entities(entities, similarity_threshold=0.9):
    """
    Deduplicate entities based on normalized text and embedding similarity.
    Uses a set for doc_ids to avoid duplicates.
    """
    canonical_entities = {}
    next_id = 1

    for e in entities:
        # Force doc_id to be an integer so we don't get '1' and 1 as two distinct values
        e["doc_id"] = int(e["doc_id"])

        e_norm = normalize_text(e["text"])
        found = False

        for cid, ce in canonical_entities.items():
            # Check if normalized text matches
            if normalize_text(ce["text"]) == e_norm:
                ce.setdefault("doc_ids", set()).add(e["doc_id"])
                found = True
                break

            # If embeddings exist, compare similarity
            if "embedding" in ce and "embedding" in e:
                emb1 = np.array(ce["embedding"]).reshape(1, -1)
                emb2 = np.array(e["embedding"]).reshape(1, -1)
                sim = cosine_similarity(emb1, emb2)[0][0]
                if sim > similarity_threshold:
                    ce.setdefault("doc_ids", set()).add(e["doc_id"])
                    found = True
                    break

        if not found:
            # Initialize doc_ids as a set
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


#########

def main():
    df = pd.read_csv("validation_100.csv")
    abstracts = df["title_abstract"].iloc[1:101].tolist()

    all_entities = []
    all_relationships = []

    for idx, abstract in enumerate(abstracts):
        doc_id = idx + 1
        print(f"\n=== Processing Document {doc_id} ===")

        # PHASE 1: Extract Entities Only
        doc_entities = extract_entities_only(abstract, doc_id)
        # Reassign undefined types
        doc_entities = reassign_undefined_types_with_llm(doc_entities)
        # Post-process (e.g., host => add latin_name)
        doc_entities = post_process_entities(doc_entities)
        # Add embeddings to doc entities
        add_embeddings_to_entities(doc_entities)

        #Add doc_entities to the global list
        all_entities.extend(doc_entities)

        # PHASE 2: Build Relationships from Known Entities
        doc_relationships = build_relationships_from_entities(abstract, doc_id, doc_entities)
        # Add embeddings to doc relationships
        add_embeddings_to_relationships(doc_relationships)

        # Add doc_relationships to the global list
        all_relationships.extend(doc_relationships)


    canonical_entities_dict = deduplicate_entities(all_entities)
    updated_relationships = update_relationships_with_ids(all_relationships, canonical_entities_dict)

    today_str = datetime.now().strftime("%m%d")
    entities_csv_path = f"entities_{today_str}_prompt1.csv"
    relationships_csv_path = f"relationships_{today_str}_prompt1.csv"

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

    # --- Save relationships (with IDs and text)
    try:
        with open(relationships_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["source_id", "source_text", "target_id", "target_text", "relation_type", "doc_id"])
            for rel in updated_relationships:
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