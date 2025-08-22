from phi.agent import Agent, RunResponse
from phi.model.ollama import Ollama
from phi.tools.wikipedia import WikipediaTools
model=Ollama(model_name="llama3.1")

agent = Agent(model=model,tools=[WikipediaTools()], show_tool_calls=True,description="You are a Wikipedia agent. Obtain the required information from Wikipedia pages and answer questions in a detailed structured manner using bullet points and proper paragraphs. Incase there is a spelling mistake in the question, try to find the most related answer to it from Wikipedia. Also provide relavant links and related reading materials at the end for additional information.",)
question=input("What do you want to search about?:")
agent.print_response(f"Search for {question}", markdown=True)
