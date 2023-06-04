import math
import operator as op

Symbol = str              # A Scheme Symbol is implemented as a Python str
Number = (int, float)     # A Scheme Number is implemented as a Python int or float
Atom   = (Symbol, Number) # A Scheme Atom is a Symbol or Number
List   = list             # A Scheme List is implemented as a Python list
Exp    = (Atom, List)     # A Scheme expression is an Atom or List
Env    = dict             # A Scheme environment is a mapping of {variable: value}


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

global_env = standard_env()


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
        return env[x]

    elif isinstance(x, Number):
        # If x is a Number, it is considered a constant number.
        # A constant should evaluate to itself, so return x.
        return x

    elif x[0] == 'if':
        # If the first element of x is 'if', it is a conditional expression.
        # Unpack the values from x and evaluate the test expression.
        (_if, test_expression, consequent_expression, alternative_expression) = x

        # Determine which branch to evaluate based on the test expression.
        result_expression = (consequent_expression if eval(test_expression, env) else alternative_expression)

        # Recursively evaluate the resulting expression and return the result.
        return eval(result_expression, env)

    elif x[0] == 'define':
        # If the first element of x is 'define', it is a definition.
        # Unpack the values from x and evaluate the expression.
        (_define, symbol, expression) = x

        # Evaluate the expression and store the result in the environment with symbol as the key.
        env[symbol] = eval(expression, env)

    else:
        # If none of the above conditions are met, it is a procedure call.
        # Evaluate the procedure and the arguments, and call the procedure with the evaluated arguments.
        procedure = eval(x[0], env)
        args = [eval(arg, env) for arg in x[1:]]
        return procedure(*args)
