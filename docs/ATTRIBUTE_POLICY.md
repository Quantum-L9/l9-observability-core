# Attribute Policy

`attributes` exists for bounded producer metadata that does not yet justify a first-class canonical field.

## Allowed

- at most 32 attributes
- keys: lowercase ASCII letters, digits, `_`, `.`, `-`
- key length: 1..64
- scalar values only: string, integer, boolean
- integer values inside `[-9007199254740991, 9007199254740991]`
- string length: at most 512 characters

Validated attributes are copied into immutable model state. Mutating the caller's original dictionary after model creation MUST NOT change the event. Mutating the event's attributes MUST fail.

## Forbidden

- nested objects
- arrays
- floats
- bytes/blobs
- raw prompts or model responses
- raw tool request/response bodies
- stack dumps
- credentials or authentication material

Keys containing sensitive markers are rejected, including forms of:

- `secret`
- `password`
- `passwd`
- `token`
- `api_key`
- `apikey`
- `authorization`
- `cookie`
- `credential`

This is a deliberately conservative safety boundary. A reusable non-secret concept containing one of these markers should become a first-class field rather than bypassing the attribute guard.

## Graduation rule

If a field becomes operationally important across two or more independent consumers, it should graduate into a versioned first-class schema field rather than accumulating as an attribute convention.
