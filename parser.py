def parse_latex_matrix(s):
    """
    Parse a LaTeX pmatrix string (optionally with a leading minus sign) into a list of lists of numbers.
    Returns (sign, matrix) where sign is +1 or -1.
    Example: '-\\begin{pmatrix}1&0\\\\0&1\\end{pmatrix}' -> (-1, [[1,0],[0,1]])
    """
    s = s.strip()
    sign = 1
    if s.startswith('-'):
        sign = -1
        s = s[1:].strip()
    # Accept both pmatrix and bmatrix
    m = re.match(r"\\begin\{p?matrix\}(.*?)\\end\{p?matrix\}", s)
    if not m:
        return None
    body = m.group(1)
    # Split rows by \\ (double backslash)
    rows = [row for row in re.split(r"\\\\", body) if row.strip()]
    matrix = []
    for row in rows:
        # Split columns by &
        cols = [c.strip() for c in row.split('&')]
        # Try to convert to int or float
        parsed_row = []
        for c in cols:
            try:
                parsed_row.append(int(c))
            except ValueError:
                try:
                    parsed_row.append(float(c))
                except ValueError:
                    # If not a number, just keep as string
                    parsed_row.append(c)
        matrix.append(parsed_row)
    return sign, matrix

import re
import regex
import sympy
from typing import TypeVar, Iterable, List, Union, Any, Dict
from word2number import w2n
from utils import *


def _fix_fracs(string):
    substrs = string.split("\\frac")
    new_str = substrs[0]
    if len(substrs) > 1:
        substrs = substrs[1:]
        for substr in substrs:
            new_str += "\\frac"
            if len(substr) > 0 and substr[0] == "{":
                new_str += substr
            else:
                try:
                    assert len(substr) >= 2
                except:
                    return string
                a = substr[0]
                b = substr[1]
                if b != "{":
                    if len(substr) > 2:
                        post_substr = substr[2:]
                        new_str += "{" + a + "}{" + b + "}" + post_substr
                    else:
                        new_str += "{" + a + "}{" + b + "}"
                else:
                    if len(substr) > 2:
                        post_substr = substr[2:]
                        new_str += "{" + a + "}" + b + post_substr
                    else:
                        new_str += "{" + a + "}" + b
    string = new_str
    return string


def _fix_a_slash_b(string):
    if len(string.split("/")) != 2:
        return string
    a = string.split("/")[0]
    b = string.split("/")[1]
    try:
        if "sqrt" not in a:
            a = int(a)
        if "sqrt" not in b:
            b = int(b)
        assert string == "{}/{}".format(a, b)
        new_string = "\\frac{" + str(a) + "}{" + str(b) + "}"
        return new_string
    except:
        return string


def _fix_sqrt(string):
    _string = re.sub(r"\\sqrt(\w+)", r"\\sqrt{\1}", string)
    return _string


def convert_word_number(text:str) -> str:
    try:
        text = str(w2n.word_to_num(text))
    except:
        pass
    return text

# units mainly from MathQA
unit_texts = [
    "east", "degree", "mph", "kmph", "ft", "m sqaure", " m east", "sq m", "deg", "mile",
    "q .", "monkey", "prime", "ratio", "profit of rs",  "rd", "o", "gm",
    "p . m", "lb", "tile", "per", "dm", "lt", "gain", "ab", "way", "west",
    "a .", "b .", "c .", "d .", "e .", "f .", "g .", "h .", "t", "a", "h",
    "no change", "men", "soldier", "pie", "bc", "excess", "st",
    "inches", "noon", "percent", "by", "gal", "kmh", "c", "acre", "rise",
    "a . m", "th", "π r 2", "sq", "mark", "l", "toy", "coin",
    "sq . m", "gallon", "° f", "profit", "minw", "yr", "women",
    "feet", "am", "pm", "hr", "cu cm", "square", "v â € ™", "are",
    "rupee", "rounds", "cubic", "cc", "mtr", "s", "ohm", "number",
    "kmph", "day", "hour", "minute", "min", "second", "man", "woman", 
    "sec", "cube", "mt", "sq inch", "mp", "∏ cm ³", "hectare", "more",
    "sec", "unit", "cu . m", "cm 2", "rs .", "rs", "kg", "g", "month",
    "km", "m", "cm", "mm", "apple", "liter", "loss", "yard",
    "pure", "year", "increase", "decrease", "d", "less", "Surface",
    "litre", "pi sq m", "s .", "metre", "meter", "inch",
]

unit_texts.extend([t + "s" for t in unit_texts])

def strip_string(string):
    string = str(string).strip()
    # linebreaks
    string = string.replace("\n", "")

    # right "."
    string = string.rstrip(".")

    # remove inverse spaces
    # replace \\ with \
    string = string.replace("\\!", "")
    # string = string.replace("\\ ", "")
    # string = string.replace("\\\\", "\\")

    # matrix
    string = re.sub(r'\\begin\{array\}\{.*?\}', r'\\begin{pmatrix}', string)  
    string = re.sub(r'\\end\{array\}', r'\\end{pmatrix}', string)  
    string = string.replace("bmatrix", "pmatrix")


    # replace tfrac and dfrac with frac
    string = string.replace("tfrac", "frac")
    string = string.replace("dfrac", "frac")

    # remove \left and \right
    string = string.replace("\\left", "")
    string = string.replace("\\right", "")
    string = string.replace("\\{", "{")
    string = string.replace("\\}", "}")
    
    # remove LaTeX inline math delimiters \( and \) when they wrap the entire expression
    if string.startswith("\\(") and string.endswith("\\)"):
        string = string[2:-2]
    
    # remove inline math delimiters \( and \)
    string = string.replace("\\(", "")
    string = string.replace("\\)", "")

    # Remove unit: miles, dollars if after is not none
    _string = re.sub(r"\\text{.*?}$", "", string).strip()
    if _string != "" and _string != string:
        # print("Warning: unit not removed: '{}' -> '{}'".format(string, _string))
        string = _string
    
    # Remove unit: texts
    for _ in range(2):
        for unit_text in unit_texts:
            # Skip single letters if they appear in algebraic contexts (between operators/parentheses)
            if len(unit_text) == 1 and unit_text.isalpha():
                # Check if this single letter appears in an algebraic context
                # Look for patterns like (a+, a-, a*, a/, +a, -a, *a, /a, =a, a=
                algebraic_pattern = r"[\(\)\+\-\*/=]" + unit_text + r"[\(\)\+\-\*/=]"
                if re.search(algebraic_pattern, string):
                    continue  # Skip removing this single letter
            
            # use regex, the prefix should be either the start of the string or a non-alphanumeric character
            # the suffix should be either the end of the string or a non-alphanumeric character
            _string = re.sub(r"(^|\W)" + unit_text + r"($|\W)", r"\1\2", string)
            if _string != "":
                string = _string

    # Remove circ (degrees)
    string = string.replace("^{\\circ}", "")
    string = string.replace("^\\circ", "")

    # remove dollar signs
    string = string.replace("\\$", "")
    string = string.replace("$", "")

    # convert word number to digit
    string = convert_word_number(string)

    # replace "\\text{...}" to "..."
    string = re.sub(r"\\text\{(.*?)\}", r"\1", string)
    # replace "\\textbf{...}" to "..."
    string = re.sub(r"\\textbf\{(.*?)\}", r"\1", string)
    for key in ['x=', 'y=', 'z=', 'x\\in', 'y\\in', 'z\\in', 'x\\to', 'y\\to', 'z\\to']:
        string = string.replace(key, "")
    string = string.replace("\\emptyset", r"{}")
    string = string.replace("(-\\infty,\\infty)", "\\mathbb{R}")

    # remove percentage
    string = string.replace("\\%", "")
    string = string.replace(r"\%", "")
    string = string.replace("%", "")

    # " 0." equivalent to " ." and "{0." equivalent to "{." Alternatively, add "0" if "." is the start of the string
    string = string.replace(" .", " 0.")
    string = string.replace("{.", "{0.")

    # cdot
    # string = string.replace("\\cdot", "")
    if string.startswith("{") and string.endswith("}") and string.isalnum() or \
        string.startswith("(") and string.endswith(")") and string.isalnum() or \
        string.startswith("[") and string.endswith("]") and string.isalnum():
        string = string[1:-1]

    # inf
    string = string.replace("infinity", "\\infty")
    if "\\infty" not in string:
        string = string.replace("inf", "\\infty")
    string = string.replace("+\\inity", "\\infty")

    # and 
    string = string.replace("and", "")
    string = string.replace("\\mathbf", "")

    # use regex to remove \mbox{...}
    string = re.sub(r"\\mbox{.*?}", "", string)

    # quote
    string.replace("'", "")
    string.replace("\"", "")
    
    # i, j
    if "j" in string and "i" not in string:
        string = string.replace("j", "i")

    # replace a.000b where b is not number or b is end, with ab, use regex
    string = re.sub(r"(\d+)\.0*([^\d])", r"\1\2", string)
    string = re.sub(r"(\d+)\.0*$", r"\1", string)

    # if empty, return empty string
    if len(string) == 0:
        return string
    if string[0] == ".":
        string = "0" + string

    # to consider: get rid of e.g. "k = " or "q = " at beginning
    if len(string.split("=")) == 2:
        if len(string.split("=")[0]) <= 2:
            string = string.split("=")[1]

    string = _fix_sqrt(string)
    string = string.replace(" ", "")

    # \frac1b or \frac12 --> \frac{1}{b} and \frac{1}{2}, etc. Even works with \frac1{72} (but not \frac{72}1). Also does a/b --> \\frac{a}{b}
    string = _fix_fracs(string)

    # NOTE: X/Y changed to \frac{X}{Y} in dataset, but in simple cases fix in case the model output is X/Y
    string = _fix_a_slash_b(string)

    return string

def matrix_equiv(ans1, ans2):
    """
    Returns True if two LaTeX matrices (possibly with sign) are equivalent.
    """
    parsed1 = parse_latex_matrix(ans1)
    parsed2 = parse_latex_matrix(ans2)
    if parsed1 is None or parsed2 is None:
        return False
    sign1, mat1 = parsed1
    sign2, mat2 = parsed2
    if len(mat1) != len(mat2):
        return False
    for r1, r2 in zip(mat1, mat2):
        if len(r1) != len(r2):
            return False
        for v1, v2 in zip(r1, r2):
            try:
                if sign1 * float(v1) != sign2 * float(v2):
                    return False
            except Exception:
                if str(v1) != str(v2):
                    return False
    return True


def extract_multi_choice_answer(pred_str):
    # TODO: SFT models
    if 'Problem:' in pred_str:
        pred_str = pred_str.split("Problem:", 1)[0]
    pred_str = pred_str.replace("choice is", "answer is")
    patt = regex.search(r"answer is \(?(?P<ans>[abcde])\)?", pred_str.lower())
    if patt is not None:
        return patt.group('ans').upper()
    return 'placeholder'


def extract_answer(pred_str, data_name):
    if data_name in ["mmlu_stem", "sat_math", "mathqa"]:
        return extract_multi_choice_answer(pred_str)

    # Cap the string at "I hope it is correct" and ignore everything after
    if "I hope it is correct" in pred_str:
        pred_str = pred_str.split("I hope it is correct")[0] + "I hope it is correct"

    pred = pred_str

    # List of (pattern, group, description) for answer extraction
    regex_patterns = [
        # e.g. "Final Answer: The roots are $3$, $5$, and $7$. I hope it is correct."
        (r"Final Answer: .*?(?:are|is) ([^.]+)\. I hope", 1, "Final Answer: ... are/is ... . I hope"),
        # e.g. "Final Answer: ... is $-2$ ... ."
        (r"Final Answer: .*?is [^$]*\$([^$]+)\$.", 1, "Final Answer: ... is $...$"),
        # e.g. the final answer is ...  $-2$
        (r"final answer is.*? \$([^$]+)\$.", 1, "final answer is ... $...$"),
        # e.g. "The answer is $...$"
        (r"[Tt]he answer is \$([^$]+)\$.", 1, "The answer is $...$"),
        # e.g. "The answer is a/an ..."
        (r"[Tt]he answer is (?:a|an) ([^\n\.]*).", 1, "The answer is a/an ..."),
        # e.g. "The answer is ..."
        (r"[Tt]he answer is ([^\n\.]*).", 1, "The answer is ..."),
        # e.g. "final answer is a/an ..."
        (r"final answer is (?:a|an) ([^\n\.]*).", 1, "final answer is a/an ..."),
        # e.g. "final answer is ..."
        (r"final answer is ([^\n\.]*).", 1, "final answer is ..."),
        # e.g. "he answer is a/an ..."
        (r"he answer is (?:a|an) ([^\n\.]*).", 1, "he answer is a/an ..."),
        # e.g. "he answer is ..."
        (r"he answer is ([^\n\.]*).", 1, "he answer is ..."),
        
    ]

    # Collect all matches for all patterns, keep the one that appears last in the text
    last_match = None
    last_group = None
    last_pos = -1
    for patt, group, _ in regex_patterns:
        for m in re.finditer(patt, pred_str):
            if m.start() > last_pos:
                last_match = m
                last_group = group
                last_pos = m.start()
    if last_match is not None:
        pred = last_match.group(last_group).strip()
        
        # Handle multiple numbers in dollar signs like "$3$, $5$, and $7$"
        if '$' in pred and ',' in pred:
            # Extract all numbers from dollar signs
            dollar_numbers = re.findall(r'\$([^$]+)\$', pred)
            if dollar_numbers:
                # Join the numbers with commas
                pred = ','.join(dollar_numbers)
        # Handle single number in dollar signs like "$3$"
        elif '$' in pred:
            dollar_match = re.search(r'\$([^$]+)\$', pred)
            if dollar_match:
                pred = dollar_match.group(1)

    # Special handling for boxed answers
    if 'boxed' in pred:
        ans = pred.split('boxed', 1)[-1]
        if len(ans) == 0:
            return ""
        elif ans[0] == '{':
            stack = 1
            a = ''
            for c in ans[1:]:
                if c == '{':
                    stack += 1
                    a += c
                elif c == '}':
                    stack -= 1
                    if stack == 0:
                        break
                    a += c
                else:
                    a += c
        else:
            a = ans.split('$')[0].strip()
        pred = a

    # minerva_math: 'final answer is ... . I ...'
    if pred == pred_str and 'final answer is ' in pred_str and '. I ' in pred_str:
        tmp = pred_str.split('final answer is ', 1)[1]
        pred = tmp.split('. I ', 1)[0].strip()

    # Fallback: use the last number in the string
    if pred == pred_str:
        pattern = r'-?\d*\.?\d+'
        numbers = re.findall(pattern, pred_str.replace(",", ""))
        if numbers:
            pred = numbers[-1]
        else:
            pred = ''

    # Clean up answer
    pred = re.sub(r"\n\s*", "", pred)
    if pred != "" and pred[0] == ":":
        pred = pred[1:]
    if pred != "" and pred[-1] == ".":
        pred = pred[:-1]
    if pred != "" and pred[-1] == "/":
        pred = pred[:-1]
    pred = strip_string(pred)
    return pred


def parse_ground_truth(example: Dict[str, Any], data_name):
    if 'gt_cot' in example and 'gt' in example:
        if data_name in ["math", "math_oai", "ocw", "amps", "hungarian_exam"]:
            gt_ans = extract_answer(example['gt_cot'], data_name)
        else:
            gt_ans = strip_string(example['gt'])
        return example['gt_cot'], gt_ans

    # parse ground truth
    if data_name in ["math", "math_oai", "minerva_math", "ocw", "amps", "hungarian_exam"]:
        gt_cot = example['solution']
        gt_ans = extract_answer(gt_cot, data_name)
    elif data_name in ['mathqa']:
        gt_cot = example['rationale']
        gt_ans = example['correct'].upper()
        assert gt_ans in ['A', 'B', 'C', 'D', 'E']
    elif data_name == "gsm8k":
        gt_cot, gt_ans = example['answer'].split("####")
    elif data_name == "gsm_hard":
        gt_cot, gt_ans = example['code'], example['target']
    elif data_name == "svamp":
        gt_cot, gt_ans = example['Equation'], example['Answer']
    elif data_name == "asdiv":
        gt_cot = example['formula']
        gt_ans = re.sub(r"\(.*?\)", "", example['answer'])
    elif data_name == "mawps":
        gt_cot, gt_ans = None, example['target']
    elif data_name == "tabmwp":
        gt_cot = example['solution']
        gt_ans = example['answer']
        if example['ans_type'] in ['integer_number', 'decimal_number']:
            if '/' in gt_ans:
                gt_ans = int(gt_ans.split('/')[0]) / int(gt_ans.split('/')[1])
            elif ',' in gt_ans:
                gt_ans = float(gt_ans.replace(',', ''))
            elif '%' in gt_ans:
                gt_ans = float(gt_ans.split('%')[0]) / 100
            else:
                gt_ans = float(gt_ans)
    elif data_name == "bbh":
        gt_cot, gt_ans = None, example['target']
    elif data_name == "theorem_qa":
        gt_cot, gt_ans = None, example['answer']
    elif data_name == "mmlu_stem":
        abcd = 'ABCD'
        gt_cot, gt_ans = None, abcd[example['answer']]
    elif data_name == "sat_math":
        gt_cot, gt_ans = None, example['Answer']
    else:
        raise NotImplementedError(f"`{data_name}`")
    # post process
    gt_cot = str(gt_cot).strip()
    gt_ans = strip_string(gt_ans)
    return gt_cot, gt_ans


def parse_question(example, data_name):
    question = ""
    if data_name == "asdiv":
        question = f"{example['body'].strip()} {example['question'].strip()}"
    elif data_name == "svamp":
        body = example["Body"].strip()
        if not body.endswith("."):
            body = body + "."
        question = f'{body} {example["Question"].strip()}'
    elif data_name == "tabmwp":
        title_str = f'regarding "{example["table_title"]}" ' if example['table_title'] else ""
        question = f'Read the following table {title_str}and answer a question:\n'
        question += f'{example["table"]}\n{example["question"]}'
        if example['choices']:
            question += f' Please select from the following options: {example["choices"]}'
    elif data_name == "theorem_qa":
        question = f"{example['question'].strip()}\nTheorem: {example['theorem_def'].strip()}"
    elif data_name == "mmlu_stem":
        options = example['choices']
        assert len(options) == 4
        for i, (label, option) in enumerate(zip('ABCD', options)):
            options[i] = f"({label}) {str(option).strip()}"
        options = ", ".join(options)
        question = f"{example['question'].strip()}\nWhat of the following is the right choice? Explain your answer.\n{options}"
    elif data_name == "sat_math":
        options = example['options'].strip()
        assert 'A' == options[0]
        options = '(' + options
        for ch in 'BCD':
            if f' {ch}) ' in options:
                options = regex.sub(rf' {ch}\) ', rf" ({ch}) ", options)
        question = f"{example['question'].strip()}\nWhat of the following is the right choice? Explain your answer.\n{options.strip()}"
    elif data_name == "mathqa":
        example['problem'] = example['problem'][0].upper() + example['problem'][1:]
        options = example['options'].strip()
        if options[0] == '[':
            options = eval(options)
            options = ", ".join(options)
        assert 'a' == options[0], options
        for ch in 'abcde':
            if f'{ch} ) ' in options:
                options = regex.sub(rf'{ch} \) {ch} \) ', rf'{ch} ) ', options)
                options = regex.sub(rf'{ch} \) ', rf"({ch.upper()}) ", options)
        options = options.replace(' , ', ', ')
        question = f"{example['problem'].strip()}\nWhat of the following is the right choice? Explain your answer.\n{options.strip()}"
    else:
        for key in ['question', 'problem', 'Question', 'input']:
            if key in example:
                question = example[key]
                break
    assert question != ""
    # Yes or No question
    _, gt_ans = parse_ground_truth(example, data_name)
    gt_lower = gt_ans.lower()
    if gt_lower in ["true", "false"]:
        question += " (True or False)"
    if gt_lower in ["yes", "no"]:
        question += " (Yes or No)"
    return question.strip()


def run_execute(executor, result, prompt_type, data_name, execute=False):
    if not result or result == 'error':
        return None, None
    report = None

    if "program_only" in prompt_type:
        prediction = extract_program_output(result)
    elif prompt_type in ["pot", "pal"] and execute:
        code = extract_program(result)
        prediction, report = executor.apply(code)
    else:
        prediction = extract_answer(result, data_name)

    prediction = strip_string(prediction)
    return prediction, report

# Utility for answer checking: matrix-aware comparison
def answers_equivalent(pred, gt):
    # Try matrix equivalence first
    if matrix_equiv(pred, gt):
        return True
    # Fallback: string equality
    return pred == gt


def _test_extract_answer():
    text= r"""
    The answer is $\boxed{\left(                                                                                                                      
\begin{array}{ccc}                                                                                                                                          
 -13 & 4 & -2 \\
 7 & 8 & -3 \\
 0 & 18 & -7 \\
 6 & 12 & 5 \\
\end{array}
\right)}$.
"""
    print(extract_answer(text, "math"))
    # should output a dict


if __name__ == "__main__":
    _test_extract_answer()