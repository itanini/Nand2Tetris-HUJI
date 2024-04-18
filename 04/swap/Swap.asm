// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.

// Initialization
	@min
	M=A
	@max
	M=A
	@15
	D=M
	@i
	M=D
	@16384
	D=A
	@minVal
	M=D
	@maxVal
	M=-D
	
//counting iterations of i
	(LOOP)
		@i
		M=M-1
		D=M
		@SWAP
		D;JLT
		
//cur address 
		@14
		A=D+M
		D=M
		
//checks if it is the minimal value so far
		@minVal
		D=D-M
		@SETMIN
		D;JLT

//cur address
	(CONT)
		@i
		D=M
		@14
		A=D+M
		D=M
		
//checks if it is the maximal value so far		
		@maxVal
		D=D-M
		@SETMAX
		D;JGT

		@LOOP
		0;JMP


	(SETMIN)
		@i
		D=M
		@14

//setting the address of the minimal so far to "min"
		A=D+M
		D=A
		@min
		M=D
		
		@i
		D=M
		@14
		A=D+M
		D=M
		
//setting the cur minimal value 
		@minVal
		M=D
		
		@CONT
		0;JMP


	(SETMAX)
		@i
		D=M
		@14
		
//setting the address of the maximal so far to "max"
		A=D+M
		D=A
		@max
		M=D
		
		@i
		D=M
		@14
		A=D+M
		D=M
		
//setting the cur maximal value 
		@maxVal
		M=D
		
		@LOOP
		0;JMP
	
//finally swaping the values 
	(SWAP)
		@minVal
		D=M
		@max
		A=M
		M=D
		
		@maxVal
		D=M
		@min
		A=M
		M=D
		
//endless loop for preventing bugs
	(END)
		@END
		0;JMP