# Tree-sitter queries for different languages

PYTHON_QUERIES = {
    "imports": """
        (import_from_statement
            module_name: (dotted_name) @import.from)
        (import_statement
            name: (dotted_name) @import.name)
        (import_from_statement
            module_name: (relative_dotted_name) @import.relative)
    """,
    "symbols": """
        (class_definition
            name: (identifier) @class.name)
        (function_definition
            name: (identifier) @function.name)
    """
}

JAVASCRIPT_QUERIES = {
    "imports": """
        (import_statement
            source: (string) @import.source)
        (call_expression
            function: (identifier) @func.name
            arguments: (arguments (string) @import.require)
            (#eq? @func.name "require"))
    """,
    "symbols": """
        (class_declaration
            name: (identifier) @class.name)
        (function_declaration
            name: (identifier) @function.name)
        (variable_declarator
            name: (identifier) @var.name
            value: [(arrow_function) (function)])
    """
}
