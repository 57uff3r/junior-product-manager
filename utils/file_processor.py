import os
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class FileProcessor:
    def __init__(self, directory_path: str):
        """Initialize with the directory containing files to process."""
        self.directory_path = directory_path
    
    def process_all_files(self) -> Dict[str, str]:
        """Process all supported files in the directory."""
        all_files = {}
        
        if not os.path.exists(self.directory_path):
            logger.error(f"Directory not found: {self.directory_path}")
            return all_files
        
        # Walk through all files in the directory
        for root, _, files in os.walk(self.directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    # Process based on file extension
                    if file.endswith('.txt'):
                        content = self._process_text_file(file_path)
                    elif file.endswith('.json'):
                        content = self._process_json_file(file_path)
                    else:
                        # Skip unsupported file types
                        continue
                    
                    # Store the processed content
                    if content:
                        rel_path = os.path.relpath(file_path, self.directory_path)
                        all_files[rel_path] = content
                
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")
        
        return all_files
    
    def _process_text_file(self, file_path: str) -> str:
        """Process a text file and return its content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add file name as a header
            file_name = os.path.basename(file_path)
            return f"# {file_name}\n\n{content}"
        
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {e}")
            return ""
    
    def _process_json_file(self, file_path: str) -> str:
        """Process a JSON file and convert it to readable text."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert JSON to a readable format
            file_name = os.path.basename(file_path)
            content = f"# {file_name}\n\n"
            
            # Format the JSON data as readable text
            content += self._format_json_as_text(data)
            
            return content
        
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in file {file_path}")
            return ""
        except Exception as e:
            logger.error(f"Error processing JSON file {file_path}: {e}")
            return ""
    
    def _format_json_as_text(self, data: Any, indent: int = 0) -> str:
        """Format JSON data as readable text."""
        result = ""
        indent_str = "  " * indent
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    result += f"{indent_str}{key}:\n"
                    result += self._format_json_as_text(value, indent + 1)
                else:
                    result += f"{indent_str}{key}: {value}\n"
        
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    result += f"{indent_str}- \n"
                    result += self._format_json_as_text(item, indent + 1)
                else:
                    result += f"{indent_str}- {item}\n"
        
        else:
            result += f"{indent_str}{data}\n"
        
        return result 