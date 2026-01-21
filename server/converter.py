import copy

TYPE_MAP =\
{
    "string": "string",
    "number": "double",
    "integer": "int",
    "object": "object",
    "array": "array",
    "boolean": "bool",
    "null": "null"
}

UNSUPPORTED_KEYS =\
{
    "title",
    "description",
    "examples",
    "default",
    "nullable",
    "format",
    "pattern",
    "minLength",
    "maxLength",
    "minimum",
    "maximum",
    "exclusiveMinimum",
    "exclusiveMaximum",
    "multipleOf",
    "enum",
    "const",
    "$comment",
    "readOnly",
    "writeOnly",
    "deprecated",
    "unevaluatedProperties",
    "patternProperties",
    "additionalItems",
    "anyOf",
    "allOf",
    "oneOf",
    "not",
    "if",
    "then",
    "else"
}

def resolve_refs(node: dict, defs: dict) -> dict:
    """Inline $ref definitions

    Args:
        node (dict): Node
        defs (dict): Defs

    Returns:
        dict: Updated node
    """
    
    if "$ref" in node:
        
        # * Extract the referenced model name
        
        ref: str = node["$ref"]
        
        name: str = ref.split("/")[-1]
        
        if name in defs:
            
            # * Replace the $ref with the actual schema
            
            resolved: dict = copy.deepcopy(defs[name])
            
            return resolve_refs(resolved, defs)
        
        return {}

    # * Recursively resolve nested objects ($ref)
    
    for key, value in list(node.items()):
        
        if isinstance(value, dict):
            
            node[key] = resolve_refs(value, defs)
            
        elif isinstance(value, list):
            
            node[key] = [resolve_refs(v, defs) if isinstance(v, dict) else v for v in value]

    return node

def convert(node: dict) -> dict:
    """Convert JSON Schema node → MongoDB bsonType schema

    Args:
        node (dict): Node

    Returns:
        dict: Scema
    """
    
    node = copy.deepcopy(node)

    # * Remove unsupported keywords
    
    keys_to_remove = [key for key in node.keys() if key in UNSUPPORTED_KEYS]

    for key in keys_to_remove: node.pop(key)

    # * Convert "type" → "bsonType"
    
    if "type" in node:
        
        t = node.pop("type")
        
        if isinstance(t, list):
            
            node["bsonType"] = [TYPE_MAP.get(x, x) for x in t]
            
        else:
            
            node["bsonType"] = TYPE_MAP.get(t, t)

    # * Convert nested properties
    
    if "properties" in node:
        
        for key, value in node["properties"].items():
            
            node["properties"][key] = convert(value)

    # * Convert array items
    
    if "items" in node:
        
        node["items"] = convert(node["items"])

    return node

def convert_pydantic_to_mongo(schema: dict) -> dict:
    """Convert a Pydantic JSON Schema into a MongoDB-compatible $jsonSchema

    Args:
        schema (dict): Pydantic JSON Schema

    Returns:
        dict: MongoDB-compatible $jsonSchema
    """
    
    schema = copy.deepcopy(schema)

    # * Extract definitions ($defs): MongoDB does not support $defs, so we remove them and store them for later.
    
    defs: dict = schema.pop("$defs", {})

    schema = resolve_refs(schema, defs)
    
    return convert(schema)

def convert_pydantic_to_mongo_2(schema: dict) -> dict:
    """Convert pydantic model into MongoDB format

    Args:
        schema (dict): Pydantic schema

    Returns:
        dict: MongoDB format
    """
    
    if "type" in schema:
        
        schema["bsonType"] = TYPE_MAP.get(schema["type"], schema["type"])
        
        del schema["type"]

    if "properties" in schema:
        
        for key, value in schema["properties"].items():
            
            schema["properties"][key] = convert_pydantic_to_mongo(value)

    if "items" in schema:
        
        schema["items"] = convert_pydantic_to_mongo(schema["items"])

    return schema