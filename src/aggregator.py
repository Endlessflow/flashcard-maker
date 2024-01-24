import os
from time import time
import re
from src.fileUtils import open_file, save_file
import pickle
from src.gptHandler import FACT_CHECK_SYSTEM_PROMPT_PATH, FACT_CHECK_USER_PROMPT_PATH, FACT_CHECK_CONTENT_PLACEHOLDER, chatgpt_completion, construct_messages


def extract_questions(text):
    question_pattern = r'Q: (.*?)\nA: (.*?)\nE: (.*?)\nT: (.*?)\n'
    questions = re.findall(question_pattern, text, re.DOTALL)
    return questions


def escape_quotes(text):
    return text.replace('"', '""')


def format_question_for_anki(question_data):
    question, answer, extra, tags = question_data
    formatted_question = escape_quotes(question.replace('&', '&amp;').replace(
        '<', '&lt;').replace('>', '&gt;').replace('\n', '<br>'))
    formatted_answer = escape_quotes(answer.replace('&', '&amp;').replace(
        '<', '&lt;').replace('>', '&gt;').replace('\n', '<br>'))
    formatted_extra = escape_quotes(extra.replace('&', '&amp;').replace(
        '<', '&lt;').replace('>', '&gt;').replace('\n', '<br>'))
    formatted_tags = escape_quotes(tags.replace('&', '&amp;').replace(
        '<', '&lt;').replace('>', '&gt;').replace('\n', '<br>').replace(
        ', ', 'delimiter').replace(' ', '_').replace('delimiter', ' '))
    return f'"{formatted_question}"\t"{formatted_answer}"\t"{formatted_extra}"\t"{formatted_tags}"'


def swap_extra_field_for_response(question_data, response):
    question, answer, extra, tags = question_data
    return question, answer, response, tags


def format_question_for_fact_check(question_data):
    question, answer, extra, tags = question_data
    return f'Q: {question}\nA: {answer}\nE: {extra}\nT: {tags}'


def save_to_pickle(data, file_path):
    # create the backup directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'wb') as f:
        pickle.dump(data, f)


def load_from_pickle(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)


def aggregate_questions(input_dir,  backup_file_path='data/backup.pickle'):
    aggregated_questions = {}

    if os.path.exists(backup_file_path):
        aggregated_questions = load_from_pickle(backup_file_path)

    if os.path.exists(input_dir) == False:
        return aggregated_questions

    file_list = [file_name for file_name in os.listdir(
        input_dir) if file_name.endswith('_reply.txt')]
    total_files = len(file_list)

    for index, file_name in enumerate(file_list):
        base_name = file_name.rsplit('_page', 1)[0]
        file_path = os.path.join(input_dir, file_name)
        content = open_file(file_path)
        print(
            f"Fact checking question in {file_name} - progress: {index + 1}/{total_files}")

        if base_name not in aggregated_questions:
            aggregated_questions[base_name] = []

        if content != 'No relevant content.':
            questions = extract_questions(content)
            total_questions = len(questions)
            for question_index, question_data in enumerate(questions):
                print(
                    f"Handling question {question_index + 1}/{total_questions}")
                match_found = False
                for question in aggregated_questions[base_name]:
                    normal_question = question
                    if question_data[0] in normal_question.replace('<br>', '\n').replace(
                            '""', '"'):
                        match_found = True

                if match_found == False:
                    formatted_question_normal = format_question_for_fact_check(
                        question_data)
                    message = construct_messages(formatted_question_normal, FACT_CHECK_CONTENT_PLACEHOLDER,
                                                 FACT_CHECK_SYSTEM_PROMPT_PATH, FACT_CHECK_USER_PROMPT_PATH)
                    response = chatgpt_completion(message)
                    question_data = swap_extra_field_for_response(
                        question_data, response)
                    formatted_question_anki = format_question_for_anki(
                        question_data)
                    aggregated_questions[base_name].append(
                        formatted_question_anki)
                    # Save aggregated_questions to pickle file after appending a question
                    save_to_pickle(aggregated_questions, backup_file_path)
    return aggregated_questions


def save_aggregated_questions(aggregated_questions, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for base_name, questions in aggregated_questions.items():
        output_file_name = f'{base_name}_anki.txt'
        output_file_path = os.path.join(output_dir, output_file_name)
        anki_questions = '\n'.join(questions)
        save_file(output_file_path, anki_questions)
    # rename backup pickle to file to `{timestamp}_backup.pickle}`
    # os.rename('backup/backup.pickle', f'backup/{time()}_backup.pickle')


def process_text_files(input_dir, output_dir):
    aggregated_questions = aggregate_questions(input_dir)
    save_aggregated_questions(aggregated_questions, output_dir)
