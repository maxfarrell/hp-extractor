CREATE (abstract:Abstract {absID: '61102', title: 'Sequence analysis of the complete S genomic segment of a newly identified hantavirus isolated from the white-footed mouse (Peromyscus leucopus): phylogenetic relationship with other sigmodontine rodent-borne hantaviruses'})

CREATE (virus1:Virus {absID: '61102', name: 'Four Corners virus', synonym: 'Sin Nombre virus'})
CREATE (virus2:Virus {absID: '61102', name: 'New York virus', synonym: 'NY virus'})

CREATE (condition:HantavirusPulmonarySyndrome {absID: '61102', name: 'Hantavirus Pulmonary Syndrome', acronym: 'HPS'})

CREATE (mouse1:Rodent {absID: '61102', name: 'deer mouse', scientificName: 'Peromyscus maniculatus'})
CREATE (mouse2:Rodent {absID: '61102', name: 'white-footed mouse', scientificName: 'Peromyscus leucopus'})

CREATE (region:ShelterIsland {absID: '61102', name: 'Shelter Island', state: 'New York'})
CREATE (region2:NortheasternUS {absID: '61102', name: 'Northeastern United States'})

CREATE (genomicSegment:GenomicSegment {absID: '61102', name: 'S segment', lengthNucleotides: 2078, openReadingFrameLength: 1284, proteinLengthAminoAcids: 428, noncodingRegionLength: 752})

CREATE (phyloAnalysis:PhylogeneticAnalysis {absID: '61102', name: 'Phylogenetic Analysis'})
CREATE (pairwiseAnalysis:PairwiseAnalysis {absID: '61102', name: 'Pairwise Analysis', nucleotideDifference: '16.6-17.8%', aminoAcidDifference: '7.0-8.2%'})

CREATE (sigmodontineRodents:RodentGroup {absID: '61102', name: 'Sigmodontine rodents'})

CREATE (virus1)-[:CAUSES {absID: '61102'}]->(condition)
CREATE (virus2)-[:CAUSES {absID: '61102'}]->(condition)

CREATE (mouse1)-[:HARBORS {absID: '61102'}]->(virus1)
CREATE (mouse2)-[:HARBORS {absID: '61102'}]->(virus2)

CREATE (region)-[:LOCATION_OF {absID: '61102'}]->(virus2)
CREATE (region2)-[:LOCATION_OF {absID: '61102'}]->(condition)

CREATE (virus2)-[:HAS_GENOMIC_SEGMENT {absID: '61102'}]->(genomicSegment)
CREATE (virus2)-[:ANALYZED_BY {absID: '61102'}]->(phyloAnalysis)
CREATE (virus2)-[:ANALYZED_BY {absID: '61102'}]->(pairwiseAnalysis)

CREATE (virus1)-[:ANALYZED_BY {absID: '61102'}]->(pairwiseAnalysis)

CREATE (phyloAnalysis)-[:COMPARES {absID: '61102'}]->(virus1)
CREATE (phyloAnalysis)-[:COMPARES {absID: '61102'}]->(virus2)
CREATE (phyloAnalysis)-[:INVOLVES {absID: '61102'}]->(sigmodontineRodents)

CREATE (pairwiseAnalysis)-[:COMPARES {absID: '61102'}]->(virus1)
CREATE (pairwiseAnalysis)-[:COMPARES {absID: '61102'}]->(virus2)

CREATE (genomicSegment)-[:PART_OF {absID: '61102'}]->(virus2)
CREATE (virus1)-[:RELATED_TO {absID: '61102', relation: 'more similar to'}]->(virus2)