import os
from typing import Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from database import get_notice_by_id, get_chat_history, save_chat_message
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

SYSTEM_PROMPT = """You are an intelligent assistant for university students.
Your goal is to answer questions about a specific notice while being helpful and informative.

You will be provided with:
- The notice text (Primary source)
- The student's branch and year

Your responsibilities:
1. Prioritize the information in the notice.
2. You MAY use your general knowledge to explain terms, provide context, or offer standard university guidance if it helps the student understand the notice better.
3. If the specific answer is not in the notice, you can say so, but try to offer related helpful information or general advice if applicable (e.g., "The notice doesn't specify the time, but usually these events happen around..."). Be sure to clarify what is from the notice vs. general knowledge.

Personalization:
- Acknowledge the student's branch/year if relevant (e.g., "As a CSE student, this is important for you...").
- Be friendly and professional.

- Helpful, clear, and encouraging.

About You:
- Your name is "Dastabbej".
- Your task is simplifying notices for students.
- You were created by "Aryan Anand", a 2nd year B.Tech student from the CSAI branch.
- IMPORTANT: Only mention your name or creator if the user explicitly asks about them or about you. Otherwise, focus solely on the notices."""


def assemble_context(notice: Dict, user_branch: str, user_year: str) -> str:
    """
    Assembles the notice context for the LLM.
    """
    if not notice:
        return "Notice not found."
    
    context_parts = []
    context_parts.append(f"Student Information: Branch={user_branch}, Year={user_year}\n")
    context_parts.append("=== NOTICE ===\n")
    context_parts.append(f"Title: {notice['title']}")
    context_parts.append(f"Date: {notice.get('date', 'N/A')}")
    
    if notice.get('summary'):
        context_parts.append(f"\nSummary: {notice['summary']}")
    
    if notice.get('extracted_text'):
        context_parts.append(f"\nFull Text:\n{notice['extracted_text']}")
    
    context_parts.append("\n---")
    
    return "\n".join(context_parts)


def generate_chat_response(
    query: str,
    user_id: str,
    notice_id: str,
    user_branch: str,
    user_year: str
) -> str:
    """
    Generates a chat response for a specific notice using Google's Gemma 27b model.
    
    Args:
        query: User's question
        user_id: User identifier
        notice_id: Notice ID to discuss
        user_branch: User's branch (e.g., "CSE")
        user_year: User's year (e.g., "3")
    
    Returns:
        LLM response string
    """
    try:
        # 1. Retrieve the specific notice
        notice = get_notice_by_id(notice_id)
        if not notice:
            return "Sorry, I couldn't find that notice. Please select a valid notice."
        
        # 2. Assemble context
        notice_context = assemble_context(notice, user_branch, user_year)
        
        # 3. Retrieve chat history for this user and notice
        history = get_chat_history(user_id, notice_id, limit=10)
        
        # 4. Configure LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=GOOGLE_API_KEY,
            temperature=0.5,
            convert_system_message_to_human=True # Gemma via API might benefit from this, though newer models handle system prompts. Keeping it safe or default.
        )
        
        # 5. Build message chain
        # Manually handle system prompt since the model doesn't support developer instructions
        initial_instruction = f"{SYSTEM_PROMPT}\n\n{notice_context}"
        
        messages = []
        
        # Add chat history
        # If history exists, we prepend instruction to the first message or just add it as a separate first message
        if history:
             # Add instructions as the very first message
             messages.append(HumanMessage(content=initial_instruction))
             # Then append history
             for msg in history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))
             # Append current query
             messages.append(HumanMessage(content=query))
        else:
            # No history, just instructions + query combined or separate
            # Combining is usually safer for "context"
            messages.append(HumanMessage(content=f"{initial_instruction}\n\nUser Question: {query}"))
        
        # 6. Get response
        response = llm.invoke(messages)
        response_text = response.content
        
        # 7. Save to chat history
        save_chat_message(user_id, notice_id, "user", query, user_branch, user_year)
        save_chat_message(user_id, notice_id, "assistant", response_text, user_branch, user_year)
        
        return response_text
        
    except Exception as e:
        error_msg = f"Error generating response: {str(e)}"
        print(error_msg)
        return "I apologize, but I encountered an error processing your request. Please try again."


def generate_streaming_chat_response(
    query: str,
    user_id: str,
    notice_id: str,
    user_branch: str,
    user_year: str
):
    """
    Generates a STREAMING chat response.
    Yields chunks of text.
    Saves full conversation to DB at the end.
    """
    try:
        # 1. Retrieve the specific notice
        notice = get_notice_by_id(notice_id)
        if not notice:
            yield "Sorry, I couldn't find that notice."
            return
        
        # 2. Assemble context
        notice_context = assemble_context(notice, user_branch, user_year)
        
        # 3. Retrieve chat history
        history = get_chat_history(user_id, notice_id, limit=10)
        
        # 4. Configure LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=GOOGLE_API_KEY,
            temperature=0.5,
            convert_system_message_to_human=True,
            max_output_tokens=2048
        )
        
        # 5. Build message chain
        initial_instruction = f"{SYSTEM_PROMPT}\n\n{notice_context}"
        messages = []
        
        if history:
             messages.append(HumanMessage(content=initial_instruction))
             for msg in history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))
             messages.append(HumanMessage(content=query))
        else:
            messages.append(HumanMessage(content=f"{initial_instruction}\n\nUser Question: {query}"))
        
        # 6. Stream response
        full_response = ""
        # Save user message first
        save_chat_message(user_id, notice_id, "user", query, user_branch, user_year)
        
        for chunk in llm.stream(messages):
            content = chunk.content
            if content:
                full_response += content
                yield content
        
        # 7. Save assistant response to DB
        save_chat_message(user_id, notice_id, "assistant", full_response, user_branch, user_year)
        
    except Exception as e:
        print(f"Error streaming response: {e}")
        yield f"Error: {str(e)}"

