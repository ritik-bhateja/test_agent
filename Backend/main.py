from bedrock_agentcore.runtime import BedrockAgentCoreApp
from Backend.agent.sql_agent import SQLQueryExecutor
import logging
import json

logger = logging.getLogger(__name__)

app = BedrockAgentCoreApp()

@app.entrypoint
def main(payload, context = None):
    logger.info("🚀 Entrypoint triggered for Bedrock Agent Core App.")
    logger.info(f"📩 Incoming payload: {payload}")
    
    # Extract and validate user_id
    user_id = payload.get("user_id")
    if not user_id:
        logger.error("❌ Missing user_id in payload")
        return {
            "type": "text",
            "data": "",
            "explanation": "Error: user_id is required for memory isolation",
            "customer_specific": "False",
            "query_executed": ""
        }
    
    # Extract and validate session_id
    session_id = payload.get("session_id")
    if not session_id:
        logger.error("❌ Missing session_id in payload")
        return {
            "type": "text",
            "data": "",
            "explanation": "Error: session_id is required for memory isolation",
            "customer_specific": "False",
            "query_executed": ""
        }
    
    # Sanitize user_id for use as actor_id (AWS Bedrock Memory requirement)
    # actor_id must match pattern: [a-zA-Z0-9][a-zA-Z0-9-_/]*
    # Replace periods and other invalid characters with underscores
    actor_id = user_id.replace('.', '_').replace('@', '_at_').replace(' ', '_')
    
    logger.info(f"✅ Validated identifiers - user_id: {user_id}, actor_id: {actor_id}, session_id: {session_id}")
    
    # Initialize SQLQueryExecutor with dynamic identifiers
    generator = SQLQueryExecutor(actor_id=actor_id, session_id=session_id)
    try:
        
        result = generator.execute_sql(payload.get("user_query", ""), user_id)
        logger.info("✅ SQL execution completed successfully.")
        return result
    except Exception as e:
        logger.error("❌ Entrypoint execution failed!", exc_info=True)
        return {
                    "type": "text",
                    "data": "",
                    "explanation": f"Something went wrong while executing the query. Check the logs for more details. Error: {str(e)}",
                    "customer_specific": "False",
                    "query_executed": ""
                }

if __name__ == "__main__":
    app.run()