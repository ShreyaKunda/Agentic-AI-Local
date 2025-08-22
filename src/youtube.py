from phi.agent import Agent, RunResponse
from phi.model.ollama import Ollama
from phi.tools.youtube_tools import YouTubeTools

model=Ollama(model_name="llama3.1")


agent = Agent(
    model=model,
    tools=[YouTubeTools()],
    show_tool_calls=True,
    description="You are a YouTube agent. Obtain the YouTube video and answer questions in a very very detailed and an extensive structured manner using bullet points and proper paragraphs. Provide correct and factual data from the video but don't make up information that does not exist and dont hallucinate. Structure the answer in a nice and an understandable way in parts and paragraphs.",
)
video_url=input("Please provide the youtube link for summarization:")
response= agent.print_response(f"Summarize this video {video_url}", markdown=True)
print(response)
