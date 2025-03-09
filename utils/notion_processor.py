from typing import List, Dict, Any
import logging
from notion_client import Client

logger = logging.getLogger(__name__)

class NotionReader:
    def __init__(self, api_key: str):
        """Initialize Notion client with API key."""
        self.client = Client(auth=api_key)
    
    def get_page_content(self, page_id: str) -> str:
        """Get the content of a specific page."""
        try:
            # Get page properties
            page = self.client.pages.retrieve(page_id=page_id)
            title = self._extract_title(page)
            
            # Get page blocks (content)
            blocks = self._get_all_blocks(page_id)
            content = self._blocks_to_text(blocks)
            
            return f"# {title}\n\n{content}"
        except Exception as e:
            logger.error(f"Error retrieving page {page_id}: {e}")
            return ""
    
    def get_all_pages_from_root(self, root_page_id: str) -> Dict[str, str]:
        """Get content from all pages under the root page."""
        all_pages = {}
        
        # Get the root page first
        root_content = self.get_page_content(root_page_id)
        all_pages[root_page_id] = root_content
        
        # Get child pages
        child_pages = self._get_child_pages(root_page_id)
        
        # Recursively get content from all child pages
        for child_id in child_pages:
            # Get the child page content
            child_content = self.get_page_content(child_id)
            all_pages[child_id] = child_content
            
            # Recursively get grandchildren
            grandchildren = self._get_all_nested_pages(child_id)
            all_pages.update(grandchildren)
        
        return all_pages
    
    def _get_all_nested_pages(self, page_id: str) -> Dict[str, str]:
        """Recursively get all nested pages under a page."""
        nested_pages = {}
        
        # Get child pages
        child_pages = self._get_child_pages(page_id)
        
        # Get content for each child and their children
        for child_id in child_pages:
            child_content = self.get_page_content(child_id)
            nested_pages[child_id] = child_content
            
            # Recursively get grandchildren
            grandchildren = self._get_all_nested_pages(child_id)
            nested_pages.update(grandchildren)
        
        return nested_pages
    
    def _get_child_pages(self, page_id: str) -> List[str]:
        """Get IDs of all child pages under a page."""
        child_pages = []
        
        blocks = self._get_all_blocks(page_id)
        for block in blocks:
            if block["type"] == "child_page":
                child_pages.append(block["id"])
            elif block["has_children"]:
                # Get blocks within this block
                child_blocks = self._get_all_blocks(block["id"])
                for child_block in child_blocks:
                    if child_block["type"] == "child_page":
                        child_pages.append(child_block["id"])
        
        return child_pages
    
    def _get_all_blocks(self, block_id: str) -> List[Dict[str, Any]]:
        """Get all blocks from a page or block."""
        results = []
        has_more = True
        start_cursor = None
        
        while has_more:
            if start_cursor:
                response = self.client.blocks.children.list(
                    block_id=block_id, 
                    start_cursor=start_cursor
                )
            else:
                response = self.client.blocks.children.list(block_id=block_id)
            
            results.extend(response["results"])
            has_more = response["has_more"]
            if has_more:
                start_cursor = response["next_cursor"]
        
        return results
    
    def _extract_title(self, page: Dict[str, Any]) -> str:
        """Extract the title from a page object."""
        if "properties" in page:
            for prop_name, prop_data in page["properties"].items():
                if prop_data["type"] == "title" and prop_data["title"]:
                    return " ".join([text_obj["plain_text"] for text_obj in prop_data["title"]])
        return "Untitled"
    
    def _blocks_to_text(self, blocks: List[Dict[str, Any]]) -> str:
        """Convert blocks to plain text."""
        text_parts = []
        
        for block in blocks:
            block_text = self._block_to_text(block)
            if block_text:
                text_parts.append(block_text)
            
            # If the block has children, get their text too
            if block.get("has_children", False):
                child_blocks = self._get_all_blocks(block["id"])
                child_text = self._blocks_to_text(child_blocks)
                if child_text:
                    # Indent child text for better readability
                    indented_text = "\n".join(f"  {line}" for line in child_text.split("\n"))
                    text_parts.append(indented_text)
        
        return "\n\n".join(text_parts)
    
    def _block_to_text(self, block: Dict[str, Any]) -> str:
        """Convert a single block to text."""
        block_type = block["type"]
        
        if block_type == "paragraph":
            return self._rich_text_to_plain_text(block["paragraph"]["rich_text"])
        elif block_type == "heading_1":
            return f"# {self._rich_text_to_plain_text(block['heading_1']['rich_text'])}"
        elif block_type == "heading_2":
            return f"## {self._rich_text_to_plain_text(block['heading_2']['rich_text'])}"
        elif block_type == "heading_3":
            return f"### {self._rich_text_to_plain_text(block['heading_3']['rich_text'])}"
        elif block_type == "bulleted_list_item":
            return f"• {self._rich_text_to_plain_text(block['bulleted_list_item']['rich_text'])}"
        elif block_type == "numbered_list_item":
            return f"1. {self._rich_text_to_plain_text(block['numbered_list_item']['rich_text'])}"
        elif block_type == "to_do":
            checked = "✓" if block["to_do"]["checked"] else "☐"
            return f"{checked} {self._rich_text_to_plain_text(block['to_do']['rich_text'])}"
        elif block_type == "toggle":
            return f"▶ {self._rich_text_to_plain_text(block['toggle']['rich_text'])}"
        elif block_type == "code":
            language = block["code"].get("language", "")
            return f"```{language}\n{self._rich_text_to_plain_text(block['code']['rich_text'])}\n```"
        elif block_type == "quote":
            return f"> {self._rich_text_to_plain_text(block['quote']['rich_text'])}"
        elif block_type == "callout":
            emoji = block["callout"].get("icon", {}).get("emoji", "")
            return f"{emoji} {self._rich_text_to_plain_text(block['callout']['rich_text'])}"
        elif block_type == "divider":
            return "---"
        elif block_type == "child_page":
            # Just return the title of the child page
            return f"[[Page: {block.get('child_page', {}).get('title', 'Untitled')}]]"
        else:
            # For unsupported block types, return empty string
            return ""
    
    def _rich_text_to_plain_text(self, rich_text: List[Dict[str, Any]]) -> str:
        """Convert rich text array to plain text."""
        if not rich_text:
            return ""
        
        return " ".join([text_obj["plain_text"] for text_obj in rich_text]) 