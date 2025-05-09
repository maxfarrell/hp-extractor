// Nodes
CREATE (a:Animal {name: "Eurasian lynx", synonym: "Lynx lynx", absID: 60336})
CREATE (b:Animal {name: "Red fox", synonym: "Vulpes vulpes", absID: 60336})
CREATE (c:Animal {name: "White-footed mouse", synonym: "Peromyscus leucopus", absID: 60336})
CREATE (d:Animal {name: "Deer mouse", synonym: "Peromyscus maniculatus", absID: 60336})
CREATE (e:Pathogen {name: "Helicobacter heilmannii", synonym: "H. heilmannii", absID: 60336})
CREATE (f:Pathogen {name: "Helicobacter salomonis", synonym: "H. salomonis", absID: 60336})
CREATE (g:Pathogen {name: "Helicobacter spp.", absID: 60336})
CREATE (h:Test {name: "Histopathology", absID: 60336})
CREATE (i:Test {name: "Bacteriologic culture", absID: 60336})
CREATE (j:Test {name: "Urease test", absID: 60336})
CREATE (k:Test {name: "16S rDNA PCR analysis", absID: 60336})
CREATE (l:Test {name: "DNA sequence analysis", absID: 60336})
CREATE (m:Sample {name: "Gastric mucosa", absID: 60336})
CREATE (n:Sample {name: "Liver", absID: 60336})
CREATE (o:Country {name: "Sweden", absID: 60336})

// Relationships
CREATE (a)-[:HAS_PATHOGEN {absID: 60336}]->(g)
CREATE (a)-[:HAS_PATHOGEN {absID: 60336}]->(e)
CREATE (a)-[:TESTED_POSITIVE {absID: 60336}]->(j)
CREATE (a)-[:TESTED_POSITIVE {absID: 60336}]->(k)
CREATE (a)-[:HAS_SAMPLE {absID: 60336}]->(m)
CREATE (a)-[:HAS_SAMPLE {absID: 60336}]->(n)
CREATE (b)-[:HAS_PATHOGEN {absID: 60336}]->(g)
CREATE (b)-[:HAS_PATHOGEN {absID: 60336}]->(e)
CREATE (b)-[:HAS_PATHOGEN {absID: 60336}]->(f)
CREATE (b)-[:TESTED_POSITIVE {absID: 60336}]->(k)
CREATE (b)-[:HAS_SAMPLE {absID: 60336}]->(m)
CREATE (b)-[:HAS_SAMPLE {absID: 60336}]->(n)
CREATE (c)-[:LOCATED_IN {absID: 60336}]->(o)
CREATE (d)-[:LOCATED_IN {absID: 60336}]->(o)
CREATE (e)-[:DETECTED_BY {absID: 60336}]->(k)
CREATE (f)-[:DETECTED_BY {absID: 60336}]->(k)
CREATE (g)-[:DETECTED_BY {absID: 60336}]->(k)
CREATE (g)-[:OBSERVED_BY {absID: 60336}]->(h)
CREATE (h)-[:USED_FOR {absID: 60336}]->(g)
CREATE (i)-[:USED_FOR {absID: 60336}]->(g)
CREATE (j)-[:USED_FOR {absID: 60336}]->(g)
CREATE (k)-[:USED_FOR {absID: 60336}]->(g)
CREATE (l)-[:USED_FOR {absID: 60336}]->(g)
CREATE (m)-[:SAMPLED_FROM {absID: 60336}]->(a)
CREATE (m)-[:SAMPLED_FROM {absID: 60336}]->(b)
CREATE (m)-[:ANALYZED_BY {absID: 60336}]->(k)
CREATE (n)-[:SAMPLED_FROM {absID: 60336}]->(a)
CREATE (n)-[:SAMPLED_FROM {absID: 60336}]->(b)
CREATE (n)-[:ANALYZED_BY {absID: 60336}]->(k)