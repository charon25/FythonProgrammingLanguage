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

|Instruction|Description|Has a parameter $v$ ?|Stack does not have enough elements ?|Invalid $v$ |Default value ($v$ not specified)|
|:-:|:-:|:-:|:-:|:-:|:-:|
|NOP|Do nothing.| / | / | / | / |
|PUSH|Add $v$ onto the stack.|The value to add to the stack.| / | / | 0 |
|POP|Remove the top $v$ values from the stack.|The number of values to remove from the stack.|Remove as much as possible then raise zero flag.|$v \leq 0$ : do nothing.| 1 |
|ADD|Pop the top 2 elements of the stack, add them and push the result.| / |ADD(x, n) = n <br> ADD(x, x) = 0| / | / |
|SUB|Pop the top 2 elements of the stack, subtract the first from the second and push the result.| / |SUB(x, n) = -n <br> SUB(x, x) = 0| / | / |
|MUL|Pop the top 2 elements of the stack, multiply them and push the result.| / |MUL(x, n) = 0 <br> MUL(x, x) = 0| / | / |
|DIV|Pop the top 2 elements of the stack, divide (euclidean division) the second by the first and push the quotient.| / |DIV(x, n) = 0 <br> DIV(x, x) = 0| / | / |
|MOD|Pop the top 2 elements of the stack, divide (euclidean division) the second by the first and push the rest.| / |MOD(x, n) = 0 <br> MOD(x, x) = 0| / | / |
|POW|Pop the top 2 elements of the stack, raise the second to the power of the first and push the result.| / |POW(x, n) = 1 <br> POW(x, x) = 1| / | / |
|ABS|Pop the top element of the stack and push its absolute value.| / |ABS(x) = 0| / | / |
|PRINT|Print the top $v$ values of the stack.|Number of value to print.|Do nothing.|$v \leq 0$ : do nothing.| 1 |
|READ|Read $v$ values and add them onto the stack.|Number of value to read.| / |$v \leq 0$ : do nothing.| 1 |
|COPY|Pop the top element of the stack, and push $v$ copy of it.|Number of copy to add to the stack.|Copy 0|$v \leq 0$ : pop the last value without adding it back.| 2 |
|JMPZ|Move the instruction pointer $v$ instruction away (not counting NOP and comments) if the zero flag is set.|Number of instructions to move (can be negative to jump backwards).| / |$v = 0$ : go the next instruction.| 1 |
|JMPNZ|Same thing, but if the zero flag is not raised.|Idem.| / |$v = 0$ : go the next instruction.| 1 |
|PLACE|Pop the top element of the stack and place it at the specified location.|Where to put the element : 0 is at the same place, > 0 is couting down from the top of the stack, < 0 is counting up from the bottom of the stack [-1 is the bottom]).|Add 0 to the stack.| / | 1 |
|PICK|Pop the element at the specified location and add it onto the stack.|Where to take the element from : 0 is at the same place, > 0 is couting down from the top of the stack, < 0 is counting up from the bottom of the stack [-1 is the bottom]).|Add 0 to the stack.| / | 1 |

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

This repo contains an interpreter for this language. During execution from the Fython code (which is really Python code), it converts it first to a list of deltas, then to a pseudo-assembly which only contains the instructions and their parameters. This assembly is then executed. 

This means the interpreter can output to any of this formats instead of executing the code, and can accept deltas or assembly to execute them, making it easier to create a working code.

### Usage

Once cloned, the interpreter is used with the following command :

```
python main.py <input file path> [output file path] [--input-type {p,d,a}] [--output-type {d,a,e}] [--program-input PROGRAM_INPUT] [--program-output PROGRAM_OUTPUT] [--format {char,number}]
```

Where the parameters are :
 - `input file path` : mandatory argument containing the input of the interpreter (either Fython, deltas or assembly) ;
 - `output file path` : the output of the interpreter, mandatory if the code is not executed, but outputted to another format ;
 - `--input-type` (or `-i`) : the type of the input. Either `p` for a Fython/Python code (default), `d` for a list of deltas or `a` for assembly ;
 - `--output-type` (or `-o`) : the type of the output. Either `d` for the list of deltas, `a` for the assembly or `e` to execute the code (default) ;
 - `--program-input` (or `-I`) : if the program is executed, where it should look for its input. If not provided, will use stdin ;
 - `--program-output` (or `-O`) : if the program is executed, where it should print its output. If not provided, will use stdout ;
 - `--format` (or `-f`) : if the program is executed, the format of the output and input. Either `char` (default) to print and read ASCII characters, or `number` to print and read base 10 numbers.

**Important note** : when the input is a Fython code, the underlying Python code should be at least syntactically correct, or the interpreter will stop execution.

### Formats table

This table sums up the different format combinations. The empty set marks the default behavior.

|Input \ Output|Fython|Deltas|Assembly|Execution|
|:-:|:-:|:-:|:-:|:-:|
|Fython| X | `-o d` | `-o a` | $\emptyset$ |
|Deltas| X | `-i d -o d` | `-i d -o a` | `-i d` |
|Assembly| X |  `-i a -o d` | `-i a -o a` | `-i a` |
|Execution| X | X | X | X |

### Delta input format

When the input is a list of deltas, it should respect the regex : 
```regex
(-?[0-9]+)[^0-9-]+(-?[0-9]+)
```
This means two numbers, possibly negative, separated by anything other than digits or dashes. Everything which is not of this format will be considered a comment.

### Assembly input format

The interpreter will match as an instruction anything respecting one of those regexes :
```regex
^\s*([a-z]+)
^\s*([a-z]+)\s*(-?[0-9]+)
```
This means any number of whitespace after the start of the line, followed by lower case letters, then optionally whitespaces and a number, possibly negative. This means everything not starting with a letter will be considered a comment.
However, default value will not be considered contrary to Fython or deltas input, meaning e.g. a line just containing `push` will stop the execution.

### Formats example

All the formats are taken from the `test_files` folder.

Fython code :
```python
a= 2
if a:
    a = 3
    b = "This is a very long" * a
    print(b, sep=" ", end="")
a = len(b) * 2
```

The equivalent deltas :

```txt
di	dw
0	0
1	1
0	6
0	-5
-1	1
```

The equivalent pseudo-assembly :

```txt
push 65
print 1
```

And the output of the intrepreter :

```bash
> python main.py test_files\python.py
Program execution:
==========
A
==========
Execution complete!
```

Finally, if converting from assembly to deltas, the instruction corresponding to the deltas will be printed in comments around it :
```txt
di	dw

# push 65	
1	1
0	6
0	5

# print 1	
-1	1
0	1
```

## Examples

Writing a Fython program (directly in real Python code) is actually quite difficult, which means the examples have been written in the assembly format directly (the corresponding deltas can be found next to them in the `examples` folder).

**Hello, world!**
```txt
push 33
push 100
push 108
push 114
push 111
push 119
push 32
push 44
push 111
push 108
push 108
push 101
push 72

print 13
```

**Fibonacci sequence** (the input is the number $N$ of terms to print)

```txt
    # Read number of terms N
read 1
push 1
add
    # Initialization with a=0 and b=1
push 0
push 1
    # N = N - 1, and check if N == 0
pick -1
push 1
sub
    # If yes, end of the program
jmpz 7
    # a, b = b, a + b
place -1
copy 3
print 1
pick -2
add
    # Loop
jmpnz -13
```

Output :
```bash
> python main.py examples\fibonacci_assembly.txt -i a -f number
Program execution:
==========
10
1
1
2
3
5
8
13
21
34
55

==========
Execution complete!
```

**Primes** (the input is the number $M$ of number to check for primeness)

```txt
    # M
read 1
push 1
add
    # N
push 2
    # check if N = M
copy 2
pick 2
copy 2
pick 3
sub
pop 1
    # if yes, finished
jmpz 35
    # duplicate i to work on it with the prime algorithm
pick 1
copy 2

    == CHECK IF PRIME
	# d
push 2

	# check if d = N
copy 2
pick 2
copy 2
pick 3
sub
pop 1
    # if yes, not prime
jmpz 15
	# N % d
copy 2
pick 2
copy 2
place 3
mod
pop 1
	# if N % d = 0, not prime
jmpz 5
	# else, increment i
pick 1
push 1
add 1

	# not prime and not finished
jmpnz -17

	# not prime
pop 2
push 0
jmpz 3
	# prime
pop 2
push 1

    # if N was prime, print it
pop 1
jmpnz 2
jmpz 3
copy 2
print 1

    # increment N and jump back to top
push 1
add
jmpnz -40
```

Output :
```bash
> python main.py examples\primes_assembly.txt -i a -f number
Program execution:
==========
100
2
3
5
7
11
13
17
19
23
29
31
37
41
43
47
53
59
61
67
71
73
79
83
89
97

==========
Execution complete!
```
