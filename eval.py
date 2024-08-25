from groq import Groq
import re
import json
from dotenv import load_dotenv

import statistics
load_dotenv()

client = Groq()
"""
completion = client.chat.completions.create(
    model="llama3-8b-8192",
    messages=[
        {
            "role": "system",
            "content": "Please rate the mood level in the provided text. Give me a number between (1-5), with  1 being the lowest and 5 being the highest level,respectively. Your reponse should be a JSON file {\"Rating\": RATING}"
        },
        {
            "role": "user",
            "content": "Mood: Humour; Text: \"Starting a new society at HKUST, eh? That's a great way to make your mark on campus! \\n\\nAccording to the Student Support & Activities Team, you're recommended to prepare a proposal and seek advice from them. They're more than happy to help you out! You can reach out to them through email at ssa@ust.hk, give them a call at 2358 6662, or visit them in person at LG3005, Student Support & Activities Counter, Indoor Sports Complex, Clear Water Bay Campus, HKUST. Just make sure to drop by during their office hours, which are Monday to Friday, 0900-1245, 1400-1730, except public holidays.\\n\\nThat's it! Simple, right? Now, go ahead and take the first step towards creating an amazing new society at HKUST!\\n\\nSource: student_organizations.txt\""
        }
    ],
    temperature=0,
    max_tokens=1024,
    top_p=1,
    stream=False,
    response_format={"type": "json_object"},
    stop=None,
)

print(completion.choices[0].message)
"""

models=['llama3-8b-8192', "gemma2-9b-it", "mixtral-8x7b-32768"]
moods= ['Humour', 'Rudeness', 'Flirtiness']

def get_first_number(input_string):
    """
    Extracts the first number from a given string.
    
    Args:
        input_string (str): The input string to search for a number.
        
    Returns:
        int or None: The first number found in the string, or None if no number is found.
    """
    match = re.search(r'\d+', input_string)
    if match:
        return int(match.group())
    else:
        return None

def rate_response(model_name, mood, evaluated_reponse):
    completion = client.chat.completions.create(
    model=model_name,
    messages=[
        {
            "role": "system",
            "content": "Please rate the mood level in the provided text. Give me a number between (1-5), with  1 being the lowest and 5 being the highest level,respectively. Your reponse should be a JSON file {\"Rating\": RATING}"
        },
        {
            "role": "user",
            "content": f"Mood: {mood}; Text: {evaluated_reponse}"
        }
    ],
    temperature=0,
    max_tokens=1024,
    top_p=1,
    stream=False,
    response_format={"type": "json_object"},
    stop=None,
    )
    rating= get_first_number(completion.choices[0].message.content) #don't know why it is actually a string
    return rating

def eval_single_convo(evaluated_reponse):
    mood_scores=[] #in the order of the moods 
    for mood in moods:
        scores=[]
        for model in models:
            model_score= rate_response(model_name=model, mood=mood, evaluated_reponse=evaluated_reponse)
            scores.append(model_score)
        final_score= statistics.mean(scores)
        mood_scores.append(final_score)
    result = dict(zip(moods, mood_scores))
    return result


def eval(json_file_path):
    with open(json_file_path, 'r+') as file:
        data = json.load(file)
        conversations_list = data['conversations']
        for convo in conversations_list:
            print(f"Evaluating test {convo['test_id']}")
            convo['Evaluation']=eval_single_convo(convo['response'])
        # Move the file pointer back to the beginning
        file.seek(0)

        # Write the updated data back to the file
        json.dump(data, file, indent=4)

        # Truncate the file to the current position of the file pointer
        file.truncate()

if __name__=="__main__":
    eval(r"Testing\uniform.json")