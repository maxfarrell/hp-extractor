# 2024-06-14_friday

- [x] prompt design to create Neo4j Cypher graph database

**Prompt 1**

Using the given abstract, create an extremely detailed graph database from all possible entities and relationships with detailed labels and properties. Create a separate node for absID and link all other nodes to it with a reference relationship. Export it in the Neo4j cypher format without semicolons "absID 61102. Sequence analysis of the complete S genomic segment of a newly identified hantavirus isolated from the white-footed mouse (Peromyscus leucopus): phylogenetic relationship with other sigmodontine rodent-borne hantaviruses. Four Corners (FC) or Sin Nombre virus, a hantavirus harbored by the deer mouse (Peromyscus maniculatus), is the principal etiologic agent of hantavirus pulmonary syndrome (HPS). Recently, a hantavirus, designated New York (NY) virus, isolated from a white-footed mouse (Peromyscus leucopus) captured on Shelter Island, New York, was molecularly linked to a fatal case of HPS occurring in the northeastern United States. To clarify the genetic and phylogenetic relationship between NY and FC viruses and other sigmodontine rodent-borne hantaviruses, we amplified and sequenced the entire S genomic segment of NY virus. The S segment of NY virus was 2078 nucleotides long, with an open reading frame of 1284 nucleotides in the virus complementary strand, capable of encoding a protein of 428 amino acids, and with a 752-nucleotide long 3'-noncoding region, comprised of numerous imperfect repeats. Pairwise analysis indicated that NY virus was more similar to FC virus than to other sigmodontine rodent-borne hantaviruses, differing from strains of FC virus by 16.6-17.8% and 7.0-8.2% at the nucleotide and amino acid levels, respectively. As determined by the maximum parsimony and neighbor-joining methods, NY virus formed a separate lineage from FC virus and was phylogenetically distinct from hantaviruses harbored by other sigmodontine rodents. Whether or not NY and FC viruses represent distinct viral species is unclear. Further analyses of hantaviruses harbored by white-footed mice are needed to clarify the genetic diversity and evolution of Peromyscus-borne hantaviruses."

**Cypher 1**

```Cypher
// Create the absID node
CREATE (a:Abstract {absID: 61102})

// Create nodes for each unique entity
CREATE (s:S_Genomic_Segment {length_nucleotides: 2078, ORF_length: 1284, protein_length: 428, noncoding_region_length: 752})
CREATE (wfm:Mouse {species: "Peromyscus leucopus", common_name: "white-footed mouse"})
CREATE (dm:Mouse {species: "Peromyscus maniculatus", common_name: "deer mouse"})
CREATE (fc:Virus {name: "Four Corners Virus", abbreviation: "FC", disease: "Hantavirus Pulmonary Syndrome"})
CREATE (ny:Virus {name: "New York Virus", abbreviation: "NY", disease: "Hantavirus Pulmonary Syndrome"})
CREATE (hps:Disease {name: "Hantavirus Pulmonary Syndrome", abbreviation: "HPS"})
CREATE (island:Location {name: "Shelter Island", state: "New York", region: "Northeastern United States"})
CREATE (phylo:Phylogenetic_Analysis {method1: "maximum parsimony", method2: "neighbor-joining"})

// Create relationships between the absID node and other nodes
CREATE (a)-[:REFERENCE]->(s)
CREATE (a)-[:REFERENCE]->(wfm)
CREATE (a)-[:REFERENCE]->(dm)
CREATE (a)-[:REFERENCE]->(fc)
CREATE (a)-[:REFERENCE]->(ny)
CREATE (a)-[:REFERENCE]->(hps)
CREATE (a)-[:REFERENCE]->(island)
CREATE (a)-[:REFERENCE]->(phylo)

// Create relationships between entities
CREATE (ny)-[:ISOLATED_FROM]->(wfm)
CREATE (ny)-[:CAPTURED_AT]->(island)
CREATE (ny)-[:CAUSES]->(hps)
CREATE (fc)-[:HARBORS]->(dm)
CREATE (fc)-[:CAUSES]->(hps)
CREATE (ny)-[:HAS_SEGMENT]->(s)
CREATE (s)-[:HAS_PART]->(:Nucleotide_Sequence {length: 2078})
CREATE (s)-[:HAS_ORF]->(:Open_Reading_Frame {length: 1284})
CREATE (s)-[:ENCODES]->(:Protein {length: 428, strand: "virus complementary"})
CREATE (s)-[:HAS_NONCODING_REGION]->(:Noncoding_Region {length: 752, feature: "imperfect repeats"})
CREATE (ny)-[:RELATED_TO]->(fc)
CREATE (ny)-[:RELATED_TO]->(:Virus {name: "sigmodontine rodent-borne hantaviruses"})
CREATE (phylo)-[:ANALYSIS_OF]->(ny)
CREATE (phylo)-[:ANALYSIS_OF]->(fc)

// Add properties for relationships
CREATE (ny)-[:RELATED_TO {similarity_nucleotide: 16.6, similarity_amino_acid: 7.0}]->(fc)
CREATE (ny)-[:RELATED_TO {similarity_nucleotide: 17.8, similarity_amino_acid: 8.2}]->(fc)

// Create nodes for additional viruses for context
CREATE (srh:Virus {name: "sigmodontine rodent-borne hantaviruses"})
CREATE (srh)-[:HARBORS]->(:Rodent {family: "Sigmodontine"})

// Connect to phylogenetic analysis
CREATE (phylo)-[:SHOWS_LINEAGE]->(ny)
CREATE (phylo)-[:SHOWS_LINEAGE]->(fc)
CREATE (ny)-[:DISTINCT_FROM]->(srh)

// Connect back to the abstract for completeness
CREATE (a)-[:STUDY_OF]->(ny)
CREATE (a)-[:STUDY_OF]->(fc)
CREATE (a)-[:STUDY_OF]->(srh)
```

**Graph 1**

![[Screenshot 2024-06-14 at 11.05.04.png]]


**Prompt 2**

Using the given abstract, create a very detailed graph database from all possible entities and relationships with detailed labels (including "Host") and properties (including "synonym"). Create a separate node for absID and link all other nodes to it with the "absID" relationship. Export it in the Neo4j cypher format without semicolons "absID 61102. Sequence analysis of the complete S genomic segment of a newly identified hantavirus isolated from the white-footed mouse (Peromyscus leucopus): phylogenetic relationship with other sigmodontine rodent-borne hantaviruses. Four Corners (FC) or Sin Nombre virus, a hantavirus harbored by the deer mouse (Peromyscus maniculatus), is the principal etiologic agent of hantavirus pulmonary syndrome (HPS). Recently, a hantavirus, designated New York (NY) virus, isolated from a white-footed mouse (Peromyscus leucopus) captured on Shelter Island, New York, was molecularly linked to a fatal case of HPS occurring in the northeastern United States. To clarify the genetic and phylogenetic relationship between NY and FC viruses and other sigmodontine rodent-borne hantaviruses, we amplified and sequenced the entire S genomic segment of NY virus. The S segment of NY virus was 2078 nucleotides long, with an open reading frame of 1284 nucleotides in the virus complementary strand, capable of encoding a protein of 428 amino acids, and with a 752-nucleotide long 3'-noncoding region, comprised of numerous imperfect repeats. Pairwise analysis indicated that NY virus was more similar to FC virus than to other sigmodontine rodent-borne hantaviruses, differing from strains of FC virus by 16.6-17.8% and 7.0-8.2% at the nucleotide and amino acid levels, respectively. As determined by the maximum parsimony and neighbor-joining methods, NY virus formed a separate lineage from FC virus and was phylogenetically distinct from hantaviruses harbored by other sigmodontine rodents. Whether or not NY and FC viruses represent distinct viral species is unclear. Further analyses of hantaviruses harbored by white-footed mice are needed to clarify the genetic diversity and evolution of Peromyscus-borne hantaviruses."

**Graph 2**

![[Screenshot 2024-06-14 at 11.14.03.png]]

**Prompt 3**

Using the given abstract, create a very detailed graph database from all possible entities with detailed labels (including Host and Pathogen) and properties and relationships. Create a separate node for absID labelled as absID and link it to all other nodes with the absID relationship. Export it in the Neo4j cypher format without semicolons "absID 61102. Sequence analysis of the complete S genomic segment of a newly identified hantavirus isolated from the white-footed mouse (Peromyscus leucopus): phylogenetic relationship with other sigmodontine rodent-borne hantaviruses. Four Corners (FC) or Sin Nombre virus, a hantavirus harbored by the deer mouse (Peromyscus maniculatus), is the principal etiologic agent of hantavirus pulmonary syndrome (HPS). Recently, a hantavirus, designated New York (NY) virus, isolated from a white-footed mouse (Peromyscus leucopus) captured on Shelter Island, New York, was molecularly linked to a fatal case of HPS occurring in the northeastern United States. To clarify the genetic and phylogenetic relationship between NY and FC viruses and other sigmodontine rodent-borne hantaviruses, we amplified and sequenced the entire S genomic segment of NY virus. The S segment of NY virus was 2078 nucleotides long, with an open reading frame of 1284 nucleotides in the virus complementary strand, capable of encoding a protein of 428 amino acids, and with a 752-nucleotide long 3'-noncoding region, comprised of numerous imperfect repeats. Pairwise analysis indicated that NY virus was more similar to FC virus than to other sigmodontine rodent-borne hantaviruses, differing from strains of FC virus by 16.6-17.8% and 7.0-8.2% at the nucleotide and amino acid levels, respectively. As determined by the maximum parsimony and neighbor-joining methods, NY virus formed a separate lineage from FC virus and was phylogenetically distinct from hantaviruses harbored by other sigmodontine rodents. Whether or not NY and FC viruses represent distinct viral species is unclear. Further analyses of hantaviruses harbored by white-footed mice are needed to clarify the genetic diversity and evolution of Peromyscus-borne hantaviruses."

**Prompt 4**

Using the given abstract, create a very detailed graph database from all possible entities with detailed labels (including "host" and "pathogen") and properties (including "name" and "synonym") and relationships. Create a separate node for absID and link it to all other nodes with the "in_article" relationship. Export it in the Neo4j cypher format without semicolons "absID 61102. Sequence analysis of the complete S genomic segment of a newly identified hantavirus isolated from the white-footed mouse (Peromyscus leucopus): phylogenetic relationship with other sigmodontine rodent-borne hantaviruses. Four Corners (FC) or Sin Nombre virus, a hantavirus harbored by the deer mouse (Peromyscus maniculatus), is the principal etiologic agent of hantavirus pulmonary syndrome (HPS). Recently, a hantavirus, designated New York (NY) virus, isolated from a white-footed mouse (Peromyscus leucopus) captured on Shelter Island, New York, was molecularly linked to a fatal case of HPS occurring in the northeastern United States. To clarify the genetic and phylogenetic relationship between NY and FC viruses and other sigmodontine rodent-borne hantaviruses, we amplified and sequenced the entire S genomic segment of NY virus. The S segment of NY virus was 2078 nucleotides long, with an open reading frame of 1284 nucleotides in the virus complementary strand, capable of encoding a protein of 428 amino acids, and with a 752-nucleotide long 3'-noncoding region, comprised of numerous imperfect repeats. Pairwise analysis indicated that NY virus was more similar to FC virus than to other sigmodontine rodent-borne hantaviruses, differing from strains of FC virus by 16.6-17.8% and 7.0-8.2% at the nucleotide and amino acid levels, respectively. As determined by the maximum parsimony and neighbor-joining methods, NY virus formed a separate lineage from FC virus and was phylogenetically distinct from hantaviruses harbored by other sigmodontine rodents. Whether or not NY and FC viruses represent distinct viral species is unclear. Further analyses of hantaviruses harbored by white-footed mice are needed to clarify the genetic diversity and evolution of Peromyscus-borne hantaviruses."

**Prompt 5**

Using the given abstract, create a very detailed graph database from all possible entities with detailed labels (including "host" and "pathogen") and properties (including "name" and "synonym") and relationships. For each node and relationship include the absID property. Export it in the Neo4j cypher format without semicolons "absID 61102. Sequence analysis of the complete S genomic segment of a newly identified hantavirus isolated from the white-footed mouse (Peromyscus leucopus): phylogenetic relationship with other sigmodontine rodent-borne hantaviruses. Four Corners (FC) or Sin Nombre virus, a hantavirus harbored by the deer mouse (Peromyscus maniculatus), is the principal etiologic agent of hantavirus pulmonary syndrome (HPS). Recently, a hantavirus, designated New York (NY) virus, isolated from a white-footed mouse (Peromyscus leucopus) captured on Shelter Island, New York, was molecularly linked to a fatal case of HPS occurring in the northeastern United States. To clarify the genetic and phylogenetic relationship between NY and FC viruses and other sigmodontine rodent-borne hantaviruses, we amplified and sequenced the entire S genomic segment of NY virus. The S segment of NY virus was 2078 nucleotides long, with an open reading frame of 1284 nucleotides in the virus complementary strand, capable of encoding a protein of 428 amino acids, and with a 752-nucleotide long 3'-noncoding region, comprised of numerous imperfect repeats. Pairwise analysis indicated that NY virus was more similar to FC virus than to other sigmodontine rodent-borne hantaviruses, differing from strains of FC virus by 16.6-17.8% and 7.0-8.2% at the nucleotide and amino acid levels, respectively. As determined by the maximum parsimony and neighbor-joining methods, NY virus formed a separate lineage from FC virus and was phylogenetically distinct from hantaviruses harbored by other sigmodontine rodents. Whether or not NY and FC viruses represent distinct viral species is unclear. Further analyses of hantaviruses harbored by white-footed mice are needed to clarify the genetic diversity and evolution of Peromyscus-borne hantaviruses."

**Prompt 6**

Using the given abstract, create a very detailed graph database from all possible entities with detailed labels (including Host and Pathogen) and properties (including name and synonym) and relationships. For each node and relationship include the absID property as well. Export it in the Neo4j cypher format without semicolons "absID 61102. Sequence analysis of the complete S genomic segment of a newly identified hantavirus isolated from the white-footed mouse (Peromyscus leucopus): phylogenetic relationship with other sigmodontine rodent-borne hantaviruses. Four Corners (FC) or Sin Nombre virus, a hantavirus harbored by the deer mouse (Peromyscus maniculatus), is the principal etiologic agent of hantavirus pulmonary syndrome (HPS). Recently, a hantavirus, designated New York (NY) virus, isolated from a white-footed mouse (Peromyscus leucopus) captured on Shelter Island, New York, was molecularly linked to a fatal case of HPS occurring in the northeastern United States. To clarify the genetic and phylogenetic relationship between NY and FC viruses and other sigmodontine rodent-borne hantaviruses, we amplified and sequenced the entire S genomic segment of NY virus. The S segment of NY virus was 2078 nucleotides long, with an open reading frame of 1284 nucleotides in the virus complementary strand, capable of encoding a protein of 428 amino acids, and with a 752-nucleotide long 3'-noncoding region, comprised of numerous imperfect repeats. Pairwise analysis indicated that NY virus was more similar to FC virus than to other sigmodontine rodent-borne hantaviruses, differing from strains of FC virus by 16.6-17.8% and 7.0-8.2% at the nucleotide and amino acid levels, respectively. As determined by the maximum parsimony and neighbor-joining methods, NY virus formed a separate lineage from FC virus and was phylogenetically distinct from hantaviruses harbored by other sigmodontine rodents. Whether or not NY and FC viruses represent distinct viral species is unclear. Further analyses of hantaviruses harbored by white-footed mice are needed to clarify the genetic diversity and evolution of Peromyscus-borne hantaviruses."

**Prompt 7**

Using the given abstract, create a very detailed graph database from all possible entities with detailed labels and properties and relationships. Each node can have multiple labels. All nodes corresponding to animals should also have a host label. All nodes corresponding to viruses, bacteria or parasites should also have a pathogen label. For each node and relationship include the absID property. Export everything in the Neo4j cypher format. Do not use semicolons. "absID 60336. Detection of gastric Helicobacter species in white-footed mouse (Peromyscus leucopus) and deer mouse (Peromyscus maniculatus) in Sweden. Specimens of gastric mucosa and liver of 25 free-ranging Eurasian lynx (Lynx lynx), and four red foxes (Vulpes vulpes) shot in Sweden during 1999-2000, were investigated for the presence of Helicobacter species. Histopathology, bacteriologic culture and urease test, Helicobacter genus-specific 16S rDNA PCR analysis, and DNA sequence analysis were applied. Numerous Helicobacter-like organisms were observed histologically in the gastric mucosa of one fox. Helicobacter spp. were detected in the stomach by PCR analysis in 17 (68%) of the lynx and in three (75%) of the foxes. Seven of the positive lynx were also positive in the urease test. PCR fragments, amplified from lynx and foxes, were sequenced and compared with those of known Helicobacter species. PCR products from lynx were closely related (>or=98% homology) to H. heilmannii, and PCR fragments from foxes demonstrated close homology to H. heilmannii and H. salomonis. No Helicobacter spp. or Helicobacter-like organisms could be cultured. The PCR analysis of the liver was negative for all animals. The pathologic significance of the presence of Helicobacter spp. in the stomach of free-ranging lynx and foxes remains uncertain."

**Prompt 8**

Using the given abstract, create a very detailed graph database from all possible entities with detailed labels and properties and relationships. Each node can have multiple labels. All nodes corresponding to animals should also have a host label. All nodes corresponding to viruses, bacteria or parasites should also have a pathogen label. For each node and relationship include the absID property. Export everything in the Neo4j cypher format. Do not use semicolons. "absID 60405. Physaloptera sibirica in foxes and badgers from the Western Alps (Italy). We investigated the presence of Physaloptera sibirica and its distribution as well as the association among the parasite, host (i.e. mange due to Sarcoptes scabiei) and environmental factors (i.e. altitudes) in foxes (Vulpes vulpes) and badgers (Meles meles) from the North-West of Italy. From 1996 to 2008 a total of 608 foxes, culled by hunters or road killed, and 39 road killed badgers were examined in order to investigate the presence of nematodes in the stomach. P. sibirica was found in 16 foxes (2.63%) and one badger (2.56%). As regards foxes' habitat type, prevalence was significantly higher (chi(2) = 16.36, p < or = 0.05) in mountain foxes (6.43%; 95%CI 3.25-11.22%) than those from hills (2.22%; 95%CI 0.46-6.36%) or irrigated plains (0.34%; 95%CI 0.01-1.90%). There were no significant differences between sex, age, months and years of the sampling. P. sibirica presence is significantly (chi(2) = 241.63, p > 0.000001) higher (73.33%; 95%CI 44.83-91.09%) in foxes with sarcoptic mange than foxes without mange (0.84%; 95%CI 0.21-1.84%). According to previous studies, in Southern Europe this parasite is associated with mountain areas, probably due to its intermediate hosts which require cold climate. Further studies are needed to evaluate the pathogenic role of P. sibirica in wildlife and its effects on host life history."

**Promp 9**

Using the given abstract, create a very detailed graph database from all possible entities with detailed labels and properties and relationships. Each node can have multiple labels. All nodes corresponding to organisms should have scientific name as their name. All nodes corresponding to vertebrates should also have a host label. All nodes corresponding to parasites, pathogens, infectious agents should also have a pathogen label. For each node and relationship include the absID property. Export everything in the Neo4j cypher format. Do not use semicolons. "absID 60405. Physaloptera sibirica in foxes and badgers from the Western Alps (Italy). We investigated the presence of Physaloptera sibirica and its distribution as well as the association among the parasite, host (i.e. mange due to Sarcoptes scabiei) and environmental factors (i.e. altitudes) in foxes (Vulpes vulpes) and badgers (Meles meles) from the North-West of Italy. From 1996 to 2008 a total of 608 foxes, culled by hunters or road killed, and 39 road killed badgers were examined in order to investigate the presence of nematodes in the stomach. P. sibirica was found in 16 foxes (2.63%) and one badger (2.56%). As regards foxes' habitat type, prevalence was significantly higher (chi(2) = 16.36, p < or = 0.05) in mountain foxes (6.43%; 95%CI 3.25-11.22%) than those from hills (2.22%; 95%CI 0.46-6.36%) or irrigated plains (0.34%; 95%CI 0.01-1.90%). There were no significant differences between sex, age, months and years of the sampling. P. sibirica presence is significantly (chi(2) = 241.63, p > 0.000001) higher (73.33%; 95%CI 44.83-91.09%) in foxes with sarcoptic mange than foxes without mange (0.84%; 95%CI 0.21-1.84%). According to previous studies, in Southern Europe this parasite is associated with mountain areas, probably due to its intermediate hosts which require cold climate. Further studies are needed to evaluate the pathogenic role of P. sibirica in wildlife and its effects on host life history."

**Prompt 10**

Using the given abstract, create a very detailed graph database from all possible entities with detailed labels and properties and relationships. Each node can have multiple labels including host label for hosts and pathogen label for parasites, pathogens and infectious agents. For each node and relationship include the absID property. Export everything in the Neo4j cypher format. Do not use semicolons. "absID 60405. Physaloptera sibirica in foxes and badgers from the Western Alps (Italy). We investigated the presence of Physaloptera sibirica and its distribution as well as the association among the parasite, host (i.e. mange due to Sarcoptes scabiei) and environmental factors (i.e. altitudes) in foxes (Vulpes vulpes) and badgers (Meles meles) from the North-West of Italy. From 1996 to 2008 a total of 608 foxes, culled by hunters or road killed, and 39 road killed badgers were examined in order to investigate the presence of nematodes in the stomach. P. sibirica was found in 16 foxes (2.63%) and one badger (2.56%). As regards foxes' habitat type, prevalence was significantly higher (chi(2) = 16.36, p < or = 0.05) in mountain foxes (6.43%; 95%CI 3.25-11.22%) than those from hills (2.22%; 95%CI 0.46-6.36%) or irrigated plains (0.34%; 95%CI 0.01-1.90%). There were no significant differences between sex, age, months and years of the sampling. P. sibirica presence is significantly (chi(2) = 241.63, p > 0.000001) higher (73.33%; 95%CI 44.83-91.09%) in foxes with sarcoptic mange than foxes without mange (0.84%; 95%CI 0.21-1.84%). According to previous studies, in Southern Europe this parasite is associated with mountain areas, probably due to its intermediate hosts which require cold climate. Further studies are needed to evaluate the pathogenic role of P. sibirica in wildlife and its effects on host life history."


# 2024-06-13_thursday


- [x] ChatGPT CQL output for absID 61102

Prompt 1:

Export a knowledge graph in a Neo4j CQL format for all entities (including synonyms), their types and relationships from "Title + Abstract"

Output 1:

```Cypher
// Create entities
CREATE (:Virus {name: 'Sin Nombre Virus', synonym: 'Four Corners Virus', abbreviation: 'FC'});
CREATE (:Virus {name: 'New York Virus', abbreviation: 'NY'});
CREATE (:Rodent {name: 'White-footed mouse', scientific_name: 'Peromyscus leucopus'});
CREATE (:Rodent {name: 'Deer mouse', scientific_name: 'Peromyscus maniculatus'});
CREATE (:Disease {name: 'Hantavirus Pulmonary Syndrome', abbreviation: 'HPS'});
CREATE (:Location {name: 'Shelter Island', state: 'New York'});
CREATE (:Location {name: 'Northeastern United States'});

// Create relationships
MATCH (v1:Virus {abbreviation: 'FC'}), (r1:Rodent {scientific_name: 'Peromyscus maniculatus'})
CREATE (v1)-[:HARBORS]->(r1);

MATCH (v2:Virus {abbreviation: 'NY'}), (r2:Rodent {scientific_name: 'Peromyscus leucopus'})
CREATE (v2)-[:HARBORS]->(r2);

MATCH (v2:Virus {abbreviation: 'NY'}), (d:Disease {abbreviation: 'HPS'})
CREATE (v2)-[:LINKED_TO]->(d);

MATCH (r2:Rodent {scientific_name: 'Peromyscus leucopus'}), (l1:Location {name: 'Shelter Island', state: 'New York'})
CREATE (r2)-[:CAPTURED_ON]->(l1);

MATCH (v1:Virus {abbreviation: 'FC'}), (v2:Virus {abbreviation: 'NY'})
CREATE (v2)-[:SIMILAR_TO {nucleotide_diff: '16.6-17.8%', amino_acid_diff: '7.0-8.2%'}]->(v1);

MATCH (v2:Virus {abbreviation: 'NY'}), (v1:Virus {abbreviation: 'FC'})
CREATE (v2)-[:DISTINCT_FROM]->(v1);

```

Graph 1:

![[Screenshot 2024-06-13 at 20.44.34.png]]

Prompt 2:

Using the given abstract, export all possible entities and their relationships with appropriate labels (including host and pathogen) and properties in Neo4j cypher format without semicolons "Title + Abstract"

Output 2:

```Cypher
// Create nodes for the viruses
CREATE (fc:Virus {name: "Four Corners Virus", alias: "Sin Nombre Virus"})
CREATE (ny:Virus {name: "New York Virus"})

// Create nodes for the mice
CREATE (pm:Host {name: "Peromyscus maniculatus", common_name: "deer mouse"})
CREATE (pl:Host {name: "Peromyscus leucopus", common_name: "white-footed mouse"})

// Create nodes for the diseases
CREATE (hps:Disease {name: "Hantavirus Pulmonary Syndrome", acronym: "HPS"})

// Create nodes for the methods
CREATE (mp:Method {name: "Maximum Parsimony"})
CREATE (nj:Method {name: "Neighbor-Joining"})

// Create relationships between viruses and hosts
CREATE (fc)-[:HARBORS]->(pm)
CREATE (ny)-[:HARBORS]->(pl)

// Create relationships between viruses and diseases
CREATE (fc)-[:CAUSES]->(hps)
CREATE (ny)-[:LINKED_TO]->(hps)

// Create relationships between viruses and methods
CREATE (ny)-[:ANALYZED_BY]->(mp)
CREATE (ny)-[:ANALYZED_BY]->(nj)

// Create relationships between viruses for genetic similarity
CREATE (ny)-[:MORE_SIMILAR_TO {nucleotide_difference: "16.6-17.8%", amino_acid_difference: "7.0-8.2%"}]->(fc)

// Create relationships for phylogenetic lineage
CREATE (ny)-[:SEPARATE_LINEAGE_FROM]->(fc)
```

Graph 2:

![[Screenshot 2024-06-13 at 21.12.00.png]]

- [x] Neo4j and graph databases

**Graph database** uses graph structures with **nodes**, **edges** where edges represent relationships between nodes and treated as important as the data itself.

Neo4j (java-based)

**Entities** (with key properties in a form of dictionary) and one-directional **relationships** (with key properties in a form of a dictionary). Entities can belong to different types (have different labels)

Queries are written in a Cypher (or CQL for Cypher Query Language)

https://www.youtube.com/watch?v=8jNPelugC2s

```Cypher
# return all nodes and relationships (graph)
MATCH (n) RETURN n

## Query for nodes
# return only nodes with PLAYER label (graph)
MATCH (n:PLAYER) RETURN n

# return name and height property values for nodes with PLAYER label (table)
MATCH (n:PLAYER) RETURN n.name, n.height

# change column names to name and height
MATCH (n:PLAYER) RETURN n.name AS name, n.height AS height

# return all PLAYER nodes where a name attribute is "LeBron James"
MATCH (n:PLAYER) WHERE n.name = "LeBron James" RETURN n
MATCH (n:PLAYER {name: "LeBron James"}) RETURN n

# return all PLAYER nodes where a name attribute is not "LeBron James"
MATCH (n:PLAYER) WHERE n.name <> "LeBron James" RETURN n

# return all PLAYER nodes where a height attribute is greater than 2
MATCH (n:PLAYER) WHERE n.height > 2 RETURN n

# return all PLAYER nodes matching our criteria 
MATCH (n:PLAYER) WHERE (n.weight / (n.height * n.height)) > 25 RETURN n

# return all PLAYER nodes matching our criteria 
MATCH (n:PLAYER) WHERE n.weight > 100 AND n.height < 2 RETURN n

# return all PLAYER nodes matching our criteria 
MATCH (n:PLAYER) WHERE n.weight > 120 OR n.height > 2.1 RETURN n

# return all PLAYER nodes not matching our criteria 
MATCH (n:PLAYER) WHERE NOT n.weight > 120 OR n.height > 2.1 RETURN n

# return all PLAYER nodes matching our criteria but limit the output to 2 nodes skipping the first 2 nodes
MATCH (n:PLAYER) WHERE n.height > 2 RETURN n SKIP 2 LIMIT 2

# return all PLAYER nodes matching our criteria ordered by height from highest to shortest or from shortest to highest
MATCH (n:PLAYER) WHERE n.height > 2 RETURN n ORDER BY n.height DESC
MATCH (n:PLAYER) WHERE n.height > 2 RETURN n ORDER BY n.height ASC

# return all PLAYER and COACH nodes
MATCH (player:PLAYER), (coach:COACH) RETURN player, coach

## Query for relationships
# return all PLAYER nodes that have a relationship of playing for LA Lakers
MATCH (player:PLAYER) -[r:PLAYS_FOR]-> (team:TEAM) WHERE team.name = "LA Lakers" RETURN player

# return all PLAYER nodes that have a salary higher than 35 million
MATCH (player:PLAYER) -[contract:PLAYS_FOR]-> (team:TEAM) WHERE contract.salary > 35000000 RETURN player

# return all PLAYER nodes that are teammates with LeBron James and have a salary higher than 40 million
MATCH (lebron:PLAYER {name: "LeBron James"}) -[:TEAMMATES]-> (teammate:PLAYER) MATCH (teammate) -[contract:PLAYS_FOR]-> (team:TEAM) WHERE contract.salary > 40000000 RETURN teammate

# callculate a sum of played games for each player
MATCH (player:PLAYER) -[game_played:PLAYED_AGAINST]-> (:TEAM) RETURN player.name COUNT(game_played)

# callculate an average of points for each player and show only the top player
MATCH (player:PLAYER) -[game_played:PLAYED_AGAINST]-> (:TEAM) RETURN player.name AVG(game_played.points) AS ppg ORDER BY DESC LIMIT 1

## Delete a node with all relationships (you cannot delete a node keeping the relationships)
MATCH (ja {name: "Ja Morant"}) DETACH DELETE ja

## Delete only the relationship
MATCH (ja {name: "Ja Morant"}) -[rel:PLAYS_FOR]-> (:TEAM) DELETE rel

## Create nodes
# Create a node with multiple labels
CREATE (lebron:PLAYER:COACH:MANAGER {name: "LeBron James", height: 2.01, }) RETURN lebron

# Create two nodes with a relationship
CREATE (:PLAYER) -[:PLAYS_FOR {salary: 34000000}]-> (:TEAM {name: "LA Lakers"})

# Create a relationship for existing nodes
MATCH (lebron:PLAYER {name: "LeBron James"}), (lakers:TEAM {name: "LA Lakers"}) CREATE (lebron) -[:PLAYS_FOR {salary: 40000000}]-> (lakers)

## Update nodes and relationships
# Add, change properties and labels for existing nodes
MATCH (anthony:PLAYER) WHERE ID(anthony) = 0 SET anthony.name = "Anthony Davis", anthony.age = 36, anthony:COACH RETURN anthony

# Remove a label or property
MATCH (lebron:PLAYER {name: "LeBron James"}) REMOVE lebron.age, lebron:COACH RETURN lebron
```

- [x] install Neo4j Desktop

```bash
# key to activate your copy of Neo4j Desktop
eyJhbGciOiJQUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Ii4rQC4rIiwibWl4cGFuZWxJZCI6IiRkZXZpY2U6MTkwMGMxNTcyNjY0ZWMtMDBmZTRjYmFhNTJiOTMtMWE1MjU2MzctMTZhN2YwLTE5MDBjMTU3MjY2NGVjIiwibWl4cGFuZWxQcm9qZWN0SWQiOiI0YmZiMjQxNGFiOTczYzc0MWI2ZjA2N2JmMDZkNTU3NSIsIm9yZyI6Ii4qIiwicHViIjoibmVvNGouY29tIiwicmVnIjoiICIsInN1YiI6Im5lbzRqLWRlc2t0b3AiLCJleHAiOjE3NDk4MjAzODIsInZlciI6IioiLCJpc3MiOiJuZW80ai5jb20iLCJuYmYiOjE3MTgyODQzODIsImlhdCI6MTcxODI4NDM4MiwianRpIjoiaHk3bTVKV2xhIn0.Bxepnt2klsccK_hjCtsoPFQobdXYndkRFtMIc5pAcQYA1wbngdjQaZfCsSeMih7befIEMz-3OtJdv6X3NgY2JGeC7VNGBqRBFiFuqW2Zx7CTWOGE-TKlzrydTqvGnmZ1O_tnzDwoRWQOb8wjd0LbZsNOQ6xGg8X5fRRqvOf037DQV5fdmRs8kowPNUWVe_jouOdo56lNJxFlvldzwQP488d_r1tXubxul307XH1QN-p4rDLW-2rqW2dC4R8wx7yBWxVAv7IIASmEnx8xc3vgbL5eScletolkKFfDgu_GARrZlb78WkgQUne0clZioyoHqp3BDaguLfrSDmtinz0pWg
```

- [x] paper subsets

- Viruses: 17,500 abstracts
- Mammalian viruses: 15,000

# 2024-06-12_wednesday

- [x] create some ChatGPT prompts to extract info on host-pathogen interactions from Title + Abstract

- Make a table of extracted pairs of organism names with host-pathogen, host-parasite relationships from “Title + Abstract”
- Make a table of extracted pairs of scientific and common organism names with host-pathogen or host-parasite relationship from “Title + Abstract”


- [x] connect to MARS and start interactive session

```bash
# connect to MARS
ssh 2820395l@mars-login.ice.gla.ac.uk

# go to project folder
cd /mnt/data/project0037

# start interactive session (to install software)
srun --account=project0037 -p gpuplus --gres=gpu:1 --reservation=hackathon_p37 --pty bash

# load modules
module load apps/anaconda3
```