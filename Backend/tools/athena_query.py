import boto3
import time
from typing import Any, Dict, List, Union
from strands import tool

@tool(
    name="athena_query",
    description="""Execute SQL queries on AWS Athena databases.

CRITICAL: You MUST specify the correct database parameter:
- For insurance queries (policy, claim, premium, coverage) → database="insurance_db"
- For banking queries (customer, account, loan, card) → database="sentra_db"

The insurance_db database EXISTS and contains INSURANCE_POLICIES and INSURANCE_CLAIMS tables with real data.
DO NOT default to sentra_db for insurance queries!""",
    inputSchema={
        "type": "object",
        "properties": {
            "sql": {
                "type": "string", 
                "description": "The SQL query to execute"
            },
            "database": {
                "type": "string", 
                "description": "REQUIRED: Database name. Use 'insurance_db' for insurance queries, 'sentra_db' for banking queries.",
                "enum": ["sentra_db", "insurance_db"]
            },
            "workgroup": {"type": "string"},
            "output_s3": {"type": "string"}
        },
        "required": ["sql", "database"]
    }
)
def athena_query(sql: str, database: str = "sentra_db") -> Union[str, List[Dict[str, Any]]]:
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"🔍 ATHENA QUERY TOOL CALLED")
    logger.info(f"   Database: {database}")
    logger.info(f"   SQL: {sql}")
    
    client = boto3.client("athena")
    workgroup = "primary"
    output_s3 = "s3://bedrock-agentcore-runtime-628897991744-ap-south-1-3m5mgapsu7/TestQueryOutput/"

    result_conf = {}
    if output_s3:
        result_conf["OutputLocation"] = output_s3

    try:
        resp = client.start_query_execution(
            QueryString=sql,
            QueryExecutionContext={
                'Database': database
            },
            WorkGroup=workgroup,
            ResultConfiguration=result_conf if result_conf else None
        )
        query_id = resp["QueryExecutionId"]
        logger.info(f"   Query ID: {query_id}")

        while True:
            status = client.get_query_execution(QueryExecutionId=query_id)
            state = status["QueryExecution"]["Status"]["State"]
            if state in ("SUCCEEDED", "FAILED", "CANCELLED"):
                break
            time.sleep(1)

        if state != "SUCCEEDED":
            error_msg = f"Athena query failed: {state}"
            logger.error(f"   ❌ {error_msg}")
            if state == "FAILED":
                reason = status["QueryExecution"]["Status"].get("StateChangeReason", "Unknown")
                error_msg += f" - Reason: {reason}"
                logger.error(f"   Failure reason: {reason}")
            return error_msg

        res = client.get_query_results(QueryExecutionId=query_id)
        rows = res["ResultSet"]["Rows"]
        
        if len(rows) == 0:
            logger.warning(f"   ⚠️ Query returned 0 rows (no data)")
            return []
        
        headers = [col["VarCharValue"] for col in rows[0]["Data"]]
        logger.info(f"   Columns: {headers}")

        data: List[Dict[str, Any]] = []
        for row in rows[1:]:
            values = [col.get("VarCharValue") for col in row["Data"]]
            row_dict = dict(zip(headers, values))
            data.append(row_dict)

        logger.info(f"   ✅ Query succeeded - returned {len(data)} rows")
        if len(data) > 0:
            logger.info(f"   Sample row: {data[0]}")
        
        return data

    except Exception as e:
        error_msg = f"Error executing Athena query: {str(e)}"
        logger.error(f"   ❌ {error_msg}")
        return error_msg
