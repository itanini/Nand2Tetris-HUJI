"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class VMWriter:
    """
    Writes VM commands into a file. Encapsulates the VM command syntax.
    """
    UNARY_DICT = {"-": "neg", "~": "not", "#": "rightshift", "^": "leftshift"}
    BINARY_DICT ={'+': 'add', '-': 'sub', '=': 'eq', '>': 'gt', '<': 'lt', '&': 'and', '|': 'or', '*': 'call Math.multiply 2',
                   '/': 'call Math.divide 2'}

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Creates a new file and prepares it for writing VM commands."""
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self.output_stream = output_stream

    def write_push(self, segment: str, index: int) -> None:
        """Writes a VM push command.

        Args:
            segment (str): the segment to push to, can be "CONST", "ARG", 
            "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP"
            index (int): the index to push to.
        """
        self.output_stream.write(f'push {segment} {index}\n')

    def write_pop(self, segment: str, index: int) -> None:
        """Writes a VM pop command.

        Args:
            segment (str): the segment to pop from, can be "CONST", "ARG", 
            "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP".
            index (int): the index to pop from.
        """
        self.output_stream.write(f'pop {segment} {index}\n')
        pass

    def write_binary_arithmetic(self, command: str) -> None:
        """Writes a VM arithmetic command.

        Args:
            command (str): the command to write, can be "ADD", "SUB", "NEG", 
            "EQ", "GT", "LT", "AND", "OR", "NOT", "SHIFTLEFT", "SHIFTRIGHT".
        """
        self.output_stream.write(f'{VMWriter.BINARY_DICT[command]}\n')

    def write_unary_arithmetic(self, command:str):
        self.output_stream.write(f'{VMWriter.UNARY_DICT[command]}\n')

    def write_label(self, label: str) -> None:
        """Writes a VM label command.

        Args:
            label (str): the label to write.
        """
        self.output_stream.write(f'label {label}\n')

    def write_goto(self, label: str) -> None:
        """Writes a VM goto command.

        Args:
            label (str): the label to go to.
        """
        self.output_stream.write(f'goto {label}\n')

    def write_if(self, label: str) -> None:
        """Writes a VM if-goto command.

        Args:
            label (str): the label to go to.
        """
        self.output_stream.write(f'if-goto {label}\n')

    def write_call(self, class_name: str,func_name: str, n_args: int) -> None:
        """Writes a VM call command.

        Args:
            name (str): the name of the function to call.
            n_args (int): the number of arguments the function receives.
        """
        self.output_stream.write(f'call {class_name}.{func_name} {n_args}\n')

    def write_function(self, name: str, n_locals: int) -> None:
        """Writes a VM function command.

        Args:
            name (str): the name of the function.
            n_locals (int): the number of local variables the function uses.
        """
        self.output_stream.write(f'function {name} {n_locals}\n')

    def write_return(self) -> None:
        """Writes a VM return command."""
        self.output_stream.write(f'return\n')
