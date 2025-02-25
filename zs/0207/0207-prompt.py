## no deduplicate  but with clean json string
import os, time
import requests
import re
import csv
import pandas as pd

os.environ["GROQ_API_KEY"] = "your API"
from groq import Groq
from datetime import datetime
from sentence_transformers import SentenceTransformer
import torch
import json

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
model = SentenceTransformer('all-MiniLM-L6-v2')
model = model.to('cpu')  # Explicitly set to CPU

def clean_json_string(json_string):
    """
    Attempts to clean and repair malformed JSON strings.
    """

    json_string = re.sub(r'(?<![\w])"\'|\'(?![\w])', '"', json_string)
    json_string = re.sub(r'(?<![\w])\'|\'(?![\w])', '"', json_string)

    json_string = json_string.replace(""", '"').replace(""", '"')

    json_string = re.sub(r',\s*([\]}])', r'\1', json_string)

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
        if "entities" not in data or "relationships" not in data:
            print("Error: Missing 'entities' or 'relationships' keys")
            return False
        if not isinstance(data["entities"], list) or not isinstance(data["relationships"], list):
            print("Error: 'entities' or 'relationships' is not a list")
            return False
        return True
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error at position {e.pos}:")
        print(f"Problem area: {json_string[max(0, e.pos - 20):min(len(json_string), e.pos + 20)]}")
        print(f"Error message: {str(e)}")
        return False


def validate_json_structure(json_string):
    """
    Validates the structure of the JSON string to ensure it meets the expected format.
    """
    try:
        data = json.loads(json_string)
        if not isinstance(data, dict):
            return False
        if "entities" not in data or "relationships" not in data:
            return False
        if not isinstance(data["entities"], list) or not isinstance(data["relationships"], list):
            return False
        return True
    except json.JSONDecodeError:
        return False


def complete_truncated_relationship(truncated_text, abstract):
    """Use LLM to complete a truncated relationship entry"""
    prompt = f"""
    Given this truncated relationship entry: {truncated_text}
    From abstract: {abstract}
    Complete the relationship as a valid three-element array ["source", "relation", "target"].
    Output only the completed array.
    """
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            temperature=0.0,
            max_tokens=128,
            top_p=1.0,
            seed=42
        )
        completed = response.choices[0].message.content.strip()
        array_match = re.search(r'\[.*?\]', completed, re.DOTALL)
        if array_match:
            return array_match.group(0)
    except Exception as e:
        print(f"Error completing relationship: {e}")
    return None


def extract_entities_and_relations(abstract, doc_id, max_retries=1):
    """
    Extract meaningful entities and relationships from a document using the Groq API.
    """


    example_output = """
            {
              "entities": [
                ["XXXXX", "AAAA"],
                ["BBB", "CCC"],
                ["DDD", "BCJ"]
              ],
              "relationships": [
                ["ABC", "XSAAJ", "HDKA"],
                ["OSHA", "HSAKOI", "JDHSL"]
              ]
            }
            """

    prompt = f"""
        This extraction should mention at least one bidirectional relation between a host and a pathogen. For both host and pathogen names, report the common name and scientific Latin binomial name if available.

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

    Output:
    {example_output}

    Now, for Document {doc_id}, please extract entities and relationships in the same format:

    Abstract:
    {abstract}
    """

    for attempt in range(max_retries):
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

        try:
            json_match = re.search(r'\{.*\}', completion_text, re.DOTALL)
            if not json_match:
                truncated_json = re.search(r'\{\s*"entities":\s*\[.*?\],\s*"relationships":\s*\[.*?(?=\["[^"]+",\s*"$)',
                                           completion_text, re.DOTALL)
                if truncated_json:
                    # Add closing brackets to make it valid JSON
                    json_text = truncated_json.group(0) + ']}'
                    json_text = clean_json_string(json_text)
                    data = json.loads(json_text)

                    entities = [{"text": ent[0], "type": ent[1], "doc_id": doc_id}
                                for ent in data.get("entities", []) if isinstance(ent, list) and len(ent) == 2]
                    relationships = [{"src": rel[0], "relation": rel[1].lower(), "tgt": rel[2], "doc_id": doc_id}
                                     for rel in data.get("relationships", []) if
                                     isinstance(rel, list) and len(rel) == 3]

                    if entities or relationships:
                        print(f"Successfully saved data before truncation for Document {doc_id}")
                        return entities, relationships

                print(f"Error: JSON not found in Document {doc_id} response. Retrying...")
                continue

            json_text = json_match.group(0).strip()
            json_text = clean_json_string(json_text)
            print(f"Document {doc_id} - Cleaned JSON (Attempt {attempt + 1}):\n{json_text}")

            truncated_match = re.search(r'\[\s*"([^"]+)"\s*,\s*"[^"]*"?\s*$', json_text)
            if truncated_match:
                print(f"Found truncated relationship: {truncated_match.group(0)}")
                completed_rel = complete_truncated_relationship(truncated_match.group(0), abstract)
                if completed_rel:
                    json_text = json_text[:truncated_match.start()] + completed_rel + ']}'
                    print(f"Completed relationship: {completed_rel}")

            data = json.loads(json_text)

            entities = [{"text": ent[0], "type": ent[1], "doc_id": doc_id}
                        for ent in data.get("entities", []) if isinstance(ent, list) and len(ent) == 2]
            relationships = [{"src": rel[0], "relation": rel[1].lower(), "tgt": rel[2], "doc_id": doc_id}
                             for rel in data.get("relationships", []) if isinstance(rel, list) and len(rel) == 3]

            if entities or relationships:
                return entities, relationships

        except json.JSONDecodeError as e:
            print(f"JSON decode error detected for Document {doc_id}. Attempting to recover...")
            try:
                last_complete_brace = json_text.rfind(']')
                if last_complete_brace != -1:
                    salvaged_json = json_text[:last_complete_brace + 1]

                    if '"relationships": [' in salvaged_json:
                        salvaged_json = salvaged_json + ']}'
                    else:
                        salvaged_json = salvaged_json + '], "relationships": []}'

                    data = json.loads(salvaged_json)

                    entities = [{"text": ent[0], "type": ent[1], "doc_id": doc_id}
                                for ent in data.get("entities", []) if isinstance(ent, list) and len(ent) == 2]
                    relationships = [{"src": rel[0], "relation": rel[1].lower(), "tgt": rel[2], "doc_id": doc_id}
                                     for rel in data.get("relationships", []) if
                                     isinstance(rel, list) and len(rel) == 3]

                    if entities or relationships:
                        print(f"Successfully recovered partial data from Document {doc_id}")
                        return entities, relationships

            except Exception as recovery_error:
                print(f"Failed to recover truncated JSON for Document {doc_id}: {recovery_error}")
                continue

        except Exception as e:
            print(f"Unexpected error processing Document {doc_id}: {e}")

        time.sleep(1)

    print(f"Failed to extract entities and relationships for Document {doc_id} after {max_retries} attempts.")
    return [], []


def get_embedding(text):
    """Generate an embedding for a given text using Sentence Transformers."""
    return model.encode(text, convert_to_tensor=True).cpu()


def add_embeddings(entities, relationships):
    """Add embeddings to each entity and relationship."""
    for entity in entities:
        entity["embedding"] = get_embedding(entity["text"])

    for relationship in relationships:
        relationship_text = f"{relationship['src']} - {relationship['relation']} -> {relationship['tgt']}"
        relationship["embedding"] = get_embedding(relationship_text)


def reassign_undefined_types_with_llm(entities):
    """
    Reassign 'Undefined' entity types using LLM for entities that have the label 'Undefined'.
    """
    undefined_entities = [entity for entity in entities if entity['type'] == 'Undefined']
    if not undefined_entities:
        return entities

    for entity in undefined_entities:
        entity_text = entity['text']
        prompt = f"""
                This extraction should mention at least one bidirectional relation between a host and a pathogen. For both host and pathogen names, report the common name and scientific Latin binomial name if available.

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
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model="llama3-8b-8192",
                temperature=0.0,  # Set low to make it more deterministic
                max_tokens=1024,  # Maximum number of tokens in the response
                top_p=1.0,  # Controls diversity
                seed=42  # Seed for reproducibility
            )
            # Extract the response content
            completion_text = response.choices[0].message.content

            json_match = re.search(r'\{.*\}', completion_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(0).strip()
                json_text = clean_json_string(json_text)  # Clean the JSON string
                data = json.loads(json_text)
                new_label = data.get("type", "Undefined")
                entity['type'] = new_label  # Update entity type
            else:
                print(f"Could not parse response for entity '{entity_text}':\n{completion_text}")
                entity['type'] = "Undefined"  # fallback in case of error

            time.sleep(0.5)  # Pause to avoid rate limiting by the API
        except Exception as e:
            print(f"Error reassigning entity '{entity_text}': {e}")
            entity['type'] = "Undefined"  # fallback in case of error

    return entities


def main():
    df = pd.read_csv('validation_100.csv')
    abstracts = df['title_abstract'].iloc[1:101].tolist()  # Exclude header, limit to 10 documents for example

    all_entities = []
    all_relationships = []

    for idx, abstract in enumerate(abstracts):
        doc_id = idx + 1
        print(f"Processing Document {doc_id}...")

        entities, relationships = extract_entities_and_relations(abstract, doc_id)
        all_entities.extend(entities)
        all_relationships.extend(relationships)

    all_entities = reassign_undefined_types_with_llm(all_entities)

    today_str = datetime.now().strftime("%m%d")
    entities_csv_path = f"entities_{today_str}_prompt4.csv"
    relationships_csv_path = f"relationships_{today_str}_prompt4.csv"

    with open(entities_csv_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["entity_id", "entity", "doc_id", "label"])
        for idx, entity in enumerate(all_entities, start=1):
            writer.writerow([idx, entity["text"], entity.get("doc_id", ""), entity.get("type", "")])

    with open(relationships_csv_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["source", "target", "relation_type", "doc_id"])
        for relationship in all_relationships:
            writer.writerow(
                [relationship["src"], relationship["tgt"], relationship["relation"], relationship.get("doc_id", "")])

    print(f"Saved entities to {entities_csv_path} and relationships to {relationships_csv_path}")


if __name__ == "__main__":
    main()
