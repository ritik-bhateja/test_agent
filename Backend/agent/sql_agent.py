import re
import logging
from strands import Agent
from strands.models import BedrockModel
from Backend.tools.athena_query import athena_query
from Backend.memory.memory_setup import client, memory_id
from Backend.memory.memory_hook import MemoryHookProvider
from Backend.agent.prompt import base_prompt, customer_schema_prompt, insurance_schema_prompt
import json

logger = logging.getLogger(__name__)

class SQLQueryExecutor:
    def __init__(self, actor_id='actor_123', session_id='session_123', region='ap-south-1', model_id='apac.anthropic.claude-sonnet-4-20250514-v1:0'):
        logger.info("🚀 Initializing SQLQueryExecutor...")
        logger.info(f"📍 Region: {region}, Model ID: {model_id}")

        try:
            self.model = BedrockModel(
                model_id=model_id,
                region_name=region
            )
            logger.info("✅ BedrockModel initialized successfully.")
        except Exception as e:
            logger.error("❌ Failed to initialize BedrockModel.", exc_info=True)
            raise e

        try:
            logger.info(f"🔑 Creating agent with actor_id={actor_id} and session_id={session_id}")
            # Put insurance instructions FIRST so agent sees them immediately
            system_prompt = f"""
                {base_prompt}
                {insurance_schema_prompt}
                {customer_schema_prompt}
            """
            agent_state = {"actor_id": actor_id, "session_id": session_id}
            logger.info(f"🔑 Agent state: {agent_state}")
            self.agent = Agent(
                model=self.model,
                system_prompt=system_prompt,
                tools=[athena_query],
                hooks=[MemoryHookProvider(client, memory_id)],
                state=agent_state
            )
            logger.info("✅ Agent created successfully with memory hooks and state.")
        except Exception as e:
            logger.error("❌ Failed to initialize Agent.", exc_info=True)
            raise e



    def execute_sql(self, user_query, user_id):
        logger.info(f"📝 User Query: {user_query}")
        
        user_prompt = f"User Request: {user_query}, user_id: {user_id}"

        try:
            logger.info("🔹 Invoking agent with prompt...")
            result = self.agent(user_prompt)
            logger.info(f"LLM RESULT : {result}")
            logger.info("✅ Agent invocation successful.")
        except Exception as e:
            logger.error("❌ Agent invocation failed!", exc_info=True)
            raise e

        logger.info("🔹 Extracting JSON from response...")
        result_str = str(result).strip()
        logger.info(f"Raw result length: {len(result_str)}")
        logger.info(f"Raw result (first 300 chars): {result_str[:300]}")
        
        # Find the first { and last } to extract JSON
        # This handles cases where there's text before or after the JSON
        first_brace = result_str.find('{')
        last_brace = result_str.rfind('}')
        
        # If no JSON found, agent returned plain text (e.g., asking for clarification)
        # Wrap it in proper JSON format
        if first_brace == -1 or last_brace == -1 or last_brace <= first_brace:
            logger.warning("⚠️ No JSON braces found in result - agent returned plain text")
            logger.info(f"Plain text response: {result_str}")
            
            # Wrap plain text in proper JSON format
            sql_dict = {
                "type": "text",
                "data": "",
                "explanation": result_str,
                "customer_specific": "False",
                "query_executed": ""
            }
            logger.info("✅ Wrapped plain text response in JSON format")
            logger.info(f"📊 Final SQL Dictionary: {sql_dict}")
            return sql_dict
        
        # Extract JSON content between braces
        content = result_str[first_brace:last_brace + 1]
        logger.info(f"Extracted JSON length: {len(content)}")
        logger.info(f"Extracted JSON (first 200 chars): {content[:200]}")
        logger.info("✅ JSON extraction successful.")

        try:
            logger.info("🔹 Parsing extracted JSON...")
            logger.info(f"Content to parse: {repr(content[:500])}")
            sql_dict = json.loads(content)
            logger.info("✅ JSON parsed successfully.")
            logger.info(f"📊 Final SQL Dictionary: {sql_dict}")
            return sql_dict
        except json.JSONDecodeError as e:
            logger.error("❌ JSON parsing failed!", exc_info=True)
            logger.error(f"Content that failed: {content}")
            logger.error(f"Content length: {len(content)}")
            
            # Fallback: wrap the content in proper JSON format
            logger.warning("⚠️ Falling back to wrapping content as plain text")
            sql_dict = {
                "type": "text",
                "data": "",
                "explanation": result_str,
                "customer_specific": "False",
                "query_executed": ""
            }
            logger.info(f"📊 Fallback SQL Dictionary: {sql_dict}")
            return sql_dict
        except Exception as e:
            logger.error("❌ Unexpected error while parsing JSON.", exc_info=True)
            raise e
