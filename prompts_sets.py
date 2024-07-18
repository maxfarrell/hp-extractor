prompt0 = '1. Identify parasites or pathogens' \
          '2. Identify host species infected by each parasite/pathogen' \
          '3. Output a table with parasites in the first column, and the infected hosts in the second column'

prompt1 = 'here is an abstract: "absID=X. TEXT" ' \
          'Based on this information, identify all species mentioned either by their common name of latin name. ' \
          'Create a comprehensive list of all the species. Include every synonym as a separate species. Double-check that you have identified all species, including those that may be abbreviated (in which case infer the whole name). ' \
          'Categorise each species into host and pathogen. ' \
          'Create a table with exactly 2 columns: host (latin name), pathogen (latin name)' \
          'Only include information that is included in the given abstract. ' \
          'Only show the table as output.' \
          'if the host is infected by several pathgeons, you need to repeat it for several times' \
          'like host1 pathgeon1, host1 pathgeon2'

prompt2 = 'Make a table of extracted pairs of organism names with host-pathogen, host-parasite relationships from “Title + Abstract”' \
          'Make a table of extracted pairs of scientific and common organism names with host-pathogen or host-parasite relationship from “Title + Abstract'

prompt3 = '1. Extract all latin species and common names if present from the above abstract, and pair them with their appropriate latin name if available' \
          '2. Fill in their pathogen for each host Species' \
          '3. please include the geographical location of the study if present in the text' \
          '4. include infectious levels in the table specific for each species' \
          '5. include the common name for each equivalent host that is identified in the text' \
          '6. include relationship of infection potential between each host species to one another into the table' \
          '7. what species displayed symptoms of infection from the pathogen'

prompt4 = 'Export a knowledge graph in a Neo4j CQL format for all entities (including synonyms), their types and relationships from "Title + Abstract"'

prompt5 = (
    "Based on the abstract above, generate relationships in the following format for each sentence: "
    "entityA, relationship, entityB. Use the following rules: "
    "1. Describe relationships using past tense (e.g., A was infected by B). "
    "2. Specify examples for each entity type (e.g., host: human, pathogen: virus). "
    "3. Example relationships: A was infected by B, A was found in B, A was detected by B."
    "convert it to a table"
)

prompt6 = 'Based on the given text, export the biological entities and relationships between them, inferring from the text whether any named host species can be infected by any named pathogen or parasite species. Entities capturing species should include Latin binomial (scientific name) and common name. The output should be formatted as a Neo4j cypher format without semicolons "Title + Abstract"'

prompts = [prompt0, prompt1, prompt2, prompt3, prompt4, prompt5, prompt6]