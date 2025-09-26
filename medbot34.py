
from openai import OpenAI

client = OpenAI(
    api_key="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")

# Safety helpers

PRESCRIPTION_REFUSAL_MSG = (
    "Sorry — I cannot prescribe medications, provide personalized treatment plans, "
    "or give dosing tailored to an individual's medical condition. "
    "Prescribing requires a licensed healthcare professional who knows the patient's history. "
    "I can, however, provide educational information about conditions, commonly used drug classes, "
    "mechanisms, typical side effects, and safety warnings. "
    "If you need a prescription or medical advice, please consult a licensed clinician or emergency services."
)


def is_prescription_request(text):
    text_lower = text.lower()
    # simple heuristics — triggers if user explicitly asks to 'prescribe', 'give me a prescription', 'what medicine should i take for <x>', etc.
    triggers = ["prescribe", "prescription", "what medicine should i take", "what drug should i take",
                "give me medicine", "which medication should i take"]
    return any(t in text_lower for t in triggers)


# Utilities (non-prescriptive)

def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    if bmi < 18.5:
        category = "Underweight"
    elif 18.5 <= bmi < 24.9:
        category = "Normal weight"
    elif 25 <= bmi < 29.9:
        category = "Overweight"
    else:
        category = "Obese"
    return f"Your BMI is {bmi:.2f} ({category})."


#  local drug "encyclopedia"  (educational only ,not a prescription)
DRUG_DB = {
    "paracetamol": {
        "class": "Analgesic/antipyretic",
        "uses": "Pain relief and fever reduction.",
        "common_side_effects": "Rare at therapeutic doses; high doses risk liver injury.",
        "notes": "Avoid exceeding recommended max daily dose. For specific dosing consult product instructions or a clinician."
    },
    "ibuprofen": {
        "class": "Nonsteroidal anti-inflammatory drug (NSAID)",
        "uses": "Pain, inflammation, fever.",
        "common_side_effects": "Gastrointestinal upset, increased bleeding risk, renal effects with long-term/high-dose use.",
        "notes": "Use caution in people with GI bleeding risk, kidney disease, or on anticoagulants."
    },

}


def drug_info(drug_name):
    entry = DRUG_DB.get(drug_name.lower())
    if not entry:
        return "I don't have that drug in my local database. I can look up general information (educational) if you want — or you can ask me to add it to the local DB."
    info_lines = [
        f"Name: {drug_name.capitalize()}",
        f"Drug class: {entry['class']}",
        f"Common uses: {entry['uses']}",
        f"Common side effects: {entry['common_side_effects']}",
        f"Important notes: {entry['notes']}",
        "",
        "?? Reminder: This is educational information only — not a prescription or medical advice."
    ]
    return "\n".join(info_lines)


def explain_symptom(symptom):
    SYMPTOMS = {
        "headache": "Headaches have many causes: tension, migraine, dehydration, sinusitis, high blood pressure, etc. Seek urgent care for sudden severe headache or neurological deficits.",
        "fever": "Fever is usually a sign of infection or inflammation. Persistent high fever or associated severe symptoms should be evaluated by a clinician."
    }
    return SYMPTOMS.get(symptom.lower(),
                        "I can explain some common symptoms. If this is urgent or severe, seek medical care.")


#  Medical Q&A (non-personalized)

def chat_with_medical_bot(prompt):
    # If user asks for a prescription, refuse immediately.
    if is_prescription_request(prompt):
        return PRESCRIPTION_REFUSAL_MSG

    messages = [
        {
            "role": "system",
            "content": (
                "You are MedBot, an educational medical assistant. You must NOT provide personalized medical advice, diagnoses, "
                "or prescriptions. If the user asks for prescriptions or individualized treatment, refuse and direct them to a licensed clinician. "
                "You may provide general, non-personalized medical information, explain conditions, outline common treatment options in high-level "
                "terms (educational), describe drug classes, mechanisms, and safety warnings. Always include a clear disclaimer when appropriate."
            )
        },
        {"role": "user", "content": prompt}
    ]

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return resp.choices[0].message.content.strip()


if __name__ == "__main__":
    print(
        "?? MedBot (safe mode): I cannot prescribe medications. Ask about conditions, drugs (educational), or use commands: bmi, drug, symptom.")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["quit", "exit", "bye"]:
            print("?? MedBot: Goodbye — seek a clinician for prescriptions.")
            break

        if user_input.lower().startswith("bmi"):
            try:
                _, weight, height = user_input.split()
                print(calculate_bmi(float(weight), float(height)))
            except Exception:
                print("Usage: bmi <weight_kg> <height_cm>")
            continue

        if user_input.lower().startswith("drug "):
            drug_name = user_input.split(maxsplit=1)[1]
            # If user asks "drug prescribe" or asks to prescribe, refuse
            if is_prescription_request(user_input):
                print(PRESCRIPTION_REFUSAL_MSG)
            else:
                print(drug_info(drug_name))
            continue

        if user_input.lower().startswith("symptom "):
            symptom = user_input.split(maxsplit=1)[1]
            print(explain_symptom(symptom))
            continue

        print(chat_with_medical_bot(user_input))
