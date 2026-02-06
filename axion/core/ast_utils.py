import tree_sitter_python as tspython
from tree_sitter import Language, Parser
import pathlib
from typing import List, Dict, Any, Optional

class ASTParser:
    def __init__(self):
        self.language = Language(tspython.language())
        self.parser = Parser(self.language)

    def parse_file(self, file_path: str) -> Optional[Any]:
        path = pathlib.Path(file_path)
        if not path.exists():
            return None
        
        with open(path, "rb") as f:
            content = f.read()
        
        return self.parser.parse(content)

    def get_definitions(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract classes and functions with their line ranges using recursive traversal."""
        tree = self.parse_file(file_path)
        if not tree:
            return []

        with open(file_path, "rb") as f:
            content = f.read()

        definitions = []
        
        def explore(node):
            # Check for definitions
            if node.type in ["class_definition", "function_definition", "decorated_definition"]:
                # Find name
                name_node = node.child_by_field_name("name")
                if not name_node and node.type == "decorated_definition":
                    # For decorated definitions, the name is in the class/function child
                    inner = node.child_by_field_name("definition")
                    if inner:
                        name_node = inner.child_by_field_name("name")
                
                name = content[name_node.start_byte:name_node.end_byte].decode("utf-8") if name_node else "anonymous"
                
                # Docstring extraction
                docstring = None
                body = node.child_by_field_name("body")
                if body and body.children:
                    for stmt in body.children:
                        if stmt.type == "expression_statement":
                            child = stmt.children[0]
                            if child.type == "string":
                                docstring = content[child.start_byte:child.end_byte].decode("utf-8").strip('"\' \n')
                        break # Only first statement

                definitions.append({
                    "name": name,
                    "type": "class" if "class" in node.type else "function",
                    "start_line": node.start_point[0] + 1,
                    "end_line": node.end_point[0] + 1,
                    "docstring": docstring
                })

            # Always explore children regardless of current node type
            for child in node.children:
                explore(child)

        explore(tree.root_node)
        return definitions

    def get_source_segment(self, file_path: str, start_line: int, end_line: int) -> str:
        """Extract a segment of code from a file by line numbers."""
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Lines are 1-indexed in our definitions, but 0-indexed in the list
        return "".join(lines[start_line-1 : end_line])
