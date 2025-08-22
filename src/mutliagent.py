from phi.agent import Agent, RunResponse
from phi.model.ollama import Ollama
from phi.tools.wikipedia import WikipediaTools
from phi.tools.arxiv_toolkit import ArxivToolkit
from phi.tools.duckduckgo import DuckDuckGo

# Initialize the AI model
model = Ollama(id="llama3.1")

# Define specialized agents
search_agent = Agent(
    model=model,
    tools=[WikipediaTools(), ArxivToolkit(), DuckDuckGo(),],
    show_tool_calls=True,
    markdown=True
)

summarization_agent = Agent(
    model=model,
    markdown=True
)

fact_verification_agent = Agent(
    model=model,
    markdown=True
)

bias_detection_agent = Agent(
    model=model,
    markdown=True
)

citation_tracking_agent = Agent(
    model=model,
    markdown=True
)

argument_comparison_agent = Agent(
    model=model,
    markdown=True
)

qa_agent = Agent(
    model=model,
    markdown=True
)

def phd_research_assistant(query):
    """
    Multi-Agent PhD Research Assistant that:
    1. Searches multiple academic sources.
    2. Summarizes key findings.
    3. Verifies credibility of sources.
    4. Flags potential biases.
    5. Tracks citations and key research papers.
    6. Compares contrasting arguments on the topic.
    7. Provides an interactive Q&A system.
    """
    print(f"\n🔍 Searching for: {query}\n")
    
    # Step 1: Retrieve Initial Research Results
    raw_results = search_agent.run(f"Find top academic papers, Wikipedia summaries, and articles related to '{query}'. Provide structured insights.")

    # Step 2: Summarize Key Findings
    summary = summarization_agent.run(f"Summarize the key research insights from: {raw_results}")

    # Step 3: Verify Facts
    fact_check = fact_verification_agent.run(f"Cross-check the following claims from {summary} against reliable sources.")

    # Step 4: Bias Detection
    bias_analysis = bias_detection_agent.run(f"Analyze potential biases in {summary}. Flag any concerns.")

    # Step 5: Citation Tracking
    citations = citation_tracking_agent.run(f"Extract key research papers, authors, and publication years related to '{query}'.")

    # Step 6: Argument Comparison
    argument_comparison = argument_comparison_agent.run(f"Compare contrasting arguments and perspectives on '{query}'. Summarize opposing viewpoints.")

    # Step 7: Interactive Q&A
    user_question = input("Do you have any follow-up questions? (Type your question or 'no' to exit): ")
    while user_question.lower() != 'no':
        answer = qa_agent.run(f"Answer the following question based on previous research findings: {user_question}")
        print(f"\n🤖 AI Research Assistant: {answer}\n")
        user_question = input("Any more questions? (Type your question or 'no' to exit): ")

    # Format the final structured output
    final_output = f"""
    📝 **Research Summary for:** {query}

    📌 **Key Findings:**  
    {summary}

    ✅ **Fact Verification:**  
    {fact_check}

    ⚠ **Bias Analysis:**  
    {bias_analysis}

    🔗 **Citations & References:**  
    {citations}

    ⚖ **Argument Comparison:**  
    {argument_comparison}

    🎤 **Q&A Session Completed**
    """

    return final_output

# Example Research Query
query="Common Vunerabilities and Exposures"
output = phd_research_assistant(query)
print(output)
