import os
from typing import List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from dotenv import load_dotenv

load_dotenv()

# Allowed values
ALLOWED_BRANCHES = [
    "CSE", "IT", "ECE", "EE", "ME", "ICE", "BT", "CHE", 
    "CIVIL", "ARCH", "DESIGN", "MANAGEMENT", "PHYSICS", 
    "CHEMISTRY", "MATHEMATICS", "ALL"
]

ALLOWED_YEARS = [
    "1", "2", "3", "4", "PG", "PHD", "ALL"
]

class TaggingSchema(BaseModel):
    branches: List[str] = Field(description="List of applicable branches extracted from the text.")
    years: List[str] = Field(description="List of applicable years/semesters mapped to years extracted from the text.")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def extract_tags(text: str):
    """
    Extracts structured tags (Branches, Years) from text using LangChain + OpenRouter.
    """
    if not text or len(text.strip()) < 20:
        return {"branches": [], "years": []}

    try:
        # Configure ChatOpenAI with OpenRouter base URL
        llm = ChatOpenAI(
            openai_api_key=OPENROUTER_API_KEY,
            openai_api_base="https://openrouter.ai/api/v1",
            model_name="nvidia/nemotron-nano-12b-v2-vl:free",
        )

        parser = PydanticOutputParser(pydantic_object=TaggingSchema)

        prompt = PromptTemplate(
            template="""
            You are an expert academic administrative assistant for NSUT (Netaji Subhas University of Technology).
            Your task is to ACCURATELY identify the target audience for the given notice.

            ### Allowed Tags Config
            Allowed Branches: {allowed_branches}
            Allowed Years: {allowed_years}

            ### MAPPING RULES (Strictly Follow These)
            1. **Semester to Year Mapping**:
               - 1st & 2nd Sem -> "1"
               - 3rd & 4th Sem -> "2"
               - 5th & 6th Sem -> "3"
               - 7th & 8th Sem -> "4"
            
            2. **Branch Mapping**:
               - CSAI, CSDA, MAC, SE -> Map to "CSE" or "IT" if unsure, or keep as is if in allowed list. (Note: MAC is Mathematics).
               - "B.Tech" (without specific branch) -> Implies ["CSE", "IT", "ECE", "EE", "ME", "ICE", "BT", "CHE", "CIVIL"] (Use "ALL" if it applies to everyone).
               - "MPAE" -> "ME"
            
            3. **Contextual Inferences**:
               - "Orientation" -> "1" (1st Year)
               - "Placement" / "Internship" -> Usually "3", "4" (unless specified).
               - "Degree Distribution" / "Convocation" -> "4" or recently graduated (map to 4).
               - "Scholarship" -> Usually "ALL" unless specified.
               - "Holiday" / "Date Sheet" -> "ALL".

            ### INSTRUCTIONS
            - Analyze the text carefully. Look for keywords like "Final Year", "Pre-final Year", specific semesters, or branch codes.
            - If the notice says "All Students" or "General Notice", user "ALL" for both lists.
            - Be specific but inclusive.
            - OUTPUT MUST BE VALID JSON.

            ### Notice Text:
            {text}

            {format_instructions}
            """,
            input_variables=["text"],
            partial_variables={
                "allowed_branches": str(ALLOWED_BRANCHES),
                "allowed_years": str(ALLOWED_YEARS),
                "format_instructions": parser.get_format_instructions()
            }
        )

        chain = prompt | llm | parser

        # Truncate text for safety
        safe_text = text[:8000] 

        output = chain.invoke({"text": safe_text})
        
        # Filter output to ensure strict compliance (in case LLM hallucinates extra tags)
        valid_branches = [b for b in output.branches if b in ALLOWED_BRANCHES]
        valid_years = [y for y in output.years if y in ALLOWED_YEARS]

        return {"branches": valid_branches, "years": valid_years}

    except Exception as e:
        print(f"Error extracting tags: {e}")
        return {"branches": [], "years": []}
