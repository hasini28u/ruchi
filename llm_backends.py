# llm_backends.py

import requests
import config
import google.generativeai as genai

# Configure the Gemini API with the key from config.py
# This is done once at the beginning of the script.
if config.GEMINI_API_KEY:
    genai.configure(api_key=config.GEMINI_API_KEY)

# Call Ollama API (for English)
def call_ollama(messages):
    sys_prompt, convo_history = "", ""
    for m in messages:
        if m["role"] == "system":
            sys_prompt += m["content"] + "\n"
        elif m["role"] == "user":
            convo_history += f"User: {m['content']}\n"
        elif m["role"] == "assistant":
            convo_history += f"Assistant: {m['content']}\n"
    prompt = sys_prompt + "\n" + convo_history + "\nAssistant:"

    try:
        payload = {
            "model": config.OLLAMA_MODEL_ID,
            "prompt": prompt,
            "options": {"temperature": config.TEMPERATURE, "num_predict": config.MAX_TOKENS},
            "stream": False,
        }
        r = requests.post(config.OLLAMA_URL, json=payload, timeout=300) 
        r.raise_for_status()
        data = r.json()
        return data.get("response", "")
    except Exception as e:
        return f"⚠ Ollama backend error: {e}"

# Call Gemini API (for Telugu)
def call_gemini(messages):
    # Gemini requires a specific message format
    try:
        # The genai library handles the role and content directly,
        # but the system prompt needs to be passed as a message.
        model = genai.GenerativeModel(config.GEMINI_MODEL_ID)
        response = model.generate_content(
            messages,
            generation_config=genai.GenerationConfig(
                temperature=config.TEMPERATURE,
                max_output_tokens=config.MAX_TOKENS,
            )
        )
        return response.text
    except Exception as e:
        return f"⚠ Gemini backend error: {e}"

# Router function to choose the backend based on language
def ask(messages, language="english"):
    if language.lower() == "telugu":
        system_prompt = config.SYSTEM_PROMPT_TELUGU
        # For Gemini, the system prompt and chat history must be combined
        # into a single messages list with the correct format.
        # This is where the fix is implemented.
        formatted_messages = [{"role": "user", "parts": [system_prompt]}]
        for message in messages:
            formatted_messages.append({"role": message["role"], "parts": [message["content"]]})
        return call_gemini(formatted_messages)
    else: # Default to English
        system_prompt = config.SYSTEM_PROMPT_ENGLISH
        # Ollama expects a different format, so we use the old logic.
        messages_with_system = [{"role": "system", "content": system_prompt}] + messages
        return call_ollama(messages_with_system)
