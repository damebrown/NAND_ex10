import JackTokenizer as tk

KEYWORD_CONST = ['true', 'false', 'null', 'this']
PRIM_VAR_TYPES = ['int', 'char', 'boolean']
OP = ["+", "-", "*", "/", "&amp;", "|", "&lt;", "&gt;", "="]
UNARY_OP = ["-", "~"]
STATMENT_STARTERS = ["let", "if", "while", "do", "return"]

SYMBOL = 'SYMBOL'
KEYWORD = 'KEYWORD'
STRING_CONST = 'STRING_CONST'
INT_CONST = 'INT_CONST'
IDENTIFIER = 'IDENTIFIER'


class CompilationEngine:
    def __init__(self, jack_lines):
        self._xml = []
        self._token = tk.JackTokenizer(jack_lines)

    def compile(self):
        self.compile_class()
        return self._xml

    def xml_append(self, symbol, type, advance=True):
        self._xml.append(self._token.create_xml_label(type, symbol))
        if advance:
            self._token.advance()

    def xml_append_opening(self, label):
        label = '<' + label + '>'
        self._xml.append(label)

    def xml_append_closing(self, label):
        self.xml_append_opening("/" + label)

    def expect(self, e_type, value=None):
        if e_type == SYMBOL:
            if isinstance(value, list):
                if self._token.symbol() not in value:
                    raise SyntaxError("Expected" + str(value) + "symbol")
            else:
                if self._token.symbol() != value:
                    raise SyntaxError("Expected" + str(value) + "symbol")
            self.xml_append(self._token.symbol(), self._token.get_type())
            return
        if e_type == KEYWORD:
            if isinstance(value, list):
                if self._token.keyword() not in value:
                    raise SyntaxError("Expected" + str(value) + "keyword")
            else:
                if self._token.keyword() != value:
                    raise SyntaxError("Expected" + str(value) + "keyword")
            self.xml_append(self._token.keyword(), self._token.get_type())
            return
        if e_type == IDENTIFIER:
            if self._token.get_type() != IDENTIFIER:
                raise SyntaxError("Expected an identifier")
            self.xml_append(self._token.identifier(), self._token.get_type())
            return
        if e_type == INT_CONST:
            if self._token.get_type() != INT_CONST:
                raise SyntaxError("Expected an int_const")
            self.xml_append(self._token.int_val(), self._token.get_type())
            return
        if e_type == STRING_CONST:
            if self._token.get_type() != STRING_CONST:
                raise SyntaxError("Expected a string_const")
            self.xml_append(self._token.string_val(), self._token.get_type())
            return

    def compile_class(self):
        if not self._token.has_more_tokens():
            return
        self.xml_append_opening('class')
        self.expect(KEYWORD, 'class')
        self.expect(IDENTIFIER)
        self.expect(SYMBOL, '{')
        self.compile_class_var_dec()
        self.compile_subroutines()
        self.expect(SYMBOL, '}')
        self.xml_append_closing('class')

    def compile_var_name_sequence(self):
        self.expect(IDENTIFIER)
        if self._token.get_type() == SYMBOL:
            if self._token.symbol() == ';':
                return True
        self.expect(SYMBOL, ',')
        return False

    def compile_class_var_dec(self):
        still_var_dec = True
        while still_var_dec:
            if self._token.keyword() in ['static', 'field']:
                self.xml_append_opening('classVarDec')
                # get 'static' or 'field'
                self.expect(KEYWORD, ['static', 'field'])
                # get type of variable
                if self._token.get_type() == IDENTIFIER:
                    self.expect(IDENTIFIER)
                else:
                    self.expect(KEYWORD, PRIM_VAR_TYPES)
                done = False
                while not done:
                    done = self.compile_var_name_sequence()
                    if done:
                        self.xml_append(self._token.symbol(),
                                        self._token.get_type())
                self.xml_append_closing('classVarDec')
            else:
                still_var_dec = False
        return

    def compile_subroutines(self):
        while self.compile_subroutine():
            pass

    def compile_subroutine(self):
        if self._token.get_type() == SYMBOL and \
                        self._token.symbol() == "}":
            return False
        if self._token.keyword() in ['constructor', 'function', 'method']:
            self.xml_append_opening('subroutineDec')
            self.expect(KEYWORD, ['constructor', 'function', 'method'])
            if self._token.get_type() == KEYWORD:
                self.expect(KEYWORD, PRIM_VAR_TYPES + ['void'])
            else:
                self.expect(IDENTIFIER)
            self.expect(IDENTIFIER)
            self.expect(SYMBOL, '(')
            self.compile_parameter_list()
            self.expect(SYMBOL, ')')
            self.xml_append_opening('subroutineBody')
            self.expect(SYMBOL, '{')
            self.compile_var_dec()
            self.compile_statements()
            self.expect(SYMBOL, '}')
            self.xml_append_closing('subroutineBody')
            self.xml_append_closing('subroutineDec')
            return True
        return False

    def compile_parameter_list(self):
        self.xml_append_opening('parameterList')
        while self._token.get_type() != SYMBOL:
            self.expect(KEYWORD, PRIM_VAR_TYPES)
            self.expect(IDENTIFIER)
            if self._token.symbol() != ')':
                self.expect(SYMBOL, ',')
        self.xml_append_closing('parameterList')

    def compile_var_dec(self):
        while self._token.get_type() == KEYWORD \
                and self._token.keyword() == "var":
            self.xml_append_opening('varDec')
            self.expect(KEYWORD, "var")
            if self._token.get_type() == IDENTIFIER:
                self.expect(IDENTIFIER)
            else:
                self.expect(KEYWORD, PRIM_VAR_TYPES)
            self.expect(IDENTIFIER)
            while self._token.get_type() == SYMBOL \
                    and self._token.symbol() == ",":
                self.expect(SYMBOL, ',')
                self.expect(IDENTIFIER)
            self.expect(SYMBOL, ';')
            self.xml_append_closing('varDec')

    def compile_statements(self):
        self.xml_append_opening('statements')
        at_least_one = False
        while self.compile_statement():
            at_least_one = True
        if at_least_one:
            self.xml_append_closing('statements')
        else:
            self._xml.pop()

    def compile_statement(self):
        if self._token.get_type() == KEYWORD and \
                        self._token.keyword() in STATMENT_STARTERS:
            if self._token.keyword() == 'let':
                self.compile_let()
            elif self._token.keyword() == 'if':
                self.compile_if()
            elif self._token.keyword() == 'while':
                self.compile_while()
            elif self._token.keyword() == 'do':
                self.compile_do()
            elif self._token.keyword() == 'return':
                self.compile_return()
            return True
        return False

    def compile_do(self):
        self.xml_append_opening('doStatement')
        self.expect(KEYWORD, 'do')
        self.compile_subroutine_call()
        self.expect(SYMBOL, ';')
        self.xml_append_closing('doStatement')

    def compile_let(self):
        self.xml_append_opening('letStatement')
        # 'let' keyword
        self.expect(KEYWORD, 'let')
        # varName
        self.expect(IDENTIFIER)
        # ( '[' expression ']' )?  - optional
        if self._token.get_type() == SYMBOL and self._token.symbol() == '[':
            self.expect(SYMBOL, '[')
            self.compile_expression()
            self.expect(SYMBOL, ']')
        # '=' symbol
        self.expect(SYMBOL, '=')
        # expression
        self.compile_expression()
        # ';' symbol
        self.expect(SYMBOL, ';')
        self.xml_append_closing('letStatement')

    def compile_while(self):
        self.xml_append_opening('whileStatement')
        # 'while' keyword
        self.expect(KEYWORD, 'while')
        # '(' symbol
        self.expect(SYMBOL, '(')
        # expression
        self.compile_expression()
        # ')' symbol
        self.expect(SYMBOL, ')')
        # '{' symbol
        self.expect(SYMBOL, '{')
        # statements
        self.compile_statements()
        # '}' symbol
        self.expect(SYMBOL, '}')
        self.xml_append_closing('whileStatement')

    def compile_return(self):
        self.xml_append_opening('returnStatement')
        # 'return' keyword
        self.expect(KEYWORD, 'return')
        # expression? - optional
        if self._token.get_type() != SYMBOL or self._token.symbol() != ';':
            self.compile_expression()
        # ';' symbol
        self.expect(SYMBOL, ';')
        self.xml_append_closing('returnStatement')

    def compile_if(self):
        self.xml_append_opening('ifStatement')
        # 'if' keyword
        self.expect(KEYWORD, 'if')
        # '(' symbol
        self.expect(SYMBOL, '(')
        # expression
        self.compile_expression()
        # ')' symbol
        self.expect(SYMBOL, ')')
        # '{' symbol
        self.expect(SYMBOL, '{')
        # statements
        self.compile_statements()
        # '}' symbol
        self.expect(SYMBOL, '}')
        # (else clause) - optional
        if self._token.get_type() == KEYWORD and \
                        self._token.keyword() == 'else':
            # 'else' keyword
            self.expect(KEYWORD, 'else')
            # '{' symbol
            self.expect(SYMBOL, '{')
            # statements
            self.compile_statements()
            # '}' symbol
            self.expect(SYMBOL, '}')
        self.xml_append_closing('ifStatement')

    def compile_expression(self, mandatory=True):
        self.xml_append_opening('expression')
        # term - mandatory
        if not self.compile_term():
            self._xml.pop()
            if mandatory:
                raise SyntaxError("Expected term")
            else:
                return False
        # (op term)*
        while self._token.get_type() == SYMBOL and self._token.symbol() in OP:
            self.expect(SYMBOL, OP)
            self.compile_term()
        self.xml_append_closing('expression')
        return True

    def compile_term(self):
        self.xml_append_opening('term')
        if self._token.get_type() == INT_CONST:
            self.expect(INT_CONST)
        elif self._token.get_type() == STRING_CONST:
            self.expect(STRING_CONST)
        elif self._token.get_type() == KEYWORD \
                and self._token.keyword() in KEYWORD_CONST:
            self.expect(KEYWORD, KEYWORD_CONST)
        elif self._token.get_type() == SYMBOL:
            if self._token.symbol() == '(':
                self.expect(SYMBOL, '(')
                self.compile_expression()
                self.expect(SYMBOL, ')')
            elif self._token.symbol() in UNARY_OP:
                self.expect(SYMBOL, UNARY_OP)
                self.compile_term()
            else:
                self._xml.pop()
                return False
        elif self._token.get_type() == IDENTIFIER:
            next_token, next_type = self._token.peak(1)
            if next_type == SYMBOL and next_token in ['(', '.']:
                self.compile_subroutine_call()
            elif next_type == SYMBOL and next_token == '[':
                self.expect(IDENTIFIER)
                self.expect(SYMBOL, '[')
                self.compile_expression()
                self.expect(SYMBOL, ']')
            else:
                self.expect(IDENTIFIER)
        else:
            self._xml.pop()
            return False
        self.xml_append_closing('term')
        return True

    def compile_expression_list(self):
        self.xml_append_opening('expressionList')
        if self.compile_expression(mandatory=False):
            while self._token.get_type() == SYMBOL \
                    and self._token.symbol() == ',':
                self.expect(SYMBOL, ',')
                self.compile_expression()
        self.xml_append_closing('expressionList')

    def compile_subroutine_call(self):
        self.expect(IDENTIFIER)
        if self._token.get_type() == SYMBOL and self._token.symbol() == ".":
            self.expect(SYMBOL, '.')
            self.expect(IDENTIFIER)
        self.expect(SYMBOL, '(')
        self.compile_expression_list()
        self.expect(SYMBOL, ')')
