import pandas as pd
import json
import time
import random
import numpy as np
import re
import gc
import os
from gpt4all import GPT4All

# Set random seeds for reproducibility
random_seed = 42
random.seed(random_seed)
np.random.seed(random_seed)

# Load model names from file
with open('./model_for_choose.txt', 'r') as file:
    file_content = file.read()
model_names = re.findall(r'"filename":\s*"([^"]+)"', file_content)

# Import abstract data
ab_path = '../raw_data/hp_abstracts.tsv'
ab_data = pd.read_csv(ab_path, delimiter='\t')

# Import prompt IDs
id_path = '../raw_data/prompt_design_absIDs.csv'
abs_id = pd.read_csv(id_path)
absIDs = list(abs_id['absID'])

# Get the list of abstracts
Abstract_list = list(ab_data['abs'])

# Load the first prompt
with open('./prompts/prompt1.txt', 'r') as file:
    prompt1 = file.read()

# Loop through each model starting from the fifth one
for model_choose in model_names[6:]:
    print('Attempting to use model name: ' + model_choose)

    try:
        # Load the model
        model = GPT4All(model_choose, device='kompute:NVIDIA RTX A6000')
    except Exception as e:
        print(f"Error loading model {model_choose}: {e}")
        continue  # Skip to the next model

    # Process each abstract with the prompt
    all_results = []

    for i in range(len(absIDs)):
        absID = absIDs[i]
        ab = Abstract_list[absID - 1]

        start_time = time.time()  # Start timing
        input_text = prompt1 + '\n' + ab
        generated_text = ''

        try:
            with model.chat_session():
                for token in model.generate(input_text, streaming=True):
                    generated_text += token
        except Exception as e:
            print(f"Error generating text for absID {absID} with model {model_choose}: {e}")
            continue  # Skip to the next abstract

        # Process the generated JSON results
        json_match = re.search(r'\{.*?\}', generated_text, re.DOTALL)
        if json_match:
            try:
                json_str = json_match.group(0)
                result_data = json.loads(json_str)
                host_list = result_data.get('Host', [])
                pathogen_list = result_data.get('Pathogen', [])

                # Ensure all lists have the same length
                max_len = max(len(host_list), len(pathogen_list))
                host_list.extend([''] * (max_len - len(host_list)))
                pathogen_list.extend([''] * (max_len - len(pathogen_list)))

                # Collect results into a DataFrame
                df_temp = pd.DataFrame({
                    'absID': [absID] * max_len,
                    'Host': host_list,
                    'Pathogen': pathogen_list
                })

                all_results.append(df_temp)

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for absID {absID}: {e}")
        else:
            print(f"No valid JSON string found for absID {absID}")

        end_time = time.time()  # End timing
        elapsed_time = end_time - start_time  # Calculate elapsed time
        print(f"Processed absID {absID}: Time taken: {elapsed_time} seconds")  # Print timing

    # Combine all results into a single DataFrame
    if all_results:
        df_all_results = pd.concat(all_results, ignore_index=True)

        # Save results to a CSV file
        output_path = f'./output/{model_choose}_result.csv'
        df_all_results.to_csv(output_path, index=False)
        print(f"Saved results to {output_path}")

    # Clean up
    del model  # Delete the model object
    gc.collect()  # Run garbage collection

    # Optionally delete the model files from disk
    model_file_path = f'~/.cache/gpt4all/{model_choose}'
    if os.path.exists(model_file_path):
        os.remove(model_file_path)
        print(f"Deleted model file: {model_file_path}")
    else:
        print(f"Model file not found: {model_file_path}")

    print("Model resources released.")

    # Pause for 1 minute to allow GPU to recover
    print("Pausing for 20s to allow GPU to recover...")
    time.sleep(20)

print("Processing complete.")
