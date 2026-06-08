import os
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from app.config.settings import settings

# Initialize LLM
llm = ChatOpenAI(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY)

# Tool for Tavily search (mocked or actual)
from app.services.tavily_service import tavily_service

class SearchTool:
    def __init__(self):
        self.name = "Web Search Tool"
        self.description = "Searches the web for information."

    def func(self, query: str):
        return str(tavily_service.search_web(query, max_results=5))

search_tool = SearchTool()

def get_research_agent():
    return Agent(
        role='Senior Research Analyst',
        goal='Search the web, collect sources, and extract relevant content about a given topic.',
        backstory='You are an expert researcher capable of finding high-quality information across the web.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

def get_analysis_agent():
    return Agent(
        role='Data Insights Analyst',
        goal='Analyze research findings, identify key trends, and detect patterns.',
        backstory='You excel at finding the hidden meaning in large amounts of research data.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

def get_verification_agent():
    return Agent(
        role='Fact Checker & Validator',
        goal='Validate claims, check source quality, and calculate confidence scores.',
        backstory='You are meticulous and do not take any claim at face value without strong evidence.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

def get_report_agent():
    return Agent(
        role='Executive Report Writer',
        goal='Generate executive summaries and create actionable recommendations.',
        backstory='You summarize complex findings into clear, concise, and actionable business reports.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

def get_visualization_agent():
    return Agent(
        role='Data Visualizer',
        goal='Produce structured chart data, timeline data, and knowledge graph structures.',
        backstory='You turn textual insights into structured JSON formats ready for visual rendering.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

def get_assistant_agent():
    return Agent(
        role='Project Assistant',
        goal='Answer user questions accurately using project context.',
        backstory='You are a helpful AI assistant that understands the context of the user’s project deeply.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
