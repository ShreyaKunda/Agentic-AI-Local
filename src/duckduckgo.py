from phi.agent import Agent, RunResponse
from phi.model.ollama import Ollama
from phi.tools.duckduckgo import DuckDuckGo
model=Ollama(model_name="llama3.1")

agent = Agent(model=model,tools=[DuckDuckGo()], show_tool_calls=True,description="You are a Web Search agent. Answer questions in a detailed and an extensive structured manner using bullet points and proper paragraphs after searching from the web. Also provide relavant links at the end for additional information.",)
question=input("What do you want to search about?:")
agent.print_response(f"Search the web for {question}", markdown=True)
