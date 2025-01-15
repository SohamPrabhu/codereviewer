from transformers import RobertaTokenizer, RobertaForSequenceClassification
import tensorflow as tf
import re
from typing import List, Dict, Tuple
import torch


class CodeAnalyzer:
    def __init__(self):
        self.tokenizer = RobertaTokenizer.from_pretrained('microsoft/codebert-base')
        self.model = RobertaForSequenceClassification.from_pretrained('microsoft/codebert-base')

        self.complexity_threshold = 0.7
        self.max_line_length = 80
        self.max_function_length = 50
        self.max_nested_depth = 3
    def analyze_code_snippet(self,code:str) -> dict:
        inputs = self.tokenizer(code,return_tensors = "pt", truncation =True,max_length =512)
        outputs = self.model(**inputs)
        complexity_score = float(torch.sigmoid(outputs.logits[0][0]).detach().numpy())

        lines = code.split('\n')
        analysis_result = {
            'Complexity_Score': complexity_score,
            'Line Count': len(lines),
            'Suggestions': self._generate_suggestions(code,complexity_score),
            'code metrics': self._calculate_metrics(code),
            'potential issues': self._identify_issues(code),
            'best practices': self._check_best_practices(code)
        }
        return analysis_result
    def _calculate_metrics(self, code:str) -> Dict:
        lines = code.split('\n')
        return{
            'total lines': len(lines),
            'blank lines': len([l for l in lines if not l.strip()]),
            'comment lines': len([l for l in lines if l.strip().startswith('#')]),
            'function_count': len(re.findall(r'def\s+\w+\s*\(', code))      
        }

    def _identify_issues(self,code: str) ->List[Dict]:
        issues =[]
        functions = re.finditer(r'def\s+(\w+)\s*\(([^)]*)\):', code)
        for func in functions:
            func_name = func.group(1)
            func_body = self._extract_function_body(code,func.start())
            if len(func_body.split('\n')) > self.max_function_length:
                # Fix this part
                issues.append({
                    'type': 'long Function',
                    'name': func_name,
                    'message': f'Has Too Many Lines: ({len(func_body.split("\n"))} lines)'
                })

        if self._check_nesting_depth(code) > self.max_nested_depth:
            issues.append({
                    'type': 'deep neesting',
                    'message' : f'Code Contains deep nesting'
                })
        
        duplicates = self._find_duplicate_code(code)
        if duplicates:
            issues.append({
                'type':'code duplicaiton',
                'message': f'Found {len(duplicates)} that look similar'
            })
        return issues
    def _check_best_practices(self,code:str) ->List[Dict]:
        practices = []
        classes = re.findall(r'class\s+([A-Z]\w*)', code)

        if not all(cls.isupper() for cls in classes):
            practices.append({
                'type': 'naming_convention',
                'message':'Class names should use the proper CapWords Convnetion'
            })
        functions = re.finditer(r'def\s+\w+\s*\([^)]*\):', code)
        for func in functions:
            func_body = self._extract_function_body(code,func.start())
            if '"""' not in func_body[:func_body.find('\n')]:
                practices.append({
                    'type': 'missing documentation',
                    'message': 'Funcitons are missing documentation'
                })
        return practices
    def _generate_suggestions(self, code:str , complexity_score: float) ->List[str]:
        suggestions = []

        if complexity_score > self.complexity_threshold:
            suggestions.append("Functions are too complex consider breaking it down")
        



        issues = self._identify_issues(code)
        practices = self._check_best_practices(code)

        for issue in issues:
            suggestions.append(issue['message'])
        for practice in practices:
            suggestions.append(practice['message'])
        return suggestions


    def _extract_function_body(self,code:str,start_pos: int) ->str:
        lines = code[start_pos:].split('\n')
        body = []
        indent = None
        for line in lines[1:]:
            if not line.strip():
                continue
            current_indent = len(line) - len(line.lstrip())
            

            if indent is None:
                indent = current_indent
                body.append(line)
            elif current_indent >= indent:
                body.append(line)
            else:
                break
        return '\n'.join(body)
    def _check_nesting_depth(self,code: str) ->int:
        lines = code.split('\n')
        max_dept = 0
        current_dept = 0


        for line in lines:
            stripped = line.strip()
            if stripped.startswith(('if ', 'for ', 'while ', 'def ', 'class ')):
                current_dept +=1
                max_dept = max(max_dept,current_dept)
            elif stripped.startswith(('return','break','continue')):
                current_dept = max(0,current_dept-1)
        return max_dept
    
    def _find_duplicate_code(self, code:str) -> List[Tuple[str,List[int]]]:
        lines = code.split('\n')
        duplicates = []

        block_size = 3 # Size of code blocks to check

        for i in range(len(lines) - block_size+1):
            block = '\n'.join(lines[i:i + block_size])
            matches = []
            for j in range(i+1, len(lines)-block_size+1):
                compare_block = '\n'.join(lines[j:j + block_size])
                if block == compare_block:
                    matches.append(j)
        
            if matches:
                duplicates.append((block,[i]+matches))
        return duplicates






