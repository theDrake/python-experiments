//    Filename: multiply.asm
// Description: Stores the value of R0 * R1 into R2.
//      Author: David C. Drake (https://davidcdrake.com)

    @R2
    M=0
    @R0
    D=M
    @END
    D;JLE
    @R1
    D=M
    @END
    D;JLE
(LOOP)
    @R0
    D=M
    @R2
    M=D+M
    @R1
    MD=M-1
    @END
    D;JLE
    @LOOP
    0;JMP

(END)
    @END
    0;JMP
