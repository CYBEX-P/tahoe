from fastjsonschema import validate
from jsonschema import Draft7Validator
import json, jsonschema
fc = jsonschema.FormatChecker()
instance ={
	"nid" : 123,
	"att_type" : "sha256",
##	"value" : "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2",
        "value" : "1.1.1.1",
##        "valid" : False,
	"uuid" : "attribute--b2c6fadc-96f4-4cdd-8a73-502c8c9f4e47",
	"obj_ref" : ["object--b2c6fAdc-96f4-4cdd-9a73-502c8c9f4e47", "object--b2c6fAdc-96f4-4cdd-8a73-502c8c9f4e47"]
}

with open('attribute/attribute.json') as f:
    schema = json.load(f)

##with open('attribute/attribute_pattern.json') as f:
##    schema_pattern = json.load(f)

##Draft4Validator(schema = schema, format_checker=fc).validate(instance)
d = Draft7Validator(schema)
d.validate(instance)

##validate(schema, instance)

##validate(schema_core, instance)
##validate(schema_pattern, instance)

