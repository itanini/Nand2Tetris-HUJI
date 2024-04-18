"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import JackTokenizer
import SymbolTable
import VMWriter
from JackTokenizer import Token


class CompilationError(BaseException):
    pass


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """


    def __init__(self, input_stream: JackTokenizer, output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.output_stream = output_stream
        self.tokenizer = input_stream
        self.cur_token = next(self.tokenizer.token_generator())
        self.next_token()
        self.class_name = self.cur_token.text
        if self.cur_token.type == "identifier":
            JackTokenizer.CLASS_NAMES.append(self.class_name)
            self.cur_token.set_type("symbol")
        self.table = SymbolTable.SymbolTable()
        self.cur_func = None
        self.writer = VMWriter.VMWriter(output_stream)
        self.label_counter = 0

    def compile_class(self) -> None:
        """Compiles a complete class."""

        self.class_name = self.cur_token.text
        self.next_token()
        self.next_token()
        while self.cur_token.text in ['field', 'static']:
            self.compile_class_var_dec()
        while self.cur_token and self.cur_token.text in ['function', 'method', 'constructor']:
            self.compile_subroutine()
            self.next_token()



    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        kind = self.cur_token.text
        type = self.next_token().text # type
        if self.cur_token.type == "identifier":
            JackTokenizer.CLASS_NAMES.append(type)
            self.cur_token.set_type("symbol")
        name = self.next_token().text  # name
        self.table.define(name, type, kind)
        self.next_token()  # ;/,

        while self.cur_token.text == ",":
            self.next_token()  # name
            name = self.cur_token.text
            self.table.define(name, type, kind)
            self.next_token()  # ,\ ;
        self.next_token() # kind/ function/ method /constructor /

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        func_name, func_type = self.start_subroutine()
        while self.next_token().text == "var":
            self.compile_var_dec()
        self.writer.write_function(f"{self.class_name}.{func_name}", self.table.kind_count('local'))
        if func_type == "constructor":
            # n_fields = self.table.table.count(axis=)
            self.writer.write_push("constant", self.table.kind_count('field'))
            self.writer.write_call("Memory", "alloc", 1)
            self.writer.write_pop("pointer", 0)
        elif func_type == "method":
            self.writer.write_push("argument", 0)
            self.writer.write_pop("pointer", 0)
        self.compile_statements()
        self.cur_func=None

    def start_subroutine(self):
        n_args = 0
        self.table.start_subroutine()
        func_type = self.cur_token.text
        func_class = self.next_token().text
        if func_type == "method":
            self.table.define("this", func_class, "argument")
            n_args += 1
        func_name = self.next_token().text #function name
        self.next_token() # (
        n_args = self.compile_parameter_list(n_args)
        self.next_token() # {
        self.cur_func = func_name
        return func_name, func_type

    def compile_parameter_list(self, n_args) -> int:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        self.next_token()  # first arg type / )
        if self.cur_token.text == ")":  # if no parameters in the list
            return n_args
        # add args to symbol table:
        type = self.cur_token.text
        if self.cur_token.type == "identifier":
            JackTokenizer.CLASS_NAMES.append(type)
            self.cur_token.set_type("symbol")
        name = self.next_token().text # name
        self.table.define(name, type, "argument")
        n_args += 1

        self.next_token()  # , or )
        if self.cur_token.text == ",":
            return self.compile_parameter_list(n_args)
        return n_args

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""

        type = self.next_token().text
        name = self.next_token().text
        self.table.define(name, type, "local")
        while self.next_token().text == ",":
            name = self.next_token().text
            self.table.define(name, type, "local")


    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing
        "{}".
        when return from statement compilation cur_token should be ;!!!!!!!!!!!!!!!!!!
        """

        while self.cur_token.text in ["let", "do", "if", "while", "return", "else"]:
            if self.cur_token.text == "let":
                self.compile_let()
            elif self.cur_token.text == "do":
                self.compile_do()
            elif self.cur_token.text == "if":
                self.compile_if()
                continue
            elif self.cur_token.text == "while":
                self.compile_while()
            elif self.cur_token.text == "return":
                self.compile_return()
            self.next_token()  # do\if\....


    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.next_token()
        self.compile_expression()
        self.writer.write_pop("temp", 0)


    def compile_let(self) -> None:
        """Compiles a let statement."""
        array = False
        name = self.next_token().text  # name
        self.next_token()  # [ / =
        if self.cur_token and self.cur_token.text == "[":
            array = True
            self.set_array_index(name)
        self.next_token()
        self.compile_expression()
        if array:
            self.writer.write_pop("temp", 0)
            self.writer.write_pop("pointer", 1)
            self.writer.write_push("temp", 0)
            self.writer.write_pop("that", 0)
        if not array:
            self.writer.write_pop(self.table.kind_of(name), self.table.index_of(name))  # pops the first value in the stuck

    def set_array_index(self, name):
        self.writer.write_push(self.table.kind_of(name), self.table.index_of(name))
        self.next_token()  # expression
        self.compile_expression()
        self.writer.write_binary_arithmetic("+")
        self.next_token() # =

    def compile_while(self) -> None:
        """Compiles a while statement."""
        while_label = f"WHILE.{self.cur_func}.{self.class_name}.{self.label_counter}"
        out_label = F"OUT.{self.cur_func}.{self.class_name}.{self.label_counter}"
        self.label_counter +=1
        self.writer.write_label(while_label)  # back to while label
        self.next_token()  # while
        self.next_token()  # (
        self.compile_expression()
        self.next_token()  # )
        self.writer.write_unary_arithmetic("~")  # if not expression
        self.writer.write_if(out_label)  # out of the while label
        self.next_token()  # {
        self.compile_statements()  # not sure cus statments can be here function calls as well
        self.writer.write_goto(while_label)
        self.writer.write_label(out_label)



    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.next_token()  # name/;
        if self.cur_token.text == ";":
            self.writer.write_push("constant", 0)  # returning void
        # elif self.cur_token.text == "this":
        #     self.writer.write_push("pointer", 0)
        else:
            self.compile_expression()
        self.writer.write_return()
    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause.""" # (
        if_label = f'IF.{self.cur_func}.{self.class_name}.{self.label_counter}'
        else_label =f'ELSE.{self.cur_func}.{self.class_name}.{self.label_counter}'

        self.label_counter +=1
        self.next_token() # name
        self.compile_expression()
        # self.next_token()  # {
        self.writer.write_unary_arithmetic("~")  # if not expression
        self.writer.write_if(else_label)  # go to label 1
        self.next_token()
        self.compile_statements()  # needs more than that
        self.writer.write_goto(if_label)
        self.writer.write_label(else_label)
        self.next_token()
        if self.cur_token.text == "else":
            self.compile_else()
        self.writer.write_label(if_label)


    def compile_else(self):
        self.next_token()  # else
        self.next_token()  # {
        self.compile_statements()
        self.next_token()# needs mo
        # re than that

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.compile_term()
        while self.cur_token.text in JackTokenizer.BINARY_OPERATORS:
            op = self.cur_token.text
            self.next_token()
            self.compile_term()
            self.writer.write_binary_arithmetic(op)

    def compile_term(self) -> None:
        """Compiles a term.
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """

        if self.cur_token.text == "(":
            self.next_token()
            self.compile_expression()
            self.next_token()
        elif self.cur_token.type == "integerConstant":
            self.writer.write_push("constant", int(self.cur_token.text))
            self.next_token() #,/)
        elif self.cur_token.type == "stringConstant":
            self.writer.write_push("constant", len(self.cur_token.text))
            self.writer.write_call("String","new", 1)
            for char in self.cur_token.text:
                self.writer.write_push("constant",ord(char))
                self.writer.write_call('String','appendChar', 2)
            self.next_token()
        elif self.cur_token.text in ['true', 'false', 'null']:
            self.writer.write_push("constant", 0)
            if self.cur_token.text == 'true':
                self.writer.write_unary_arithmetic("~")
            self.next_token()
        elif self.cur_token.text == "this":
            self.writer.write_push("pointer", 0)
            self.next_token() #;
        elif self.cur_token.type == "identifier":
            name = self.cur_token.text
            self.next_token()
            if self.cur_token.text == '[':
                self.next_token()
                self.compile_expression()
                self.writer.write_push(self.table.kind_of(name), self.table.index_of(name))
                self.writer.write_binary_arithmetic('+')
                self.writer.write_pop('pointer', 1)
                self.writer.write_push('that', 0)
                self.next_token()  # ]
                # self.next_token()
            elif self.cur_token.text == '(': # .
                self.writer.write_push("pointer", 0)
                n_args = self.compile_expression_list(1)
                self.writer.write_call(f"{self.class_name}", f"{name}", n_args)
            elif self.cur_token.text == '.':
                if not self.table.find_name(name):
                    JackTokenizer.CLASS_NAMES.append(name)
                    self.compile_static_method_call(name)
                    return
                self.writer.write_push(self.table.kind_of(name), self.table.index_of(name))
                self.next_token() # .
                func_name = self.cur_token.text
                self.next_token()
                n_args = self.compile_expression_list(1)

                self.writer.write_call(f"{self.table.type_of(name)}", f"{func_name}", n_args)
            else:
                self.writer.write_push(self.table.kind_of(name), self.table.index_of(name))
                return
        elif self.cur_token.text in JackTokenizer.CLASS_NAMES:
            class_name = self.cur_token.text
            self.next_token()
            self.compile_static_method_call(class_name)
        elif self.cur_token.text in ['-', '~', '#', '^']:
            op = self.cur_token.text
            self.next_token()
            self.compile_term()
            self.writer.write_unary_arithmetic(op)

    def compile_static_method_call(self,class_name):
        func =  self.next_token().text  # function name
        self.next_token()  # .
        n_args = self.compile_expression_list()
        self.writer.write_call(f'{class_name}', f'{func}', n_args)

    def next_token(self):
        self.cur_token = next(self.tokenizer.token_generator())
        return self.cur_token

    def compile_expression_list(self, n_args_counter = 0) -> int:  # should count how many arguments are in the function
        """Compiles a (possibly empty) comma-separated list of expressions."""
        #name
        if self.next_token().text == ")":
            self.next_token()
            return n_args_counter
        self.compile_expression() # name
        n_args_counter += 1
        while self.cur_token.text == ',':
            n_args_counter += 1
            self.next_token()
            self.compile_expression()
        self.next_token()
        return n_args_counter



