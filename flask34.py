from flask import Flask, request, jsonify, render_template
from medbot import calculate_bmi, drug_info, explain_symptom, chat_with_medical_bot, is_prescription_request, PRESCRIPTION_REFUSAL_MSG

app = Flask(__name__, template_folder="templates")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    try:
        # Handle BMI command
        if user_message.lower().startswith("bmi"):
            try:
                _, weight, height = user_message.split()
                response = calculate_bmi(float(weight), float(height))
                return jsonify({"response": response})
            except:
                return jsonify({"response": "⚠️ Usage: bmi <weight_kg> <height_cm>"})

        # Handle drug command
        if user_message.lower().startswith("drug "):
            drug_name = user_message.split(maxsplit=1)[1]
            if is_prescription_request(user_message):
                return jsonify({"response": PRESCRIPTION_REFUSAL_MSG})
            return jsonify({"response": drug_info(drug_name)})

        # Handle symptom command
        if user_message.lower().startswith("symptom "):
            symptom = user_message.split(maxsplit=1)[1]
            return jsonify({"response": explain_symptom(symptom)})

        # Otherwise use OpenAI model for general Q&A
        response = chat_with_medical_bot(user_message)
        return jsonify({"response": response})

    except Exception as e:
        return jsonify({"response": f"⚠️ Error: {str(e)}"})


if __name__ == "__main__":
    app.run(debug=True)
