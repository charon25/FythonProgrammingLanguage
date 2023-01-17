# Fython Programming Language

## Working principle

The **Fython** (or "Faux Python") is a programming language which can be hidden in a regular Python code. It works by counting the indentation level and the number of whitespaces of the code. 

More precisely, if you define $I_n$ and $w_n$ ($n \geq 0$) as respectively of indentation level and the number of whitespaces group (so " " is the same as "      ") of every line which is neither empty nor only a comment ; then you can define the "deltas" of the code as :

$\Delta I_n = I_n - I_{n-1}$ and $\Delta w_n = w_n - w_{n-1}$

with $n \geq 1$.

The couple $(\Delta I_n, \Delta w_n)$ is the opcode for the different instructions of the language, and can also define parameters and comments.

### List of instructions

| $\Delta w_n$ | $\Delta I_n = -1$ | $\Delta I_n = 0$ | $\Delta I_n = 1$ |
|:-:|:-:|:-:|:-:|
| 0 |NOP|NOP|NOP|
| 1 |PRINT|comment|PUSH|
| -1 |READ|comment|POP|
| 2 |COPY|comment|ADD|
| -2 |   |comment|SUB|
| 3 |JMPZ|comment|MUL|
| -3 |JMPNZ|comment|DIV|
| 4 |PLACE|comment|MOD|
| -4 |PICK|comment|POW|
| 5 |   |comment|ABS|
| -5 |   |comment|   |
| 6 |   |comment|   |
| -6 |   |comment|   |
| 7 |   |comment|   |
| -7 |   |comment|   |
| 8 |   |comment|   |
| -8 |   |comment|   |
| 9 |   |comment|   |
| -9 |   |comment|   |

Every blank case in this table means a NOP for now, but can be used for a new operation in the future. If $\Delta I_n < -1$, there are no instructions.

If $|\Delta w_n| > 9$ , then $\Delta w_n = sign(\Delta w_n) \cdot (|\Delta w_n| \% 10) $ .

This means that 15 is considered as 5, and -13 as -3.


