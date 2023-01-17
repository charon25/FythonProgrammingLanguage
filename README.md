# Fython Programming Language

## Working principle

The **Fython** (or "Faux Python") is a programming language which can be hidden in a regular Python code. It works by counting the indentation level and the number of whitespaces of the code. 

More precisely, if you define $I_n$ and $w_n$ ($n \geq 0$) as respectively of indentation level and the number of whitespaces group (so " " is the same as "      ") of every line which is neither empty nor only a comment ; then you can define the "deltas" of the code as :

$\Delta I_n = I_n - I_{n-1}$ and $\Delta w_n = w_n - w_{n-1}$

with $n \geq 1$.

The couple $(\Delta I_n, \Delta w_n)$ is the opcode for the different instructions of the language, and can also define parameters and comments.

This is an integer stack-based language, and it also has a zero flag, which is raised or lowered depending on the result of the instructions.

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

### Instructions details

|Instruction|Description|Has a parameter $v$ ?|
|:-:|:-:|:-:|
|NOP|Do nothing.|   |
|PUSH|Add $v$ onto the stack.|The value to add to the stack.|
|POP|Remove the top $v$ values from the stack.|The number of values to remove from the stack.|
|ADD|Pop the top 2 elements of the stack, add them and push the result.| / |
|SUB|Pop the top 2 elements of the stack, subtract the first from the second and push the result.| / |
|MUL|Pop the top 2 elements of the stack, multiply them and push the result.| / |
|DIV|Pop the top 2 elements of the stack, divide (euclidean division) the second by the first and push the quotient.| / |
|MOD|Pop the top 2 elements of the stack, divide (euclidean division) the second by the first and push the rest.| / |
|POW|Pop the top 2 elements of the stack, raise the second to the power of the first and push the result.| / |
|ABS|Pop the top element of the stack and push its absolute value.| / |
|PRINT|Print the top $v$ values of the stack.|Number of value to print.|
|READ|Read $v$ values and add them onto the stack.|Number of value to read.|
|COPY|Pop the top element of the stack, and push $v$ copy of it.|Number of copy to add to the stack.|
|JMPZ|Move the instruction pointer $v$ instruction away (not counting NOP and comments) if the zero flag is set.|Number of instructions to move (can be negative to jump backwards).|
|JMPNZ|Same thing, but if the zero flag is not raised.|Idem|
|PLACE|Pop the top element of the stack and place it at the specified location.|Where to put the element : 0 is at the same place, > 0 is couting down from the top of the stack, < 0 is counting up from the bottom of the stack [-1 is the bottom]).|
|PICK|Pop the element at the specified location and add it onto the stack.|Where to take the element from : 0 is at the same place, > 0 is couting down from the top of the stack, < 0 is counting up from the bottom of the stack [-1 is the bottom]).|
