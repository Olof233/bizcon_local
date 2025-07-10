"""
OpenAI model client for bizCon framework.
"""
from typing import Dict, List, Optional, Any, Union
import os
import json
import openai
import tiktoken
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import re
from tools import get_default_tools
from local_llm_function_calling import Generator

from .base import ModelClient


class LocalClient(ModelClient):
    """Client for local models."""
    
    def __init__(self, 
                 model_name: str, 
                 api_key: Optional[str] = None,
                 temperature: float = 0.7,
                 max_tokens: int = 1024,
                 **kwargs):
        """
        Initialize the model.
        
        Args:
            model_name: Name of the model to use
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum number of tokens to generate
            **kwargs: Additional model parameters
        """
        super().__init__(model_name, temperature, max_tokens, **kwargs)
        
        # Set API key
        self.api_key = None # Placeholder for local model client
        
        # Initialize client
        self.client = None  # Placeholder for local model client
        
        # Initialize tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto"
        )
        # print(f"Initialized local model: {model_name}")
    
    def generate_response(self, 
                         messages: List[Dict[str, str]], 
                         tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Generate a response from the OpenAI model.
        
        Args:
            messages: List of message objects in the format 
                     [{"role": "user", "content": "Hello"}, ...]
            tools: Optional list of tool definitions
            
        Returns:
            Dictionary with response content and metadata
        """
        try:
            
            # Prepare parameters
            params = {
                "model": self.model_name,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                **self.params
            }


            # Add tools if provided
            if tools:
                for tool in tools:
                    maintool = tool.get("function", {})
                    tool_desc = "".join(
                    f"tool_name: {maintool['name']}, description: {maintool.get('description', '')}, parameters: {maintool.get('parameters', '')}"      
                    )
            else:
                tool_desc = "no tools available"
            system_msg = {
                "role": "system",
                "content": f"You can call the tool in the following format:<function_call name='tool_name'>parameters</function_call>  available tools:  {tool_desc}. Call the tool when you need to, and do not call the tool when you do not need it. If you call the tool, please make sure to provide all the required parameters in the function call. If you are not sure about the parameters, you can ask the user for clarification. Do not use any other format to call the tool, only use <function_call name='tool_name'>parameters</function_call>. If you do not need to call any tool, just answer the question directly without calling and declare that you do not need the tools." #type: ignore
                }
            messages.insert(0, system_msg)
            
            # Make the call
            text = self.tokenizer.apply_chat_template(
                params["messages"],
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=True # Switches between thinking and non-thinking modes. Default is True.
            )
            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

            # conduct text completion
            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=params["max_tokens"],
                temperature=params["temperature"]
            )
            output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist() 

            try:
                # rindex finding 151668 (</think>)
                index = len(output_ids) - output_ids[::-1].index(151668)
            except ValueError:
                index = 0

            thinking_content = self.tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
            content = self.tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")
            response = thinking_content + content

            # Extract response content
            result = {"content": response}
            
            # Add tool calls if present
            pattern = r"<function_call name=['\"](.*?)['\"]>(.*?)</function_call>"
            matches = re.findall(pattern, response, re.DOTALL)
            if matches:
                generator = Generator.hf(tool_results, self.model) #type: ignore
                params = generator.generate(messages[0]['content'])
                print(params)

                # tool_objs = get_default_tools()
                # tool_results = []
                # for name, args in matches:
                #     tool = tool_objs.get(name)
                #     if tool:
                #         tool_result = tool.call(params)
                #     else:
                #         tool_result = {"error": f"Tool '{name}' not found"}
                #     tool_results.append({
                #         "name": name,
                #         "arguments": params,
                #         "result": tool_result
                #     })
                # if tool_results:
                #     result["tool_results"] = tool_results
                    
            return result
            
        except Exception as e:
            # return errors
            return {
                "content": f"Error: {str(e)}",
                "error": str(e)
            }
    
    def get_token_count(self, text: str) -> int:
        """
        Count the number of tokens in the given text.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        if not text:
            return 0
        
        return len(self.tokenizer.encode(text))