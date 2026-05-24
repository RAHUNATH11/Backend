# from supabase import create_client

# url = "https://jfimfufzlpljtujtrbpq.supabase.co"
# key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpmaW1mdWZ6bHBsanR1anRyYnBxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3OTQ0NTI4OCwiZXhwIjoyMDk1MDIxMjg4fQ.gotvAAeSfsBm4oh1l7h4asnGHSkfr2WrNlfRkruAcD0"
from flask import Flask, jsonify, request
from flask_cors import CORS
from supabase import create_client
import os
from AskCipher import get_cipher_response

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
app = Flask(__name__)
CORS(app)

# ==============================
# SUPABASE CONFIG
# ==============================
#
# url = "https://jfimfufzlpljtujtrbpq.supabase.co"
# #key = "YOUR_SUPABASE_KEY"
# key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpmaW1mdWZ6bHBsanR1anRyYnBxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3OTQ0NTI4OCwiZXhwIjoyMDk1MDIxMjg4fQ.gotvAAeSfsBm4oh1l7h4asnGHSkfr2WrNlfRkruAcD0"

supabase = create_client(url, key)

# ==============================
# GET TICKETS + FILTERS + ANALYTICS
# ==============================

@app.route('/api/users', methods=['GET'])
def get_users():

    # ==============================
    # GET FILTER VALUES
    # ==============================

    status_filters = request.args.getlist('status[]')
    priority_filters = request.args.getlist('priority[]')
    assignee_filters = request.args.getlist('assignee[]')

    # ==============================
    # BASE QUERY
    # ==============================

    query = supabase.table("dev_updates").select("*")

    # ==============================
    # APPLY STATUS FILTER
    # ==============================

    if status_filters:
        query = query.in_("Status", status_filters)

    # ==============================
    # APPLY PRIORITY FILTER
    # ==============================

    if priority_filters:
        query = query.in_("Priority", priority_filters)

    # ==============================
    # APPLY ASSIGNEE FILTER
    # ==============================
    response = query.execute()
    print("Rows returned:", len(response.data))
    print("First row keys:", response.data[0].keys() if response.data else "No data")
    if assignee_filters:
        query = query.in_("Assignee", assignee_filters)

    # ==============================
    # EXECUTE QUERY
    # ==============================

    response = query.execute()

    tickets = response.data

    # ==============================
    # ANALYTICS
    # ==============================

    active_statuses = [
        "In Progress",
        "Test",
        "On Hold"
    ]

    active_count = len([
        t for t in tickets
        if t.get("Status") in active_statuses
    ])

    deploy_count = len([
        t for t in tickets
        if t.get("Status") == "Ready to Deploy"
    ])

    done_count = len([
        t for t in tickets
        if t.get("Status") == "Done"
    ])

    critical_count = len([
        t for t in tickets
        if t.get("Priority") in ["High", "Highest"]
    ])

    analytics = {
        "active": active_count,
        "readyToDeploy": deploy_count,
        "done": done_count,
        "critical": critical_count
    }

    # ==============================
    # RESPONSE
    # ==============================

    return jsonify({
        "tickets": tickets,
        "analytics": analytics
    })

@app.route('/api/datewise', methods=['GET'])
def get_datewise():
    try:
        response = supabase.table("date_wise").select("*").execute()
        data = response.data
        # Sort by date ascending
        data.sort(key=lambda x: x.get('date', ''))
        return jsonify(data)
    except Exception as e:
        print("Error fetching datewise:", e)
        return jsonify([]), 500



# ==============================
# ASK CIPHER - CHAT ENDPOINT
# ==============================

# @app.route('/api/chat', methods=['POST'])
# def chat():
#     data = request.json
#     question = data.get("question", "")
#     history = data.get("history", [])

#     if not question:
#         return jsonify({"error": "No question provided"}), 400

#     answer = get_cipher_response(question, history)
#     return jsonify({"answer": answer})

@app.route('/api/chat', methods=['POST'])
def chat():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "error": "No JSON received"
            }), 400

        question = data.get("question", "")

        if not question:
            return jsonify({
                "error": "No question provided"
            }), 400

        history = data.get("history", [])

        response = get_cipher_response(
            question,
            history
        )

        return jsonify({
            "response": response
        })

    except Exception as e:

        print("CHAT ERROR:", str(e))

        return jsonify({
            "error": str(e)
        }), 500

# ==============================
# MAIN
# ==============================

# if __name__ == '__main__':
#     app.run(debug=True)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
