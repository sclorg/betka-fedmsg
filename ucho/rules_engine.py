import re
import ast
import _ast
import logging
from ucho.utils import UchoError


class UchoRulesError(UchoError):
    """
    Base class of rules-related soft exceptions.

    :param str message: descriptive message, passed to parent Exception classes.
    :param Rules rules: rules in question.
    :param str intro: introductory text, pasted at the beginning of template.
    :param str error: specific error message.
    """

    def __init__(self, message, rules, intro, error):
        super(UchoRulesError, self).__init__(message)

        self.rules = rules
        self.intro = intro
        self.error = error


class InvalidASTNodeError(UchoRulesError):
    def __init__(self, rules, node):
        super(InvalidASTNodeError, self).__init__(
            "It is not allowed to use '{}' in rules".format(node.__class__.__name__),
            rules,
            'Dangerous and disallowed node used in rules',
            "It is not allowed to use '{}' in rules.".format(node.__class__.__name__))


class RulesSyntaxError(UchoRulesError):
    def __init__(self, rules, exc):
        super(RulesSyntaxError, self).__init__(
            'Cannot parse rules',
            rules,
            "Cannot parse rules '{}'".format(rules),
            'Position {}:{}: {}'.format(exc.lineno, exc.offset, exc))


class RulesTypeError(UchoRulesError):
    def __init__(self, rules, exc):
        super(RulesTypeError, self).__init__(
            'Cannot parse rules',
            rules,
            "Cannot parse rules '{}'".format(rules),
            str(exc))


class RulesASTVisitor(ast.NodeTransformer):
    """
    Custom AST visitor, making sure no disallowed nodes are present in the rules' AST.
    """

    _valid_classes = tuple([
        getattr(_ast, node_class) for node_class in (
            'Expression', 'Expr', 'Compare', 'Name', 'Load', 'BoolOp', 'UnaryOp', 'USub',
            'Constant', 'List', 'Tuple', 'Dict',
            'Subscript', 'Index', 'ListComp', 'comprehension',
            'Store',
            'Eq', 'NotEq', 'Lt', 'LtE', 'Gt', 'GtE', 'Is', 'IsNot', 'In', 'NotIn',
            'And', 'Or', 'Not',
            'Attribute', 'Call'
        )
    ])

    def __init__(self, rules, *args, **kwargs):
        super(RulesASTVisitor, self).__init__(*args, **kwargs)

        self._rules = rules

    def generic_visit(self, node):
        if not isinstance(node, RulesASTVisitor._valid_classes):
            raise InvalidASTNodeError(self._rules, node)

        return super(RulesASTVisitor, self).generic_visit(node)


class MatchableString(str):
    """
    Enhanced string - it has all methods and properties of a string, provides
    :py:ref:`re.match` and :py:ref:`re.search` as instance methods.
    """

    # pylint: disable=invalid-name
    def match(self, pattern, I=True):
        return re.match(pattern, str(self), re.I if I is True else 0)

    def search(self, pattern, I=True):
        return re.search(pattern, str(self), re.I if I is True else 0)


class Rules(object):
    # pylint: disable=too-few-public-methods

    """
    Wrap compilation and evaluation of filtering rules.

    :param str rules: Rule is a Python expression that could be evaluated.
    """

    def __init__(self, rules):
        self._rules = rules
        self._code = None

    def __repr__(self):
        return '<Rules: {}>'.format(self._rules)

    def _compile(self):
        """
        Compile rule. Parse rule into an AST, perform its sanity checks,
        and then compile it into executable.
        """

        try:
            tree = ast.parse(self._rules, mode='eval')

        except SyntaxError as exc:
            raise RulesSyntaxError(self._rules, exc)

        except TypeError as e:
            raise RulesTypeError(self._rules, e)

        RulesASTVisitor(self).visit(tree)

        try:
            return compile(tree, '<static-config-file>', 'eval')

        except Exception as e:
            raise RulesTypeError(self._rules, e)

    def eval(self, our_globals, our_locals):
        """
        Evaluate rule. User must provide both `locals` and `globals` dictionaries
        we use as a context for the rule.
        """

        if self._code is None:
            self._code = self._compile()

        # eval is dangerous. This time I hope it's safe-guarded by AST filtering...
        try:
            # pylint: disable=eval-used
            return eval(self._code, our_globals, our_locals)

        except NameError as exc:
            raise UchoError('Unknown variable used in rule: {}'.format(str(exc)))


def evaluate_rules(rules, context=None):
    """
    Evaluate rules to a single value (usualy bool-ish - ``True``/``False``, (non-)empty string, etc.),
    within a context provided by the caller via ``context`` mapping.
    Keys and values in the mapping are passed to internal ``eval`` implementation, making them
    available to the rules.

    :param str rules: rules to evaluate.
    :param dict context: mapping of names and object caller wants to be available to rules.
    :returns: whatever comes out from rules evaluation.
    """

    # pylint: disable=no-self-use

    if not rules:
        return True

    def _enhance_strings(variables):
        return {
            key: MatchableString(value) if isinstance(value, str) else value for key, value in variables.items()
        }

    custom_locals = _enhance_strings(context or {})

    custom_locals['EXISTS'] = lambda name: name in custom_locals

    logging.debug('rules: {}'.format(rules))
    logging.debug('locals: {}'.format(custom_locals))

    result = Rules(rules).eval({}, custom_locals)
    logging.debug('eval result: {}'.format(result))

    return result
