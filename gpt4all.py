import pandas as pd
import re
import time
import random
import numpy as np
from gpt4all import GPT4All
from prompts_sets import prompts

# Set random seeds for reproducibility
random_seed = 42
random.seed(random_seed)
np.random.seed(random_seed)

# Initialize the model
model = GPT4All("Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf", device='kompute:NVIDIA RTX A6000')

# Data import
ab_path = 'raw_data/hp_abstracts.tsv'
ab_data = pd.read_csv(ab_path, delimiter='\t')

# Prompt id test
id_path = './raw_data/prompt_design_absIDs.csv'
abs_id = pd.read_csv(id_path)
absIDs = list(abs_id['absID'])

# Get the first column of ab_data as a list
prelimeter = 'Abstract: '
Abstract_list = list(ab_data['abs'])

# Process each abstract with the first prompt
all_results = []

for i in range(len(absIDs)):
    absID = absIDs[i]
    ab = Abstract_list[absID-1]

    # Only use the first prompt (prompt 1, based on the code)
    p = 1

    start_time = time.time()  # Start timing
    input_text = prelimeter + ab + '\n' + prompts[p] + '\n'
    generated_text = ''

    with model.chat_session():
        for token in model.generate(input_text, streaming=True):
            generated_text += token
    print(generated_text)
    end_time = time.time()  # End timing
    elapsed_time = end_time - start_time  # Calculate elapsed time
    print(f"Prompt {p} for absID {absID}: Time taken: {elapsed_time} seconds")  # Print timing
    # Append the generated text and absID as a tuple
    all_results.append((generated_text, absID))
    print(all_results)
# Convert results to DataFrame
df = pd.DataFrame(all_results, columns=['Generated Text', 'absID'])

# Save all results to a CSV file
output_path = f'./prompt_results/prompt1.csv'
df.to_csv(output_path, index=False)
print(f"Saved results to {output_path}")  # Debug output

print("Processing complete.")
