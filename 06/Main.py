"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code


def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    # Your code goes here!
    # A good place to start is to initialize a new Parser object:

    symbol_table = SymbolTable()

    # first pass:
    parser = Parser(input_file)
    num_of_l_commands = 0
    while parser.has_more_commands():
        if parser.command_type() == "L_COMMAND":
            symbol_table.add_entry(parser.symbol(), parser.cur_line - num_of_l_commands)
            num_of_l_commands = num_of_l_commands + 1
        parser.advance()

    # second pass:
    cur_num = 16
    while parser.has_more_commands():

        if parser.command_type() == "A_COMMAND":
            if not symbol_table.contains(parser.symbol()) and not parser.symbol().isdigit():
                symbol_table.add_entry(parser.symbol(), cur_num)
                binary_address = format(int(cur_num), '016b')
                output_file.write(binary_address + "\n")
                cur_num = cur_num + 1
            else:
                if parser.symbol().isdigit():
                    binary_address = format(int(parser.symbol()), '016b')
                    output_file.write(binary_address + "\n")
                else:
                    symbol_address = symbol_table.get_address(parser.symbol())
                    binary_address = format(int(symbol_address), '016b')
                    output_file.write(binary_address + "\n")

        if parser.command_type() == "C_COMMAND":
            binary_comp = Code.comp(parser.comp())  # 7-bits acccccc
            binary_dest = Code.dest(parser.dest())  # 3-bits ddd
            binary_jump = Code.jump(parser.jump())  # 3-bits jjj
            final_str = "111" + binary_comp + binary_dest + binary_jump
            output_file.write(final_str + "\n")

        if parser.command_type() == "C_EXTENDED_COMMAND":
            binary_extended = Code.extended(parser.get_ex_c_command())  # 10-bits 15-6
            binary_dest = Code.dest(parser.dest())  # 3-bits ddd
            binary_jump = Code.jump(parser.jump())  # 3-bits jjj
            final_str = binary_extended + binary_dest + binary_jump
            output_file.write(final_str + "\n")
        parser.advance()


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
