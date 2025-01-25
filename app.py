from flask import Flask, render_template, request, redirect, url_for, jsonify
from openai import OpenAI
from rag import initialize_rag, augment_prompt

client = OpenAI(api_key="")
embeddings, index, all_chunks = initialize_rag()

regulations_path = "./static/business_regulations.xlsx"

try:
    response = client.files.create(file=open(regulations_path, "rb"),
                                  purpose="assistants")
    print("File uploaded successfully!")
except Exception as e:
    print(f"Error uploading file: {e}")

import os
# Create Flask app
app = Flask(__name__)

# Configure app settings if needed
app.config['DEBUG'] = True


# functions

def extract_links(ai_message) :
    try:
        if not ai_message:
            raise ValueError("AI message is required")

        # Make a query to OpenAI for new suggestions
        response = client.chat.completions.create(
            model="gpt-4",  # Or "gpt-3.5-turbo"
            messages=[
                {"role": "system",
                 "content": "Extract only the href URLS from this message if any exist and return them as a list of links split by a newline character"},
                {"role": "user", "content": ai_message}
            ]
        )

        # Extract the four recommendations from the AI response
        gpt_response = response.choices[0].message.content.strip()

        # Assuming the response is a list of recommendations split by new lines
        links = gpt_response.split("\n")
        links = [link.strip() for link in links if link.strip()]
        print(links)
        return links
    except Exception as e:
        print(f"Error generating links: {e}")
        return []


def generate_tasks(ai_message) :
    try:
        if not ai_message:
            raise ValueError("AI message is required")

        response = client.chat.completions.create(
            model="gpt-4",
            messages = [
                {"role": "system", "content": "Generate up to three tasks based on the following input. Tasks should be a single short sentence that is something the user needs to do to start their business, based on the content of the message. Do not duplicate recommendations and keep them brief. "},
                {"role": "user", "content": ai_message}
            ]
        )
        gpt_response = response.choices[0].message.content.strip()

        tasks = gpt_response.split("\n")
        tasks = [rec.strip() for rec in tasks if rec.strip()][:3]
        print(tasks)
        return tasks

    except Exception as e:
        print(f"Error generating tasks: {e}")
        return []

def generate_suggestions(ai_message):
    try:
        if not ai_message:
            raise ValueError("AI message is required")

        # Make a query to OpenAI for new suggestions
        response = client.chat.completions.create(
            model="gpt-4",  # Or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "Generate four suggestions for follow up questions based on the following input. Recommendations should be a single short sentence or question. "},
                {"role": "user", "content": ai_message}
            ]
        )

        # Extract the four recommendations from the AI response
        gpt_response = response.choices[0].message.content.strip()

        # Assuming the response is a list of recommendations split by new lines
        recommendations = gpt_response.split("\n")
        recommendations = [rec.strip() for rec in recommendations if rec.strip()][:4]  # Limit it to 4
        print(recommendations)
        return recommendations
    except Exception as e:
        print(f"Error generating suggestions: {e}")
        return []


# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    try:
        # Generate RAG-augmented prompt
        if embeddings is None or index is None or not all_chunks:
            return jsonify({"error": "RAG components are not initialized."}), 500

        augmented_prompt = augment_prompt(user_input, embeddings, index, all_chunks)
        print(augmented_prompt)
        # Use augmented_prompt in OpenAI API call
        response = client.chat.completions.create(
            model="gpt-4",  # Or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": f"You are a helpful assistant. Respond to the prompt, wrapping any urls in the answer in <a> tags with the correct href and target blank to open in a new window. The user's specific business details are: {request.json.get('businessDetails')}. You should reference the user's specific business details in your responses when appropriate. Only mention resources for immigrant business owners if the user mentions being an immigrant. Prioritize the information provided in the context, and use your general knowledge when the context doesn't answer the question. Return the answer with html formatting included to bold, underline, and list items appropriately. If appropriate, query the business regulations spreadsheet for specific regulations or certifications that might be required."},
                {"role": "user", "content": augmented_prompt}
            ],
        )

        # Extract and print the AI message
        ai_message = response.choices[0].message.content
        print(ai_message)
        suggestions = generate_suggestions(ai_message)
        tasks = generate_tasks(ai_message)
        links = extract_links(ai_message)

        # Return AI response and suggestions
        return jsonify({
            "reply": ai_message,
            "recommendations": suggestions,
            "tasks" : tasks,
            "links" : links
        }), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "Something went wrong with the AI processing."}), 500

@app.route('/assistant')
def assistant():
    return render_template('assistant.html')

@app.route('/api/data', methods=['GET', 'POST'])
def api_data():
    if request.method == 'POST':
        data = request.json
        # Process the data here
        return jsonify({"message": "Data received", "data": data}), 200
    else:
        sample_data = {"key": "value"}
        return jsonify(sample_data)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0')