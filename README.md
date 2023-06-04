# lisp-interpreter
A simple LISP interpreter written in Python.

## Introduction

This Lisp Interpreter is capable of evaluating Scheme expressions and executing Scheme programs. It supports a subset of the Scheme language and provides standard procedures, lexical scoping, conditionals, variable assignment, lambda expressions, and more.

## Usage

To use the Lisp Interpreter, you can follow these steps:

1. Make sure you have Python installed on your system (version 3.6 or higher).
2. Clone or download the code repository.
3. Open a terminal or command prompt and navigate to the project directory.
4. Run the interpreter by executing the following command:
   python interpreter.py
5. Once the interpreter is running, you can enter Scheme expressions or programs at the prompt (lisp-interpreter>) and press Enter to evaluate them.
6. The interpreter will display the result of the evaluation.

## Supported Features
The Lisp Interpreter supports the following features:

- Evaluation of atomic expressions (Symbols and Numbers).
- Evaluation of lists as expressions.
- Arithmetic operations (+, -, *, /).
- Comparison operations (>, <, >=, <=, =).
- Mathematical functions (sin, cos, sqrt, pi, etc. from the math module).
- Logical operations (not).
- Conditional expressions (if).
- Variable assignment (define, set!).
- Lambda expressions (lambda).
- Procedure calls.
- Printing expressions (print).
- Standard procedures and functions (abs, append, apply, begin, car, cdr, cddr, cons, eq?, expt, equal?, length, list, list?, map, max, min, null?, number?, procedure?, round, symbol?).

## Example Usage
Here's an example of using the Lisp Interpreter:

lisp-interpreter> (+ 1 2)
3
lisp-interpreter> (define radius 5)
lisp-interpreter> (* pi (* radius radius))
78.53981633974483
lisp-interpreter> (number? radius)
True

## Acknowledgments
The implementation of this Lisp Interpreter is based heavily on Peter Norvig's lis.py, see http://norvig.com/lispy.html

## License
This project is licensed under the GNU General Public License.
