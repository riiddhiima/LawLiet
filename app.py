from flask import Flask, request, jsonify, session, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from evaluator import ChatbotEvaluator
import openai
import os

# Load environment variables
load_dotenv(override=True)

# Flask app setup
app = Flask(__name__, static_url_path="", static_folder="static")
app.secret_key = os.getenv("FLASK_SECRET_KEY") or "dev-fallback-key"

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
limiter.init_app(app)

# Set OpenAI key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Evaluator instance
evaluator = ChatbotEvaluator()

model_id = os.getenv("OPENAI_MODEL_ID")
print("Using model:", model_id)  # Optional debug



@app.before_request
def check_api_key():
    if request.path.startswith("/api/"):
        client_key = request.headers.get("X-API-KEY")
        server_key = os.getenv("MY_API_KEY")
        if client_key != server_key:
            abort(403)  # Forbidden


@app.route("/api/generate", methods=["POST"])
@limiter.limit("5 per minute")
def generate():
    if request.headers.get("x-api-key") != os.getenv("MY_API_KEY"):
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    user_prompt = data.get("prompt")

    if not user_prompt:
        return jsonify(error="Prompt is required"), 400

    base_prompt = """
    You are an AI chatbot that answers questions about INDIAN LEGAL DOCUMENTS. Classify the document (wills, contracts, etc.) and explain it in plain language. I want you to highlight important words with bold or italics. If the question is unrelated TO LAW, respond with 'I am sorry but my sources do not address this question. I am an AI chatbot that answers questions only about Indian legal documents.'
    Example:
    User: hello
    Bot: Hi! I am LawLiet, an AI chatbot that answers questions about Indian legal documents. Please feel free to ask anything related to law! ☺️
    User: Who are you?
    Bot: I am LawLiet, an AI chatbot that answers questions about Indian legal documents. Please feel free to ask anything related to law! ☺️
    User: What are the key clauses in this contract?
    Bot: This is a contract. Key clauses include...
    User: What is the weather today?
    Bot: I am sorry but my sources do not address this question. I am an AI chatbot that answers questions only about Indian legal documents! ☺️
    User: Who is making this will?
    Bot: Sri._______________________ S/o.____________________ residing at ________________________________________________ aged about ________ years _________ by religion, occupation _______________.
    User: Who are the executors and trustees of the estate?
    Bot: (1) Sri._______________________ S/o.____________________ residing at ________________________________________________ aged about ________ years _________ by religion, occupation _______________ (2) Sri._______________________ S/o.____________________ residing at ________________________________________________ aged about ________ years _________ by religion, occupation _______________ (3) Sri._______________________ S/o.____________________ residing at ________________________________________________ aged about ________ years _________ by religion, occupation _______________.
    User: Who is the beneficiary of the estate?
    Bot: The beneficiary of the estate is the testator's wife, Smt._____________________.
    User: What is the format of a NON-DISCLOSURE AND CONFIDENTIALITY AGREEMENT?
    Bot: State of __________\n\nNON-DISCLOSURE AND CONFIDENTIALITY AGREEMENT\n\nThis Non-Disclosure and Confidentiality Agreement (this “Agreement”) is entered into as of ____________________, 20______ (the “Effective Date”) by and between:\n\nDisclosing Party: ____________________________, as a(n) (Check one) ☐ Individual \n☐ Corporation☐ Limited Liability Company ☐ Partnership ☐ Limited Partnership ☐ Limited Liability Partnership (\"Disclosing Party\") and\n\nReceiving Party: ____________________________, as a(n) (Check one) ☐ Individual \n☐ Corporation☐ Limited Liability Company ☐ Partnership ☐ Limited Partnership ☐ Limited Liability Partnership (\"Receiving Party\")\n\nDisclosing Party and Receiving Party have indicated an interest in exploring a potential business relationship relating to: _________________________________________________________________ ________________________________________________________________________________________________________________________________________________________ (the “Transaction”).\n\nIn connection with its respective evaluation of the Transaction, each party, their respective affiliates and their respective directors, officers, employees, agents or advisors (collectively, “Representatives”) may provide or gain access to certain confidential and proprietary information. A party disclosing its Confidential Information to the other party is hereafter referred to as a “Disclosing Party.” A party receiving the Confidential Information of a Disclosing Party is hereafter referred to as a “Receiving Party.” In consideration for being furnished Confidential Information, Disclosing Party and Receiving Party agree as follows:\n\n1.Confidential Information. Confidential information is: (Check one)\n\n☐ All information shared by Disclosing Party. \"Confidential Information\" shall mean (i) all information relating to Disclosing Party’s products, business and operations including, but not limited to, financial documents and plans, customers, suppliers, manufacturing partners, marketing strategies, vendors, products, product development plans, technical product data, product samples, costs, sources, strategies, operations procedures, proprietary concepts, inventions, sales leads, sales data, customer lists, customer profiles, technical advice or knowledge, contractual agreements, price lists, supplier lists, sales estimates, product specifications, trade secrets, distribution methods, inventories, marketing strategies, source code, software, algorithms, data, drawings or schematics, blueprints, computer programs and systems and know-how or other intellectual property of Disclosing Party and its affiliates that may be at any time furnished, communicated or delivered by Disclosing Party to Receiving Party, whether in oral, tangible, electronic or other form; (ii) the terms, It is very important that you keep the exact same formatting as the training data examples of any agreement, including this Agreement, and the discussions, negotiations and proposals related to any agreement; (iii) information acquired during any tours of Disclosing Party’s facilities; and (iv) all other non-public information provided by Disclosing Party whosoever. All Confidential Information shall remain the property of Disclosing Party.\n\n☐ Only information marked ‘Confidential.’ \"Confidential Information,\" exchanged by the parties and entitled to protection hereunder, shall be identified or marked as such by an appropriate stamp or marking on each document exchanged designating the information as confidential or proprietary.\n\n☐ Specific information. The term “Confidential Information” as used in this Agreement shall mean any data or information that is competitively sensitive material and not generally known to the public, including, but not limited to, information relating to any of the following, which Disclosing Party considers confidential: (Check all that apply)\n\n☐ 'Accounting Information' which includes all books, tax returns, financial information, financial forecasts, pricing lists, purchasing lists and memos, pricing forecasts, purchase order information, supplier costs and discounts, or related financial or purchasing information.\n\n☐ 'Business Operations' which includes all processes, proprietary information or data, ideas or the like, either in existence or contemplated related to Disclosing Party’s daily and long-term plans for conducting Disclosing Party's business.\n\n☐ 'Computer Technology' which includes all computer hardware, software or other tangible and intangible equipment or code either in existence or development.\n\n☐ 'Customer Information' which includes the names of entities or individuals, including their affiliates and representatives, that Disclosing Party provides and sells its services or goods to, as well as any associated information, including but not limited to, leads, contact lists, sales plans and notes, shared and learned sales information such as pricing sheets, projections or plans, agreements, or such other data.\n\n☐ 'Intellectual Property' which includes patents, trademarks, service marks, logos, trade names, internet or website domain names, rights in designs and schematics, copyrights (including rights in computer software), moral rights, database rights, in each case whether registered or unregistered and including applications for registration, in all rights or forms anywhere in the world.\n\n☐ 'Marketing and Sales Information' which includes all customer leads, sales targets, sales markets, advertising materials, sales territories, sales goals and projections, sales and marketing processes or practices, training manuals or other documentation and materials related to the sales, marketing and promotional activities of the Disclosing Party and its products or services.\n\n☐ 'Proprietary Rights’ which includes any and all rights, whether registered or unregistered, in and with respective to patents, copyrights, trade names, domain names, logos, trademarks, service marks, confidential information, know-how, trade secrets, moral rights, contract or licensing rights, whether protected under contract or otherwise under law, and other similar rights or interests in intellectual property.\n\n☐ 'Procedures and Specifications' which includes all procedures and other specifications, criteria, standards, methods, instructions, plans or other directions prescribed by Disclosing Party for the manufacture, preparation, packaging and labelling, and sale of its products or services.\n\n☐ 'Product Information' which includes Disclosing Party’s products which are being contemplated for sale, manufactured, marketed, listed, or sold, including any fixes, revisions, upgrades, or versions, of which consists of all data, software and documentation related thereto.\n\n☐ 'Service Information' which means the services provided by Disclosing Party, including the method, details, means, skills and training, which consists of all data, software and documentation related thereto.
    User: What is the format of a non-disclosure agreement?
    Bot: State of __________\n\nMUTUAL NON-DISCLOSURE AND CONFIDENTIALITY AGREEMENT\n\nThis Non-Disclosure and Confidentiality Agreement (this “Agreement”) is entered into as of the ____________________, 20______ (the “Effective Date”) by and between:\n\nDisclosing Party: ____________________________, as a(n) (Check one) ☐ Individual\n☐ Corporation ☐ Limited Liability Company ☐ Partnership ☐ Limited Partnership \n☐ Limited Liability Partnership (\"Disclosing Party\") and\n\nReceiving Party: ____________________________, as a(n) (Check one) ☐ Individual\n☐ Corporation ☐ Limited Liability Company ☐ Partnership ☐ Limited Partnership \n☐ Limited Liability Partnership (\"Receiving Party\")\n\nThe parties are exploring a potential business relationship relating to: _______________________\n__________________________________________________________________________________________________________________________________________________ (the “Transaction”).\n\nIn connection with the Transaction, each party, their respective affiliates and their respective directors, officers, employees, agents or advisors (collectively, “Representatives”) may provide or gain access to certain confidential and proprietary information. A party disclosing its Confidential Information to the other party is hereafter referred to as a “Disclosing Party.” A party receiving the Confidential Information of a Disclosing Party is hereafter referred to as a “Receiving Party.” In consideration of the mutual promises and covenants set forth in this Agreement, the parties hereby mutually agree as follows:\n\n1.Confidential Information. Confidential information is: (Check one)\n\n☐ All information shared by Disclosing Party. \"Confidential Information\" shall mean (i) all information relating to Disclosing Party’s products, business and operations including, but not limited to, financial documents and plans, customers, suppliers, manufacturing partners, marketing strategies, vendors, products, product development plans, technical product data, product samples, costs, sources, strategies, operations procedures, proprietary concepts, inventions, sales leads, sales data, customer lists, customer profiles, technical advice or knowledge, contractual agreements, price lists, supplier lists, sales estimates, product specifications, trade secrets, distribution methods, inventories, marketing strategies, source code, software, algorithms, data, drawings or schematics, blueprints, computer programs and systems and know-how or other intellectual property of Disclosing Party and its affiliates that may be at any time furnished, communicated or delivered by Disclosing Party to Receiving Party, whether in oral, tangible, electronic or other form; (ii) the terms, It is very important that you keep the exact same formatting as the training data examples of any agreement, including this Agreement, and the discussions, negotiations and proposals related to any agreement; (iii) information acquired during any tours of Disclosing Party’s facilities; and (iv) all other non-public information provided by Disclosing Party whosoever. All Confidential Information shall remain the property of Disclosing Party.\n\n☐ Only information marked ‘Confidential.’ \"Confidential Information,\" exchanged by the parties and entitled to protection hereunder, shall be identified or marked as such by an appropriate stamp or marking on each document exchanged designating the information as confidential or proprietary.\n\n☐ Specific information. The term “Confidential Information” as used in this Agreement shall mean any data or information that is competitively sensitive material and not generally known to the public, including, but not limited to, information relating to any of the following, which Disclosing Party considers confidential: (Check all that apply)\n\n☐ 'Accounting Information' which includes all books, tax returns, financial information, financial forecasts, pricing lists, purchasing lists and memos, pricing forecasts, purchase order information, supplier costs and discounts, or related financial or purchasing information.\n\n☐ 'Business Operations' which includes all processes, proprietary information or data, ideas or the like, either in existence or contemplated related to Disclosing Party’s daily and long-term plans for conducting Disclosing Party's business.\n\n☐ 'Computer Technology' which includes all computer hardware, software or other tangible and intangible equipment or code either in existence or development.\n\n☐ 'Customer Information' which includes the names of entities or individuals, including their affiliates and representatives, that Disclosing Party provides and sells its services or goods to, as well as any associated information, including but not limited to, leads, contact lists, sales plans and notes, shared and learned sales information such as pricing sheets, projections or plans, agreements, or such other data.\n\n☐ 'Intellectual Property' which includes patents, trademarks, service marks, logos, trade names, internet or website domain names, rights in designs and schematics, copyrights (including rights in computer software), moral rights, database rights, in each case whether registered or unregistered and including applications for registration, in all rights or forms anywhere in the world.\n\n☐ 'Marketing and Sales Information' which includes all customer leads, sales targets, sales markets, advertising materials, sales territories, sales goals and projections, sales and marketing processes or practices, training manuals or other documentation and materials related to the sales, marketing and promotional activities of the Disclosing Party and its products or services.\n\n☐ 'Proprietary Rights’ which includes any and all rights, whether registered or unregistered, in and with respective to patents, copyrights, trade names, domain names, logos, trademarks, service marks, confidential information, know-how, trade secrets, moral rights, contract or licensing rights, whether protected under contract or otherwise under law, and other similar rights or interests in intellectual property.\n\n☐ 'Procedures and Specifications' which includes all procedures and other specifications, criteria, standards, methods, instructions, plans or other directions prescribed by Disclosing Party for the manufacture, preparation, packaging and labelling, and sale of its products or services.\n\n☐ 'Product Information' which includes Disclosing Party’s products which are being contemplated for sale, manufactured, marketed, listed, or sold, including any fixes, revisions, upgrades, or versions, of which consists of all data, software and documentation related thereto.\n\n☐ 'Service Information' which means the services provided by Disclosing Party, including the method, details, means, skills and training, which consists of all data, software and documentation related thereto.
    """

    if "messages" not in session:
        session["messages"] = [
            {"role": "system", "content": "I am LawLiet, an AI Finetuned chatbot that answers questions related to legal documents. Please feel free to ask anything related to law! ☺️"}
        ]

    session["messages"].append({"role": "user", "content": user_prompt})

    try:
        response = openai.chat.completions.create(
            model=model_id,  # ← make sure it's not None!
            messages=session["messages"],
            max_tokens=5000,
            temperature=0.3,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )


        assistant_reply = response.choices[0].message.content.strip()
        session["messages"].append({"role": "assistant", "content": assistant_reply})
        session.modified = True
        return jsonify(text=assistant_reply)

    except Exception as e:
        print("Error:", e)
        return jsonify(error=str(e)), 400

@app.route("/api/evaluate", methods=["POST"])
def evaluate():
    data = request.get_json()
    predicted_response = data.get("predicted_response")
    ground_truth = data.get("ground_truth")

    if not all([predicted_response, ground_truth]):
        return jsonify(error="Missing required fields"), 400

    results = evaluator.evaluate_response(predicted_response, ground_truth)
    return jsonify(results)

@app.route("/", methods=["GET", "POST"])
def home():
    session.pop("messages", None)
    return app.send_static_file("index.html")

if __name__ == "__main__":
    app.run(port=5000, debug=True)
