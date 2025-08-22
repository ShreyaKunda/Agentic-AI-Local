from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
import chainlit as cl
import os

# ------------------- Authentication -------------------
@cl.password_auth_callback
def auth_callback(username: str, password: str):
    if (username, password) == ("admin", "admin"):
        return cl.User(identifier="admin", metadata={"role": "admin", "provider": "credentials"})
    else:
        return None

# ------------------- Neo4j Graph Setup -------------------
try:
    graph = Neo4jGraph(
        url="bolt://localhost:7687",  # Use "neo4j+s://" for Neo4j AuraDB
        username="neo4j",
        password="Password1"  # Replace with your actual password
    )
    print("Connected to Neo4j successfully!")
except Exception as e:
    print(f"Failed to connect to Neo4j: {e}")

# ------------------- Helper Functions for Query History -------------------
def update_query_history(user_id: str, query_text: str):
    cypher = """
    MERGE (u:User {id: $user_id})
    MERGE (q:Query {text: $query_text})
    MERGE (u)-[r:ASKED]->(q)
    ON CREATE SET r.count = 1
    ON MATCH SET r.count = r.count + 1
    """
    params = {"user_id": user_id, "query_text": query_text}
    graph.query(cypher, params)

def get_top_queries(user_id: str, limit: int = 3):
    cypher = """
    MATCH (u:User {id: $user_id})-[r:ASKED]->(q:Query)
    RETURN q.text as query, r.count as count
    ORDER BY r.count DESC
    LIMIT $limit
    """
    params = {"user_id": user_id, "limit": limit}
    result = graph.query(cypher, params)
    top_queries = [row["query"] for row in result]
    return top_queries

def store_feedback(user_id: str, query_text: str, rating: str):
    cypher = """
    MERGE (u:User {id: $user_id})
    MERGE (q:Query {text: $query_text})
    MERGE (u)-[r:FEEDBACK]->(q)
    SET r.rating = $rating
    """
    params = {"user_id": user_id, "query_text": query_text, "rating": rating}
    graph.query(cypher, params)

# ------------------- Recommendation Panel Function -------------------
async def show_recommendations(user_id: str, chain, memory):
    """Fetch top queries from Neo4j and display them as buttons.
    If a recommendation is chosen, process it and then re-display the panel."""
    top_queries = get_top_queries(user_id, limit=3)
    if top_queries:
        actions = [cl.Action(name="recommend", payload={"query": q}, label=q) for q in top_queries]
        actions.append(cl.Action(name="continue_chat", payload={"action": "continue"}, label="Continue to chat"))
        res_action = await cl.AskActionMessage(
            content="",
            actions=actions
        ).send()
        
        if res_action:
            payload = res_action.get("payload", {})
            if payload.get("action") == "continue":
                await cl.Message(content="Please ask your question").send()
            elif payload.get("query"):
                recommended_query = payload.get("query")
                rec_thinking = await cl.Message(content="Processing...").send()
                rec_response = await chain.ainvoke({"query": recommended_query})
                rec_generated_query = rec_response.get("intermediate_steps", ["No query generated"])[0]
                rec_final_answer = rec_response.get("result", "I don't know the answer.")
                memory.save_context({"query": recommended_query}, {"response": rec_final_answer})
                
                await cl.Message(
                    content=f"**Generated Cypher Query:**\n```\n{rec_generated_query}\n```\n\n**Answer:**\n{rec_final_answer}"
                ).send()
                # After processing, show the recommendations again.
                await show_recommendations(user_id, chain, memory)
    else:
        await cl.Message(content="No frequent queries found. Please ask your question!").send()

# ------------------- Chat Initialization -------------------
@cl.on_chat_start
async def on_chat_start():
    """Directly initialize Graph QA mode, display a welcome message and recommendation panel."""
    
    model = Ollama(model="llama3.1")  # Load the LLM model
    memory = ConversationBufferMemory(memory_key="chat_history")
    cl.user_session.set("memory", memory)
    
    # Set up Graph QA chain.
    graph_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an AI that can answer questions using a Neo4j knowledge graph. You generate Cypher queries and return accurate answers. You're a very knowledgeable Cypher query generator. Your task is to provide users with a correct and precise Cypher query along with the response. If anything else is asked, tell the user that it is beyond your ability. Please try to read the question of the user properly and find out keywords from the user and then try to generate the right query since you have the access to the Neo4j Database. The user may misspell a few words so try to find the most similar word to the word and give the answer with respect to the database."),
        ("human", "{query}")
    ])
    graph_qa_chain = GraphCypherQAChain.from_llm(
        llm=model, graph=graph, prompt=graph_prompt,
        return_intermediate_steps=True, allow_dangerous_requests=True
    )
    cl.user_session.set("runnable", graph_qa_chain)
    
    # For this example, we assume the logged-in user is admin.
    user_id = "admin"
    welcome_text = "Welcome back! You're in Graph QA Mode! Select one of your frequent queries to ask, or choose 'Continue to chat' to proceed!\n\n"
    top_queries = get_top_queries(user_id, limit=3)
    if top_queries:
        welcome_text += ("")
    else:
        welcome_text += "No previous queries found. Please ask your question below."
    await cl.Message(content=welcome_text).send()
    
    # Show recommendations on startup.
    await show_recommendations(user_id, graph_qa_chain, memory)

# ------------------- Message Handling -------------------
@cl.on_message
async def on_message(message: cl.Message):
    """Process user messages, update persistent history, and provide optional feedback and recommendation panel."""
    
    chain = cl.user_session.get("runnable")
    memory = cl.user_session.get("memory")
    
    # For this example, assume user is admin.
    user_id = "admin"
    query_text = message.content

    update_query_history(user_id, query_text)
    
    if not chain:
        await cl.Message(content="Graph QA is not initialized. Please restart the chat.").send()
        return
    
    try:
        thinking_msg = await cl.Message(content="Processing...").send()
        response = await chain.ainvoke({"query": query_text})
        generated_query = response.get("intermediate_steps", ["No query generated"])[0]
        final_answer = response.get("result", "I don't know the answer.")
        memory.save_context({"query": query_text}, {"response": final_answer})
        
        if generated_query== "No query generated":
            await cl.Message(
                content=f"**Answer:**\n{final_answer}"
            ).send()
        else:
            await cl.Message(
                    content=f"**Generated Cypher Query:**\n```\n{generated_query}\n```\n\n**Answer:**\n{final_answer}"
                ).send()
        
        
        
        # Show recommendations again after processing the user query.
        await show_recommendations(user_id, chain, memory)
    
    except Exception as e:
        await cl.Message(content=f"Error: {str(e)}").send()
        print(f"Error processing query: {str(e)}")
