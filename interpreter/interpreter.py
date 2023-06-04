# lisp-interpreter: Scheme interpreter in Python

# (c) Lilike Nel 6/2023
import math
import operator as op

# Types

Symbol = str              # A Scheme Symbol is implemented as a Python str
Number = (int, float)     # A Scheme Number is implemented as a Python int or float
Atom   = (Symbol, Number) # A Scheme Atom is a Symbol or Number
List   = list             # A Scheme List is implemented as a Python list
Exp    = (Atom, List)     # A Scheme expression is an Atom or List
Env    = dict             # A Scheme environment is a mapping of {variable: value}


# Environments

def standard_env() -> Env:
    """
    Create an environment with some Scheme standard procedures.

    Returns:
        Env: The environment with standard procedures.

    """
    env = Env()
    env.update(vars(math))  # Add math functions: sin, cos, sqrt, pi, ...

    env.update({
        '+':op.add, '-':op.sub, '*':op.mul, '/':op.truediv, 
        '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq, 
        'abs':     abs,
        'append':  op.add,  
        'apply':   lambda proc, args: proc(*args),
        'begin':   lambda *x: x[-1],
        'car':     lambda x: x[0],
        'cdr':     lambda x: x[1:],
        'cddr':    lambda x: x[2:],
        'cons':    lambda x,y: [x] + y,
        'eq?':     op.is_, 
        'expt':    pow,
        'equal?':  op.eq, 
        'length':  len, 
        'list':    lambda *x: List(x), 
        'list?':   lambda x: isinstance(x, List), 
        'map':     map,
        'max':     max,
        'min':     min,
        'not':     op.not_,
        'null?':   lambda x: x == [], 
        'number?': lambda x: isinstance(x, Number),  
		'print':   print,
        'procedure?': callable,
        'round':   round,
        'symbol?': lambda x: isinstance(x, Symbol),
    })
    return env


class Env(dict):
    """
    An environment: a dict of {'var': val} pairs, with an outer Env.

    """
    def __init__(self, parms=(), args=(), outer=None):
        """
        Initialize the environment with parameter-value pairs and an outer environment.

        Args:
            parms (tuple): The parameter names.
            args (tuple): The corresponding argument values.
            outer (Env, optional): The outer environment. Defaults to None.
        """
        self.update(zip(parms, args))
        self.outer = outer

    def find(self, var):
        """
        Find the innermost Env where var appears (lexical scoping).

        Args:
            var (str): The variable name to find.

        Returns:
            Env: The innermost environment where the variable is found.
        """
        if var in self:
            return self
        elif self.outer is not None:
            return self.outer.find(var)
        else:
            raise NameError(f'Variable {var} is not defined.')


global_env = standard_env()


# Procedures

class Procedure(object):
    """
    A user-defined Scheme procedure.

    """
    def __init__(self, parms, body, env):
        """
        Initialize the user-defined procedure.

        Args:
            parms (tuple): The parameter names of the procedure.
            body (Exp): The body of the procedure.
            env (Env): The environment in which the procedure is defined.
        """
        self.parms, self.body, self.env = parms, body, env

    def __call__(self, *args):
        """
        Call the user-defined procedure with the given arguments.

        Args:
            *args: Variable number of arguments passed to the procedure.

        Returns:
            Exp: The result of evaluating the body of the procedure in a new environment.
        """
        return eval(self.body, Env(self.parms, args, self.env))


# Parsing

def tokenize(chars: str) -> list:
    """
    Tokenize a string of characters into a list of tokens.

    Args:
        chars (str): The string of characters to be tokenized.

    Returns:
        list: The list of tokens.

    """
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()


def parse(program: str) -> Exp:
    """
    Parse a Scheme expression from a string.

    Args:
        program (str): The string containing the Scheme expression.

    Returns:
        Exp: The parsed expression.

    """
    return read_from_tokens(tokenize(program))


def atom(token: str) -> Atom:
    """
    Convert a token into an atomic expression (atom).

    Args:
        token (str): The token to be converted.

    Returns:
        Atom: The converted atomic expression.

    """
    try:
        # Try converting the token to an integer.
        return int(token)
    except ValueError:
        try:
            # If the conversion to an integer fails, try converting the token to a float.
            return float(token)
        except ValueError:
            # If both conversions fail, the token is considered a symbol.
            return Symbol(token)


def read_from_tokens(tokens: list) -> Exp:
    """
    Read an expression from a sequence of tokens.

    Args:
        tokens (list): The sequence of tokens representing an expression.

    Returns:
        Exp: The expression read from the tokens.

    Raises:
        SyntaxError: If there is a syntax error or unexpected token.

    """
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF')

    token = tokens.pop(0)

    if token == '(':
        # If the token is '(', it indicates the start of a nested expression.
        # Recursively read the tokens until the corresponding ')' is found.
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))
        tokens.pop(0)  # pop off ')'
        return L

    elif token == ')':
        # If the token is ')', it is unexpected and raises a SyntaxError.
        raise SyntaxError('unexpected )')

    else:
        # If the token is neither '(' nor ')', it is an atomic expression (atom).
        # Return the atom by converting the token to the appropriate type.
        return atom(token)


# eval

def eval(x: Exp, env=global_env) -> Exp:
    """
    Evaluate an expression in an environment.

    Args:
        x (Exp): The expression to be evaluated.
        env (dict, optional): The environment in which the expression is evaluated.
            Defaults to global_env.

    Returns:
        Exp: The result of evaluating the expression.

    """
    if isinstance(x, Symbol):
        # If x is a Symbol, it is treated as a variable reference.
        # Return the corresponding value from the environment.
        return env.find(x)[x]

    elif not isinstance(x, List):
        # If x is a Number, it is considered a constant number.
        # A constant should evaluate to itself, so return x.
        return x

    # As x is not a Symbol or a constant, we can assume it is a list
    operator, *args = x

    if operator == "quote":
        return args[0]
    
    elif operator == 'if':
        # If the first element of x is 'if', it is a conditional expression.
        # Unpack the values from args and evaluate the test expression.
        (test_expression, consequent_expression, alternative_expression) = args

        # Determine which branch to evaluate based on the test expression.
        result_expression = (consequent_expression if eval(test_expression, env) else alternative_expression)

        # Recursively evaluate the resulting expression and return the result.
        return eval(result_expression, env)

    elif operator == 'define':
        # If the first element of x is 'define', it is a definition.
        # Unpack the values from args and evaluate the expression.
        (symbol, expression) = args

        # Evaluate the expression and store the result in the environment with symbol as the key.
        env[symbol] = eval(expression, env)

    elif operator == "set!":
        # Handle the 'set!' operator for variable assignment.
        (symbol, expression) = args

        # Evaluate the expression and update the result in the environment with symbol as the key.
        env.find(symbol)[symbol] = eval(symbol, env)

    elif operator == "lambda":
        # Handle the 'lambda' operator for creating a lambda procedure.
        (parameters, body) = args

        return Procedure(parameters, body, env)
    
    elif operator == "display":
        # Handle the 'display' operator for printing strings.
        string = args

        return string

    else:
        # If none of the above conditions are met, it is a procedure call.
        # Evaluate the procedure and the arguments, and call the procedure with the evaluated arguments.
        procedure = eval(operator, env)
        vals = [eval(arg, env) for arg in args]
        return procedure(*vals)


# REPL

def lispstr(exp):
    """
    Convert a Python object back into a Lisp-readable string.

    Args:
        exp (object): The Python object to be converted.

    Returns:
        str: The Lisp-readable string representation of the object.

    """
    if isinstance(exp, List):
        return '(' + ' '.join(map(lispstr, exp)) + ')' 
    else:
        return str(exp)


def repl(prompt='lisp-interpreter> '):
    """
    A prompt-read-eval-print loop.

    Args:
        prompt (str, optional): The prompt string. Defaults to 'lisp-interpreter> '.

    """
    while True:

        val = eval(parse(input(prompt)))

        if val is not None:
            print(lispstr(val))


if __name__ == "__main__":

    repl()
