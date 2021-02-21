import re

TOKENIZER = "(?:(//.*?\n|/\*\*.*?\*/|\"([^\"]+)\"|\(|\)|\{|\}|\[|\]|;|\.|\/|\+|-|~|[a-zA-Z_]\w*|\d+|,|\*|&|\||<|>|=)(?:[\s\n]*))"
SYMBOLS = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/',
           '&', '|', '<', '>', '=', '-','~']
KEYWORDS = ['class', 'constructor', 'function', 'method', 'field', 'static',
            'var', 'int', 'char', 'boolean', 'true', 'false', 'null', 'this',
            'let', 'do', 'if', 'else', 'while', 'return', 'void']
SYMBOL_TRANSLATOR = {"<": "&lt;", ">": "&gt;", "\"": "&quot;", "&": "&amp;"}
SYMBOL_TO_XML = {"SYMBOL": "symbol", "KEYWORD": "keyword",
                 "IDENTIFIER": "identifier", "INT_CONST": "integerConstant",
                 "STRING_CONST": "stringConstant"}
STRING_RE = "\"(.*)\""
IDENTIFIER_RE = "^[a-zA-Z_]\w*$"
COMMENT_RE = "^(?://|/\*\*)"
INT_CONST_RE = "^\d+$"


class JackTokenizer:
    def __init__(self, lines):
        self._buffer = [mat.group(1) for mat in
                        re.finditer(TOKENIZER, '\n'.join(lines),flags=re.DOTALL)]
        self._buffer.reverse()
        self._has_next = True
        while re.match(COMMENT_RE, self._buffer[-1]):
            self._buffer.pop()

    def __repr__(self):
        return self._buffer[-1]

    def has_more_tokens(self):
        return len(self._buffer) > 0

    def advance(self):
        self._buffer.pop()
        while self.has_more_tokens() and self.get_type() == "COMMENT":
            self._buffer.pop()

    @staticmethod
    def _get_type(token):
        if token in SYMBOLS:
            return 'SYMBOL'
        if token in KEYWORDS:
            return 'KEYWORD'
        if re.match(STRING_RE, token):
            return 'STRING_CONST'
        if re.match(COMMENT_RE, token):
            return 'COMMENT'
        if re.match(INT_CONST_RE, token):
            return 'INT_CONST'
        if re.match(IDENTIFIER_RE, token):
            return 'IDENTIFIER'

    def peak(self, i):
        token = self._buffer[-1 - i]
        type = JackTokenizer._get_type(token)
        if type == 'SYMBOL' and token in SYMBOL_TRANSLATOR:
            return SYMBOL_TRANSLATOR[token], type
        return token, type

    def get_type(self):
        if self.has_more_tokens():
            token = self._buffer[-1]
            return JackTokenizer._get_type(token)
        raise SyntaxError("Error: no more tokens left.")

    def keyword(self):
        if (not self.has_more_tokens()) or self.get_type() != 'KEYWORD':
            raise SyntaxError("Error: current token is not of type 'keyboard', or none left")
        return self._buffer[-1]

    def symbol(self):
        if (not self.has_more_tokens()) or self.get_type() != 'SYMBOL':
            raise SyntaxError("Error: current token is not of type 'symbol', or none left")
        if self._buffer[-1] in SYMBOL_TRANSLATOR:
            return SYMBOL_TRANSLATOR[self._buffer[-1]]
        return self._buffer[-1]

    def string_val(self):
        if (not self.has_more_tokens()) or self.get_type() != 'STRING_CONST':
            raise SyntaxError("Error: current token is not of type 'string_val', or none left")
        return self._buffer[-1][1:-1]

    def int_val(self):
        if (not self.get_type()) or self.get_type() != 'INT_CONST':
            raise SyntaxError("Error: current token is not of type 'int_val', or none left")
        return self._buffer[-1]

    def identifier(self):
        if (not self.has_more_tokens()) or self.get_type() != "IDENTIFIER":
            raise SyntaxError("Error: current token is not of type 'identifier', or none left")
        return self._buffer[-1]

    @staticmethod
    def create_xml_label(type, token):
        return "<" + SYMBOL_TO_XML[type] + "> " + token + " </" + \
               SYMBOL_TO_XML[type] + ">"
