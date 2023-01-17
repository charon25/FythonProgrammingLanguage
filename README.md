# Fython Programming Language & Interpreter

## Working principle

The **Fython** (or "Faux Python") is a programming language which can be hidden in a regular Python code. It works by counting the indentation level and the number of whitespaces of the code. 

More precisely, if you define $I_n$ and $w_n$ ($n \geq 0$) as respectively of indentation level and the number of whitespaces group (so " " is the same as "      ") of every line which is neither empty nor only a comment ; then you can define the "deltas" of the code as :

$\Delta I_n = I_n - I_{n-1}$ and $\Delta w_n = w_n - w_{n-1}$

with $n \geq 1$.

The couple $(\Delta I_n, \Delta w_n)$ is the opcode for the different instructions of the language, and can also define parameters and comments.

This is an integer stack-based language, and it also has a zero flag, which is raised or lowered depending on the result of the instructions. It is also designed to have as few runtime errors as possible. In practice, only dividing by 0 will stop the execution of the program.

### List of instructions

| $\Delta w$ | $\Delta I = -1$ | $\Delta I = 0$ | $\Delta I = 1$ |
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

Every blank case in this table means a NOP for now, but can be used for a new operation in the future. If $\Delta I < -1$ , there are no instructions.

If $|\Delta w| > 9$ , then $\Delta w = sign(\Delta w) \cdot (|\Delta w_n| \% 10) $ .

This means that 15 is considered as 5, and -13 as -3.

### Instructions details

|Instruction|Description|Has a parameter $v$ ?|Stack does not have enough elements ?|Invalid $v$ |
|:-:|:-:|:-:|:-:|:-:|
|NOP|Do nothing.| / | / | / |
|PUSH|Add $v$ onto the stack.|The value to add to the stack.| / | / |
|POP|Remove the top $v$ values from the stack.|The number of values to remove from the stack.|Remove as much as possible then raise zero flag.|$v \leq 0$ : do nothing.|
|ADD|Pop the top 2 elements of the stack, add them and push the result.| / |ADD(x, n) = n <br> ADD(x, x) = 0| / |
|SUB|Pop the top 2 elements of the stack, subtract the first from the second and push the result.| / |SUB(x, n) = -n <br> SUB(x, x) = 0| / |
|MUL|Pop the top 2 elements of the stack, multiply them and push the result.| / |MUL(x, n) = 0 <br> MUL(x, x) = 0| / |
|DIV|Pop the top 2 elements of the stack, divide (euclidean division) the second by the first and push the quotient.| / |DIV(x, n) = 0 <br> DIV(x, x) = 0| / |
|MOD|Pop the top 2 elements of the stack, divide (euclidean division) the second by the first and push the rest.| / |MOD(x, n) = 0 <br> MOD(x, x) = 0| / |
|POW|Pop the top 2 elements of the stack, raise the second to the power of the first and push the result.| / |POW(x, n) = 1 <br> POW(x, x) = 1| / |
|ABS|Pop the top element of the stack and push its absolute value.| / |ABS(x) = 0| / |
|PRINT|Print the top $v$ values of the stack.|Number of value to print.|Do nothing.|$v \leq 0$ : do nothing.|
|READ|Read $v$ values and add them onto the stack.|Number of value to read.| / |$v \leq 0$ : do nothing.|
|COPY|Pop the top element of the stack, and push $v$ copy of it.|Number of copy to add to the stack.|Copy 0|$v \leq 0$ : pop the last value without adding it back.|
|JMPZ|Move the instruction pointer $v$ instruction away (not counting NOP and comments) if the zero flag is set.|Number of instructions to move (can be negative to jump backwards).| / |$v = 0$ : go the next instruction.|
|JMPNZ|Same thing, but if the zero flag is not raised.|Idem.| / |$v = 0$ : go the next instruction.|
|PLACE|Pop the top element of the stack and place it at the specified location.|Where to put the element : 0 is at the same place, > 0 is couting down from the top of the stack, < 0 is counting up from the bottom of the stack [-1 is the bottom]).|Add 0 to the stack.| / |
|PICK|Pop the element at the specified location and add it onto the stack.|Where to take the element from : 0 is at the same place, > 0 is couting down from the top of the stack, < 0 is counting up from the bottom of the stack [-1 is the bottom]).|Add 0 to the stack.| / |

### Describing a parameter

A parameter $v$ needed by an instruction is described as a sequence of deltas with $\Delta I = 0$. Then, the different $\Delta w$ describes the digits of the parameter in base 10. Additionally, to denote a negative number, the sequence must start with $\Delta w = 0$ . However, if the sequence consists only of $(\Delta I, \Delta w) = (0, 0)$ , then the parameter will be 0. Finally, if a negative number is passed as a digit, then 10 is added to it (i.e. -3 is 7). Below are some examples of delta tuples :

123 : (0, 1) (0, 2) (0, 3)
-123 : (0, 0) (0, 1) (0, 2) (0, 3)
987 : (0, 9) (0, 8) (0, 7)
987 : (0, -1) (0, -2) (0, -3)
0 : (0, 0)

### Zero flag

The zero flag is affected by every instruction except NOP, JMPZ and JMPNZ. It is raised at the start of the program. 

Mathematical instructions raise it according to the result of the operation.
PUSH, POP and COPY raise it according to the last value added to or removed from the stack.
READ and PRINT raise it according to the last value read from or written to the stack.
PLACE and PICK raise it according to the moved value.

### POW instruction details

Let's define three integers : $n \in \mathbb{Z}$, $p \geq 0$ and $m > 0$. Then :

POW(n, p) = $n^p$ (usual definition)
POW(0, 0) = 1
POW(0, -m) is a runtime error, stopping the execution.
POW(n, -m) = DIV(1, pow(n, m))

### Comments

A comment is started with a delta containing $\Delta I = 0$ and $\Delta w \neq 0$ . If $\Delta w > 0$, then the next $\Delta w$ deltas are ignored. If $\Delta w < 0$ , then every deltas until another $\Delta w < 0$ are ignored.
This means a comment cannot occur after an instruction needing a parameter or after a parameter.

## Interpreter

## Examples
