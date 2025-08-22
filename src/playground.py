from phi.agent import Agent, RunResponse
from phi.model.ollama import Ollama
from phi.tools.youtube_tools import YouTubeTools
from phi.playground import Playground, serve_playground_app

model=Ollama(model_name="llama3.1")


agent = Agent(
    model=model,
    tools=[YouTubeTools()],
    show_tool_calls=True,
    description="You are a YouTube agent. Obtain the captions of a YouTube video and answer questions.",
)

app = Playground(agents=[agent]).get_app()

if __name__ == "__main__":
    serve_playground_app("playground:app", reload=True)
