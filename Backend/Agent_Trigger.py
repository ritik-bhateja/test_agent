from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import json
import time
import botocore

app = Flask(__name__)

def parse_athena_results(result_set):
    headers = [col.get("VarCharValue", "") for col in result_set["Rows"][0]["Data"]]
    rows = []

    for row in result_set["Rows"][1:]:
        data = [col.get("VarCharValue", None) for col in row["Data"]]

        # Fix misaligned rows by padding
        if len(data) < len(headers):
            data += [None] * (len(headers) - len(data))

        row_dict = dict(zip(headers, data))

        # Filter out rows where CIF_NO starts with "CIF"
        cif_value = row_dict.get("CIF_NO", "")
        if not str(cif_value).startswith("CIF"):
            continue  # ye row fake lag rahi hai, skip it

        rows.append(row_dict)

    return rows


# Allow ALL domains
CORS(app, resources={r"/*": {"origins": "*"}})

# --------------------------------------------
#  EXISTING ENDPOINT — BEDROCK AGENTCORE
# --------------------------------------------
@app.route("/query", methods=["POST"])
def send_to_bknd():
    config = botocore.config.Config(
    read_timeout=180,
    connect_timeout=10,
    retries={'max_attempts': 0}
    )

    payload = request.get_json()
    print(payload)
    
    # Validate user_id presence
    if not payload.get("user_id"):
        return jsonify({
            "error": "missing_actor_id",
            "message": "user_id is required"
        }), 400
    
    # Validate session_id presence
    if not payload.get("session_id"):
        return jsonify({
            "error": "missing_session_id",
            "message": "session_id is required"
        }), 400
    
    client = boto3.client('bedrock-agentcore', region_name='ap-south-1', config=config)
    session_id = payload.get("session_id", "")
    
    bknd_payload = json.dumps({
        "user_query": payload.get("user_query", ""),
        "user_id": payload.get("user_id", ""),
        "session_id": session_id
    })

    # Use session_id as runtimeSessionId for proper session isolation
    # Frontend generates 33-character session IDs to meet AWS Bedrock requirement
    response = client.invoke_agent_runtime(
        agentRuntimeArn='arn:aws:bedrock-agentcore:ap-south-1:628897991744:runtime/Test_Agent-LNZiEg4CnQ',
        runtimeSessionId=session_id,
        payload=bknd_payload,
        qualifier="DEFAULT"
    )
    response_body = response['response'].read()
    response_data = json.loads(response_body)
    print("Agent Response:", response_data)
    return jsonify(response_data)


# --------------------------------------------
#  NEW ENDPOINT — ATHENA QUERY
# --------------------------------------------
@app.route("/users", methods=["POST"])
def get_users():
    payload = request.get_json()
    print(payload)
    user_id = payload.get("user_id", "")
    query = "SELECT CIF_NO,CUSTOMER_NAME,MOBILE_PHONE,EMAIL_ADDRESS FROM dm_customer_master;"

    if not query:
        return jsonify({"error": "Query parameter missing"}), 400

    # Athena connection
    session = boto3.Session(region_name="ap-south-1")
    athena = session.client("athena")

    DATABASE = "sentra_db"
    OUTPUT = "s3://bedrock-agentcore-runtime-628897991744-ap-south-1-3m5mgapsu7/TestQueryOutput/"

    # Start query execution
    resp = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={"Database": DATABASE},
        ResultConfiguration={"OutputLocation": OUTPUT}
    )
    exec_id = resp["QueryExecutionId"]

    # Poll until query finishes
    while True:
        status = athena.get_query_execution(QueryExecutionId=exec_id)
        state = status["QueryExecution"]["Status"]["State"]

        if state in ("SUCCEEDED", "FAILED", "CANCELLED"):
            break

        time.sleep(1)

    if state != "SUCCEEDED":
        return jsonify({
            "status": "error",
            "execution_id": exec_id,
            "state": state
        })

    # Fetch results
    results = athena.get_query_results(QueryExecutionId=exec_id)
    clean_rows = parse_athena_results(results["ResultSet"])

    if user_id == 'kamaljeet.singh':
        final_rows = clean_rows
    elif user_id == 'vishal.saxena':
        final_rows = clean_rows[:26]
    else:
        final_rows = clean_rows[26:100]
        

    return jsonify({
        "status": "ok",
        "execution_id": exec_id,
        "rows": final_rows
    })


# --------------------------------------------
#  RUN
# --------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
