import pandas as pd
from phi.agent import Agent
from phi.model.ollama import Ollama
from phi.tools.website import WebsiteTools
 
# Initialize the model
model = Ollama(model_name="llama3.1")
 
# Agent 1: Generates a summary from raw CSV data
summary_agent = Agent(
    model=model,
    description="Agent that summarizes raw cybersecurity data into a human-readable summary.",
    instructions=[
        "Analyze the raw cybersecurity data and generate a concise, human-readable summary.",
        "Ensure the summary includes key details about the attack type, impact, and affected systems.",
    ],
)
 
def process_csv(file_path):
    """Reads the CSV file and generates a summary using Agent 1."""
    try:
        df = pd.read_csv(file_path)
        raw_data = df.to_string()  # Convert entire dataframe to a string for summarization
        response = summary_agent.run(f"Summarize the following raw cybersecurity data: {raw_data}")
        summary = response.content if response else None
        return summary
    except Exception as e:
        print(f"Error processing CSV file: {e}")
        return None
 
# Agent 2: Finds solutions and mitigations, including website content retrieval
cyber_agent = Agent(
    model=model,
    tools=[WebsiteTools()],
    description="Agent that finds solutions and mitigations for cybersecurity threats.",
    instructions=[
        "Given a summary of a cyber attack, search for solutions and mitigations available for those weaknesses and vulnerabilities.",
        "Retrieve and analyze content from the LWN.net Security page for relevant information.",
        "Return a list of solutions and mitigations that the user can apply to tackle the weakness and vulnerability.",
    ],
)
 
# Get user input for CSV file path
csv_file_path = "C:/Users/H594278/Downloads/Shreya/Experimentation/Threat_Intelligence_Caldera/Logs_and_Files/TTPS.csv"
threat_summary = process_csv(csv_file_path)
 
if threat_summary:
    print("\nGenerated Threat Summary:")
    print(threat_summary)
    # Get mitigations and solutions
    response = cyber_agent.run(f"Mitigations and solutions for {threat_summary}")
    if response:
        print("\nMitigations and Solutions:")
        print(response.content)