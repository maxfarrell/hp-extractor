import pandas as pd
import spacy
import time
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import networkx as nx
from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk import bigrams

# Load SpaCy English model for NER
nlp = spacy.load("en_core_web_sm")

# Load CSV file (Ensure you have enough RAM)
df = pd.read_csv('title_abstract_all.csv')

# Total number of rows
total_rows = len(df)

# Start timer
start_time = time.time()

# Improved entity extraction using batch processing
def extract_entities_batch(texts):
    entities_list = []
    for doc in tqdm(nlp.pipe(texts, disable=["tagger", "parser"]), total=len(texts), desc="Extracting Entities"):
        entities_list.append([(ent.text, ent.label_) for ent in doc.ents])
    return entities_list

# Apply entity extraction with progress tracking
df['entities'] = extract_entities_batch(df['title_abstract'].fillna(""))

# Print estimated time for entity extraction
end_time = time.time()
print(f"\nEntity extraction completed in {round((end_time - start_time) / 60, 2)} minutes.")

# Count entity types
entity_counts = defaultdict(int)
for entities in df['entities']:
    for ent, label in entities:
        entity_counts[(ent, label)] += 1

print("\nTop Entities by Type:")
for (ent, label), count in sorted(entity_counts.items(), key=lambda x: -x[1])[:20]:
    print(f"{ent} ({label}): {count}")

# Entity co-occurrence analysis
co_occurrence = defaultdict(int)
for entities in tqdm(df['entities'], total=total_rows, desc="Analyzing Entity Co-occurrence"):
    ents = [ent[0] for ent in entities]
    for i in range(len(ents)):
        for j in range(i+1, len(ents)):
            pair = tuple(sorted([ents[i], ents[j]]))
            co_occurrence[pair] += 1

print("\nTop Entity Relationships:")
for pair, count in sorted(co_occurrence.items(), key=lambda x: -x[1])[:15]:
    print(f"{pair[0]} -- {pair[1]}: {count}")

# TF-IDF analysis for important terms
start_tfidf = time.time()
tfidf = TfidfVectorizer(stop_words='english', max_features=100)
tfidf_matrix = tfidf.fit_transform(df['title_abstract'].dropna())
feature_names = tfidf.get_feature_names_out()
end_tfidf = time.time()
print(f"\nTF-IDF computation completed in {round((end_tfidf - start_tfidf), 2)} seconds.")

print("\nTop TF-IDF Terms:")
for term, score in sorted(zip(feature_names, tfidf_matrix.sum(axis=0).A1), key=lambda x: -x[1])[:20]:
    print(f"{term}: {score:.2f}")

# Bigrams analysis with progress tracking
all_bigrams = []
for text in tqdm(df['title_abstract'].dropna(), total=total_rows, desc="Extracting Bigrams"):
    tokens = text.lower().split()
    all_bigrams.extend(bigrams(tokens))

bigram_counts = Counter(all_bigrams).most_common(15)
print("\nTop Bigrams:")
for bigram, count in bigram_counts:
    print(f"{' '.join(bigram)}: {count}")

# Visualization 1: Entity Network
G = nx.Graph()
for pair, count in co_occurrence.items():
    if count > 2:  # Filter for significant relationships
        G.add_edge(pair[0], pair[1], weight=count)

plt.figure(figsize=(12, 12))
pos = nx.spring_layout(G, k=0.5)
nx.draw(G, pos, with_labels=True,
        node_size=50,
        font_size=8,
        edge_color='gray',
        width=[d['weight']*0.1 for (u,v,d) in G.edges(data=True)])
plt.title("Entity Relationship Network")
plt.show()

# Visualization 2: Improved TF-IDF Plot
top_terms = sorted(zip(feature_names, tfidf_matrix.sum(axis=0).A1), key=lambda x: -x[1])[:15]
terms, scores = zip(*top_terms)

plt.figure(figsize=(10, 6))
plt.barh(terms, scores, color='darkred')
plt.gca().invert_yaxis()
plt.title("Most Important Terms (TF-IDF)")
plt.xlabel("TF-IDF Score")
plt.tight_layout()
plt.show()

# Save structured results with progress tracking
print("\nSaving entity extraction results...")
entity_df = pd.DataFrame([
    {'Entity': ent, 'Type': label, 'Count': count}
    for (ent, label), count in entity_counts.items()
])
entity_df.to_csv('process_alldata_entities_0206.csv', index=False)
print("Entity results saved!")

print("\nSaving entity relationship results...")
relation_df = pd.DataFrame([
    {'Entity1': pair[0], 'Entity2': pair[1], 'Co-occurrences': count}
    for pair, count in co_occurrence.items()
])
relation_df.to_csv('process_alldata_relationships_0206.csv', index=False)
print("Relationship results saved!")

# Final time tracking
total_time = round((time.time() - start_time) / 60, 2)
print(f"\nTotal processing time: {total_time} minutes.")
