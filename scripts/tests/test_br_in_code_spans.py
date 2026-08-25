'''Tests for `_flatten_br_inside_code_spans` and its code-span tokenizer.

The generated API reference contains ~30,000 legitimate `<br />` tags — in an
ordinary table cell they are the only way to get a line break. Only the handful
that land INSIDE an inline code span are a defect, because markdown does not
interpret HTML in a code span and the reader is shown the characters `<br />`.
So the property that matters most here is the negative one: everything outside a
span must come through untouched.
'''

REAL_KGW_ROW = (
    '| `componentLogLevels` | Envoy log levels for specific components, e.g. '
    '`yaml<br />\tcomponentLogLevels:<br />\t  upstream: debug<br />'
    '\t  connection: trace<br />` These will be converted. |'
)


def test_collapses_br_inside_a_code_span(gen_ref_docs):
    '''The real kgateway 2.2.x `componentLogLevels` row.'''
    out = gen_ref_docs._flatten_br_inside_code_spans(REAL_KGW_ROW)
    assert '<br' not in out
    assert '`componentLogLevels: upstream: debug connection: trace`' in out
    # The prose either side of the span is preserved.
    assert out.startswith('| `componentLogLevels` | Envoy log levels')
    assert out.endswith('These will be converted. |')


def test_leaves_br_outside_a_code_span_alone(gen_ref_docs):
    '''THE load-bearing case: a normal multi-line table cell must not change.

    Rewriting these globally would flatten every wrapped cell in the reference
    docs onto one line.
    '''
    row = '| `field` | line one<br />line two<br />line three |'
    assert gen_ref_docs._flatten_br_inside_code_spans(row) == row


def test_mixed_line_collapses_only_the_span(gen_ref_docs):
    row = '| `a<br />b` | prose<br />more `plain` text<br />end |'
    out = gen_ref_docs._flatten_br_inside_code_spans(row)
    assert '`a b`' in out
    assert out.count('<br />') == 2, 'the two breaks outside the span must survive'
    assert '`plain`' in out, 'an untouched span must be left byte-identical'


def test_line_with_no_code_span_is_untouched(gen_ref_docs):
    row = '| plain | a<br />b<br />c |'
    assert gen_ref_docs._flatten_br_inside_code_spans(row) == row


def test_drops_the_orphaned_fence_info_string(gen_ref_docs):
    '''crd-ref-docs strips the ``` but leaves the language behind.'''
    out = gen_ref_docs._flatten_br_inside_code_spans('see `yaml<br />a: 1<br />`')
    assert out == 'see `a: 1`'


def test_unescapes_braces_that_a_code_span_would_show_verbatim(gen_ref_docs):
    '''Inside a code span a backslash escape is NOT processed, so `\\{` reaches
    the reader with the backslash showing.'''
    out = gen_ref_docs._flatten_br_inside_code_spans(
        'e.g. `yaml<br />x: \\{\\{inja\\}\\}<br />`'
    )
    assert out == 'e.g. `x: {{inja}}`'
    assert '\\' not in out


def test_quotes_are_left_as_plain_ascii(gen_ref_docs):
    '''The output must stay inside a code span, never become raw <code>.

    Raw inline HTML lets Goldmark keep parsing markdown, and the typographer
    curls the quotes in `value: "/foo"` into `“/foo”` — silently corrupting a
    YAML snippet the reader is meant to copy. A code span is immune.
    '''
    out = gen_ref_docs._flatten_br_inside_code_spans('`yaml<br />value: "/foo"<br />`')
    assert out == '`value: "/foo"`'
    assert '<code' not in out
    assert '“' not in out and '”' not in out


def test_is_idempotent(gen_ref_docs):
    once = gen_ref_docs._flatten_br_inside_code_spans(REAL_KGW_ROW)
    assert gen_ref_docs._flatten_br_inside_code_spans(once) == once


def test_tokenizer_does_not_span_between_two_separate_code_spans(gen_ref_docs):
    '''The bug that made this defect look 17x bigger than it is.

    A naive `` `[^`]*` `` regex matches from the CLOSING backtick of one span,
    across text that is outside any span, to the OPENING backtick of the next.
    That is how a count of 11 affected spans was first reported as 188, and how
    surrounding prose was misread as markdown-significant characters inside the
    spans.
    '''
    line = 'text `first` middle<br />more `second` tail'
    spans = [body for _, _, body in gen_ref_docs._iter_code_spans(line)]
    assert spans == ['first', 'second'], spans
    # And therefore the outside break survives.
    assert gen_ref_docs._flatten_br_inside_code_spans(line) == line


def test_tokenizer_handles_a_double_backtick_span_holding_a_backtick(gen_ref_docs):
    '''CommonMark: a run of N backticks closes on a run of EXACTLY N.'''
    spans = [body for _, _, body in gen_ref_docs._iter_code_spans('``a ` b`` end')]
    assert spans == ['a ` b'], spans


def test_unclosed_backtick_is_not_treated_as_a_span(gen_ref_docs):
    line = 'a stray ` backtick with a<br />break'
    assert list(gen_ref_docs._iter_code_spans(line)) == []
    assert gen_ref_docs._flatten_br_inside_code_spans(line) == line
