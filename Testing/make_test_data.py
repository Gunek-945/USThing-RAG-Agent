#utility script to convert the testing-questions.json file into the format of template_json.json

import json

# Load the questions from the testing-questions.json file
with open('Testing/testing-questions.json', 'r') as file:
    data = json.load(file)

# Prepare the structured data in the format of template_json.json
structured_data = {
    "description": "test of 58 questions",
    "conversations": []
}

# Example scores (you can modify these as needed)
humour_score = 1
rudeness_score = 1
flirtiness_score = 1

# Define namespaces for each category
namespaces = {
    'faculty': 'faculty',
    'academic': 'academic',
    'student_life': 'student_life',
    'irrelevant_questions': None
}

# Populate the conversations list
test_id = 1
for category, questions in data.items():
    for question in questions:
        conversation = {
            "test_id": test_id,
            "user_input": f"User: {question}",
            "humour_score": humour_score,
            "rudeness_score": rudeness_score,
            "flirtiness_score": flirtiness_score,
            "template_id": 2,
            "namespace": namespaces[category]
        }
        structured_data["conversations"].append(conversation)
        test_id += 1

# Save the structured data to template_json.json
with open('Testing/test.json', 'w') as file:
    json.dump(structured_data, file, indent=4)

print("Data has been structured and saved to test.json.")

print("Data has been structured and saved to test.json. test size is", len(structured_data["conversations"]))