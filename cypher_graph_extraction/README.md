# GPT4o/ Llama3 exporting Neo4j Cypher code

Host-pathogen relation extraction project (Glasgow CompBio Hackathon 2024)
@ulad-litvin

## Background

From:
https://docs.google.com/document/d/1ZWun7tmlIXQW0SV_MtTfjSMiNeOhOk5oFifJ7K1osX0/edit?usp=sharing

Neo4j is a graph database management system (GDBMS) that relies on Cypher Query Language to operate. Graph databases are made up of two main components: (1) nodes that can have labels and properties and (2) one-directional relationships that connect different nodes and can have labels and properties of their own.

You can download Neo4j Desktop app that allows you to create, visualise and query graph databases here: https://neo4j.com/download/

Crash course on Neo4j Desktop: https://www.youtube.com/watch?v=8jNPelugC2s

## Folders

1. [llama3_prompts](./llama3_prompts/) folder contains "simple", "basic" and "advanced" prompts used to generate Cypher code with Llama3 on MARS.
2. [neo4j_visualisation](./neo4j_visualisation/) folder contains images of Neo4j graphs generated with GPT4o and visualised with Neo4j Desktop.
3. [notebooks](./notebooks/) folder contains UL's jupyter notebooks created during CompBio Hackathon.
4. [obsidian_notes](./obsidian_notes/) folder contains UL's notes created during CompBio Hackathon.
5. [simple_result](./simple_result/) folder contains examples of Cypher code extracted with Llama3 on MARS using "simple prompt".
