#
# This program takes an image of a workflow, generates a text description
# and attempts to generate a python program that implements the workflow.
#

import base64
import requests
import os
# import openai
import re


# OpenAI API Key
api_key = os.getenv("OPENAI_API_KEY")


# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

#
# Does some cleanup and possibly sanity checks in the future
#
def extract_text_between_backticks(text):
    # Regular expression pattern to match text between triple backticks
    pattern = r'```(.*?)```'

    # Find all matches in the text
    matches = re.findall(pattern, text, re.DOTALL)

    return matches

def perform_diagnostic():
    #
    # START Diagnostic information
    #
    def count_words(string):
        # Split the string into words
        words = string.split()

        # Count the number of words
        return len(words)

    # Example usage
    example_string = "Hello, this is an example string."
    word_count = count_words(example_string)
    print("Number of words:", word_count)
    # print("system: "+count_words(file_contents)
    print(f"system: {file_contents}")
    print(f"user: {prompt}")
    #
    # END Diagnostic information
    #

def remove_python_lines(file_path):
    # Define the word to filter out
    filter_word = "python"
    
    # Open the original file in read mode and a new file in write mode
    with open(file_path, 'r') as file, open('gen_code.py', 'w') as output_file:
        # Iterate over each line in the file
        for line in file:
            # Strip whitespace from the start and end of the line
            stripped_line = line.strip()
            
            # Check if the line is exactly the word 'Python'
            if stripped_line != filter_word:
                # If not, write the line to the output file
                output_file.write(line)


# Path to your image
# TODO: make configurable by user
image_path = "/Users/dpang/dev/together/data/flow.jpg"

# Getting the base64 string
base64_image = encode_image(image_path)

headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {api_key}"
}

#
# START: Make the call to Openai to get a summary of the image
#
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
  model="gpt-4o-mini",
  messages=[
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Summarize the workflow in the image in the following way in less than 50 words: A step labeled ? followed. by a step labeled ? where the question mark is filled by the text detected in the boxes"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image}"
          },
        },
      ],
    }
  ],
  max_tokens=300,
)

print(response.choices[0])

##prompt = response.json()['choices'][0]['message']['content']
prompt = response.choices[0].message.content
print("OpenAI results: " + prompt)
#
# END: Openai call
#

#
# START: Take the summary and try to produce code
#
# Define the path to your file
file_path = 'data/promptcode.txt' # This file holds instructions for the LLM to generate code
prompt_path = 'data/prompt.txt'   # This file is an example prompt for testing.  Represents the output/summary from the vision model

# Open the file and read its contents
with open(file_path, 'r') as file:
    file_contents = file.read()

# file_contents now holds the contents of the file as a string
# print(file_contents)

# Open the prompt file and read its contents
# with open(prompt_path, 'r') as file:
#     prompt = file.read()

print("Input: " + prompt)

#
# Call the LLM to generate code
#

client = OpenAI()

response = client.chat.completions.create(
  model="gpt-4o-mini",
  messages=[
    {
      "role": "system",
      "content": file_contents + ". Write main code",
    },
    {
      "role": "user",
      "content": prompt,
    }
  ],
  max_tokens=16384,
)

print(response.choices[0])

answer = response.choices[0].message.content

#
# END: Take the summary and try to produce code
#
# print(chat_completion)

extracted_text = extract_text_between_backticks(answer)

# File path where you want to write the code out to 
file_path = "code_output.py"

# Open the file in write mode
with open(file_path, 'w') as file:
    # Iterate over the list and write each string to the file
    for etext in extracted_text:
        file.write(etext + '\n')  # Add a newline character after each string

remove_python_lines(file_path)
for etext in extracted_text:
    print("====")
    print(etext)
    print("====")
# print("========Extracted text:", extracted_text)
