import json

def test_json():
    with open('Testing/uniform_copy.json', 'r+') as file:
        data = json.load(file)
        conversations_list = data['conversations']
        for convo in conversations_list:
            convo['response']= "dummy"
        # Move the file pointer back to the beginning
        file.seek(0)

        # Write the updated data back to the file
        json.dump(data, file, indent=4)

        # Truncate the file to the current position of the file pointer
        file.truncate()

test_json()