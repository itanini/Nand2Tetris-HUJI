"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import os


class CodeWriter:
    """Translates VM commands into Hack assembly code."""
    label_counter = 0

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.static_command_counter = 0
        self.output_stream = output_stream
        base_name = os.path.basename(str(output_stream))
        self.filename = os.path.splitext(base_name)[0]
        CodeWriter.label_counter = 0
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")

    def set_file_name(self, filename: str) -> None:   # no clue what i have done here
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        # This function is useful when translating code that handles the
        # static segment. For example, in order to prevent collisions between two
        # .vm files which push/pop to the static segment, one can use the current
        # file's name in the assembly variable's name and thus differentiate between
        # static variables belonging to different files.
        # To avoid problems with Linux/Windows/MacOS differences with regards
        # to filenames and paths, you are advised to parse the filename in
        # the function "translate_file" in Main.py using python's os library,
        # For example, using code similar to:
        self.output_stream.write("//translation of "+filename + " start\n")

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given 
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        self.output_stream.write("//" + command+"\n")  # for knowing which command are we in right now
        if command == "add":
            self.output_stream.write("@SP\nAM=M-1\nD=M\nA=A-1\nM=M+D\n")
        if command == "neg":
            self.output_stream.write("@0\nD=A\n@SP\nA=M-1\nM=D-M\n")
        if command == "sub":
            self.output_stream.write("@SP\nAM=M-1\nD=M\nA=A-1\nM=M-D\n")
        if command == "eq":
            s = str(self.label_counter)
            self.output_stream.write(f"""
        @SP // Assuming SP is 258 pointing to nothing
        AM=M-1 // A is 257, SP=257
        D=M // D = Y
        A=A-1 // A is 256
        D=M-D // D = X - Y
        @EQ{s}
        D;JEQ // Jump to EQ if X - Y equal 0
        @SP // case 1: X - Y is not equal 0
        A=M-1 // A is 256
        M=0
        @END{s}
        0;JMP
        (EQ{s}) // case 2: X equals Y
        @SP
        A=M-1
        M=-1
        (END{s})
        """)
            self.label_counter += 1

        if command == "lt":
            s = str(self.label_counter)
            self.output_stream.write(f"""
                  @SP // Assuming SP is 258 pointing to nothing
                  AM=M-1 // A is 257, SP=257
                  A=A-1 // A is 256
                  D=M // D = X
                  @X_POSITIVE{s}
                  D;JGT // Jump to X_POSITIVE if X is greater than 0
                  @SP // X is non-positive
                  A=M // Get Y
                  D=M
                  @SAME_SIGN{s}
                  D;JLT // Jump to SAME_SIGN if Y is negative
                  @SP // Case 1: Y is non-negative and X is non-positive - True
                  A=M-1 // A is 256
                  M=-1
                  @END{s}
                  0;JMP
                  (X_POSITIVE{s})
                  @SP // Check if Y is non-negative
                  A=M // Get Y
                  D=M
                  @SAME_SIGN{s}
                  D;JGT // Jump to SAME_SIGN if Y is greater than 0
                  @SP // Case 2: X is non-negative and Y is non-positive - False
                  A=M-1 // A is 256
                  M=0
                  @END{s}
                  0;JMP
                  (SAME_SIGN{s})
                  @SP // Case 3 and 4: X and Y have the same sign
                  A=M // A is 257
                  D=M // D = Y
                  A=A-1 // A is 256
                  D=M-D // D = X - Y
                  @LT{s}
                  D;JLT // Jump to LT if X is less than Y
                  @SP // Case 3: X is greater than or equal to Y - False
                  A=M-1
                  M=0
                  @END{s}
                  0;JMP
                  (LT{s}) // Case 4: X is less than Y - True
                  @SP
                  A=M-1
                  M=-1
                  (END{s})
                  """)
            self.label_counter += 1

        if command == "gt":
            s = str(self.label_counter)
            self.output_stream.write(f"""@SP //assuming sp is 258 pointing nothing 
              AM=M-1 // A is 257, SP=257
              A=A-1 // A is 256
              D=M // D=X
              @X_POSITIVE{s} 
              D;JGT
              @SP // X is negative 
              A=M // getting Y
              D=M
              @SAME_SIGN{s} 
              D;JLT //asking if Y negative
              @SP // case 1: Y is positive and X is negative - False.
              A=M-1 // A is 256
              M=0
              @END{s} 
              0;JMP 
              (X_POSITIVE{s})
              @SP // checking if Y is positive
              A=M // getting Y
              D=M
              @SAME_SIGN{s}
              D;JGT
              @SP // case 2: if X is positive and Y is negative - True
              A=M-1 // A is 256
              M=-1
              @END{s}
              0;JMP
              (SAME_SIGN{s})
              @SP // case 3 and 4: X and Y have same sign
              A=M //  A is 257 
              D=M // D=Y
              A=A-1 // A is 256
              D=M-D // D=X-Y
              @LT{s} 
              D;JLE //sub is little or equals 0
              @SP // X is greater than Y
              A=M-1
              M=-1
              @END{s}
              0;JMP
              (LT{s}) // case 4: X is little than Y
              @SP
              A=M-1
              M=0
              (END{s})
              """)
            self.label_counter += 1

        if command == "and":
            self.output_stream.write("@SP\nAM=M-1\nD=M\nA=A-1\nM=D&M\n")
        if command == "or":
            self.output_stream.write("@SP\nAM=M-1\nD=M\nA=A-1\nM=D|M\n")
        if command == "not":
            self.output_stream.write("@SP\nA=M-1\nM=!M\n")
        if command == "shiftleft":
            self.output_stream.write("@SP\nA=M-1\nM=M<<\n")
        if command == "shiftright":
            self.output_stream.write("@SP\nA=M-1\nM=M>>\n")

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # Your code goes here!
        # Note: each reference to "static i" appearing in the file Xxx.vm should
        # be translated to the assembly symbol "Xxx.i". In the subsequent
        # assembly process, the Hack assembler will allocate these symbolic
        # variables to the RAM, starting at address 16.

        # writing the name of the command before:
        command_comment = "//" + command + " " + segment + " " + str(index) + "\n"
        self.output_stream.write(command_comment)

        # push commands:
        if command == "C_PUSH":
            if segment == "local":
                self.output_stream.write("@" + str(index) + "\nD=A\n@LCL\nA=D+M\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n")
            if segment == "argument":
                self.output_stream.write("@" + str(index) + "\nD=A\n@ARG\nA=D+M\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n")
            if segment == "this":
                self.output_stream.write("@" + str(index) + "\nD=A\n@THIS\nA=D+M\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n")
            if segment == "that":
                self.output_stream.write("@" + str(index) + "\nD=A\n@THAT\nA=D+M\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n")
            if segment == "temp":
                self.output_stream.write("@" + str(index) + "\nD=A\n@R5\nA=D+A\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n")
            if segment == "constant":
                self.output_stream.write("@" + str(index) + "\nD=A\n@SP\nM=M+1\nA=M-1\nM=D\n")
            if segment == "static":
                self.output_stream.write("@" + self.filename + "." + str(index) + "\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n")
            if segment == "pointer":
                self.output_stream.write(f"@R{3+index}\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n")

        # pop commands:
        if command == "C_POP":
            if segment == "local":
                self.output_stream.write("@" + str(index) +
                                         "\nD=A\n@LCL\nD=D+M\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n")
            if segment == "argument":
                self.output_stream.write("@" + str(index) +
                                         "\nD=A\n@ARG\nD=D+M\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n")
            if segment == "this":
                self.output_stream.write("@" + str(index) +
                                         "\nD=A\n@THIS\nD=D+M\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n")
            if segment == "that":
                self.output_stream.write("@" + str(index) +
                                         "\nD=A\n@THAT\nD=D+M\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n")
            if segment == "temp":
                self.output_stream.write("@" + str(index) +
                                         "\nD=A\n@R5\nD=D+A\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n")
            if segment == "static":
                self.output_stream.write("@SP\nAM=M-1\nD=M\n" + "@" + self.filename + "." + str(index) + "\nM=D\n")
            if segment == "pointer":
                self.output_stream.write(f"@SP\nAM=M-1\nD=M\n@R{str(3+index)}\nM=D\n")

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command. 
        Let "Xxx.foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "Xxx.foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        command_comment = "//write label " + label + "\n"
        self.output_stream.write(command_comment)

        self.output_stream.write("(" + self.filename + "." + "$" + label + ")\n")
    
    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        command_comment = "//write goto " + label + "\n"
        self.output_stream.write(command_comment)

        self.output_stream.write("@" + self.filename + "." + "$" + label + "\n0;JMP\n")
    
    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        command_comment = "//write if goto " + label + "\n"
        self.output_stream.write(command_comment)

        label_goto = "@" + self.filename + "." + "$" + label + "\n"
        self.output_stream.write("@SP\nAM=M-1\nD=M\n" + label_goto + "D;JNE\n")

    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command. 
        The handling of each "function Xxx.foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this 
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "function function_name n_vars" is:
        # (function_name)       // injects a function entry label into the code
        # repeat n_vars times:  // n_vars = number of local variables
        #   push constant 0     // initializes the local variables to 0
        pass
    
    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command. 
        Let "Xxx.foo" be a function within the file Xxx.vm.
        The handling of each "call" command within Xxx.foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "Xxx.foo").
        This symbol is used to mark the return address within the caller's 
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "call function_name n_args" is:
        # push return_address   // generates a label and pushes it to the stack
        # push LCL              // saves LCL of the caller
        # push ARG              // saves ARG of the caller
        # push THIS             // saves THIS of the caller
        # push THAT             // saves THAT of the caller
        # ARG = SP-5-n_args     // repositions ARG
        # LCL = SP              // repositions LCL
        # goto function_name    // transfers control to the callee
        # (return_address)      // injects the return address label into the code
        pass
    
    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "return" is:
        # frame = LCL                   // frame is a temporary variable
        # return_address = *(frame-5)   // puts the return address in a temp var
        # *ARG = pop()                  // repositions the return value for the caller
        # SP = ARG + 1                  // repositions SP for the caller
        # THAT = *(frame-1)             // restores THAT for the caller
        # THIS = *(frame-2)             // restores THIS for the caller
        # ARG = *(frame-3)              // restores ARG for the caller
        # LCL = *(frame-4)              // restores LCL for the caller
        # goto return_address           // go to the return address
        pass
