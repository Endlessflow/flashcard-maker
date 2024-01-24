import openai
import os
from time import time, sleep

from src.fileUtils import open_file, save_file

openai.api_key = open_file('assets/openaiapikey.txt')

QUESTION_SYSTEM_PROMPT_PATH = 'assets/prompts/flashcard_generator_system.txt'
QUESTION_USER_PROMPT_PATH = 'assets/prompts/flashcard_generator_user.txt'
QUESTION_CONTENT_PLACEHOLDER = '<< CONTENT >>'

FACT_CHECK_SYSTEM_PROMPT_PATH = 'assets/prompts/fact_check_system.txt'
FACT_CHECK_USER_PROMPT_PATH = 'assets/prompts/fact_check_user.txt'
FACT_CHECK_CONTENT_PLACEHOLDER = '<< CONTENT >>'


def construct_messages(content, placeholder, system_prompt_path, user_prompt_path):
    system_prompt = open_file(system_prompt_path)
    user_prompt = open_file(user_prompt_path)
    user_prompt = user_prompt.replace(placeholder, content)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    return messages


def chatgpt_completion(messages, model="gpt-3.5-turbo", max_retries=10, initial_backoff=1):
    retries = 0
    backoff = initial_backoff
    while retries <= max_retries:
        try:
            #print('sending a query to OpenAI')
            response = openai.ChatCompletion.create(
                model=model, messages=messages, temperature=0, max_tokens=2048)
            #print('received a response from OpenAI')
            text = response['choices'][0]['message']['content']
            stop_reason = response['choices'][0]['finish_reason']
            save_chat_log(messages, text, stop_reason)
            return text
        except Exception as e:
            print(f"Error: {e}. Retrying in {backoff} seconds...")
            sleep(backoff)
            retries += 1
            backoff *= 2

    print("Failed to send the request after several retries. Exiting the program.")
    exit(1)


def save_chat_log(messages, text, stop_reason, logs_dir='archive/gpt3_logs'):
    filename = f"{time()}_chat.txt"
    log_content = str(messages) + '\n\n==========\n\n' + \
        text + '\n\n==========\n\n' + stop_reason
    os.makedirs(logs_dir, exist_ok=True)
    if stop_reason != 'stop':
        print(
            f"Warning: stop reason is {stop_reason} response might be incomplete.\n See log file: {filename} for more details.")
    save_file(os.path.join(logs_dir, filename), log_content)


def generate_question_per_page_in_folder(input_dir, output_dir, model="gpt-3.5-turbo"):
    file_list = [file_name for file_name in os.listdir(
        input_dir) if file_name.endswith('.txt')]
    total_files = len(file_list)

    for index, file_name in enumerate(file_list):
        output_file_name = f"{os.path.splitext(file_name)[0]}_reply.txt"
        input_file_path = os.path.join(input_dir, file_name)
        output_file_path = os.path.join(output_dir, output_file_name)
        os.makedirs(output_dir, exist_ok=True)

        if os.path.exists(output_file_path):
            print(f"Skipping {output_file_path} as it already exists.")
        else:
            content = open_file(input_file_path)
            messages = construct_messages(
                content, QUESTION_CONTENT_PLACEHOLDER, QUESTION_SYSTEM_PROMPT_PATH, QUESTION_USER_PROMPT_PATH)
            print(
                f"Generating questions for {file_name} - progress: {index + 1}/{total_files}")
            response = chatgpt_completion(messages, model=model)
            save_file(output_file_path, response)
