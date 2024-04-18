"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """Encapsulates access to the input code. Reads an assembly program
    by reading each command line-by-line, parses the current command,
    and provides convenient access to the commands components (fields
    and symbols). In addition, removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        self.cur_line = 0
        # A good place to start is to read all the lines of the input:
        input_lines = input_file.read().splitlines()  # a list of all the file lines
        self.arr_of_lines = []
        for i in range(0, len(input_lines)):
            cur_line = input_lines[i].split("//")[0].strip()
            if cur_line == "":
                continue
            else:
                self.arr_of_lines.append(cur_line)

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        # Your code goes here!
        if self.cur_line != (len(self.arr_of_lines)):
            return True
        else:
            self.cur_line = 0
            return False

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        if self.has_more_commands():
            self.cur_line = self.cur_line + 1

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
            "EXTENDED_C_COMMAND" the shift right and left commands
        """
        # Your code goes here!
        cur_line1 = self.arr_of_lines[self.cur_line].replace(" ", "")
        if cur_line1[0] == "@":
            return "A_COMMAND"
        if cur_line1[0] == "(":
            return "L_COMMAND"
        if cur_line1.find(">>") > 0 or cur_line1.find("<<") > 0:
            return "C_EXTENDED_COMMAND"
        else:
            return "C_COMMAND"

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        # Your code goes here!
        if self.command_type() == "A_COMMAND":
            return self.arr_of_lines[self.cur_line].replace("@", "").replace(" ", "")
        else:
            return self.arr_of_lines[self.cur_line].replace("(", "").replace(")", "").strip()

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        # Your code goes here!
        if self.arr_of_lines[self.cur_line].find("=") > 0:
            return self.arr_of_lines[self.cur_line].split("=")[0].strip()
        else:
            return "null"

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        # Your code goes here!
        if self.arr_of_lines[self.cur_line].find("=") < 0:
            return self.arr_of_lines[self.cur_line].split(";")[0].strip()
        return self.arr_of_lines[self.cur_line].split("=")[1].split(";")[0].strip()

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if self.arr_of_lines[self.cur_line].find(";") > 0 and self.arr_of_lines[self.cur_line].find("=") > 0:
            return self.arr_of_lines[self.cur_line].split("=")[1].split(";")[1].strip()

        if self.arr_of_lines[self.cur_line].find(";") > 0 and self.arr_of_lines[self.cur_line].find("=") < 0:
            return self.arr_of_lines[self.cur_line].split(";")[1].strip()
        else:
            return "null"

    def get_ex_c_command(self):
        """
        Returns:
            str: the shift mnemonic in the current C-command. Should be called
            only when commandType() is "C_EXTENDED_COMMAND"
        """
        if self.arr_of_lines[self.cur_line].find("=") < 0:
            return self.arr_of_lines[self.cur_line].split(";")[0].strip()
        return self.arr_of_lines[self.cur_line].split("=")[1].split(";")[0].strip()



