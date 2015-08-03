//    Filename: fill_screen.asm
// Description: Fills the screen with black pixels while any key is held down.
//              While no key is held down, the screen is completely clear.
//      Author: David C. Drake (http://davidcdrake.com)

    @8192
    D=A
    @screenMax
    M=D

(RESET_SCREEN_OFFSET)
    @screenOffset
    M=0

(CLEAR_SCREEN)
    @KBD
    D=M
    @FILL_SCREEN
    D;JNE

    @screenOffset
    D=M
    @SCREEN
    A=A+D
    M=0

    @screenOffset
    M=M+1
    D=M
    @screenMax
    D=D-M
    @RESET_SCREEN_OFFSET
    D;JGE

    @CLEAR_SCREEN
    0;JMP

(FILL_SCREEN)
    @KBD
    D=M
    @CLEAR_SCREEN
    D;JEQ

    @screenOffset
    D=M
    @SCREEN
    A=A+D
    M=-1

    @screenOffset
    M=M+1
    D=M
    @screenMax
    D=D-M
    @RESET_SCREEN_OFFSET
    D;JGE

    @FILL_SCREEN
    0;JMP
