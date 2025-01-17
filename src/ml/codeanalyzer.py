from transformers import RobertaTokenizer, RobertaForSequenceClassification
import tensorflow as tf
import re
from typing import List, Dict, Tuple
import torch
# Define Class for analyzing code files
class CodeAnalyzer:
    def __init__(self):
        #Initialize Tokenizer and model using pre trained models
        self.tokenizer = RobertaTokenizer.from_pretrained('microsoft/codebert-base')
        self.model = RobertaForSequenceClassification.from_pretrained('microsoft/codebert-base')
        #Set limits for code
        self.complexity_threshold = 0.7
        self.max_line_length = 80
        self.max_function_length = 50
        self.max_nested_depth = 3
        #Analyze a given code snippet and return analysis results
    def analyze_code_snippet(self,code:str) -> dict:
        #Use the tokenizer to generate Ai inputs
        inputs = self.tokenizer(code,return_tensors = "pt", truncation =True,max_length =512)
        #Exapnd Input and then fit it into the model
        outputs = self.model(**inputs)
        #Find the Complexity socre by going through the logits tensor
        complexity_score = float(torch.sigmoid(outputs.logits[0][0]).detach().numpy())
        #Split the code among each newline
        lines = code.split('\n')
        analysis_result = {
            'Complexity_Score': complexity_score,
            'Line Count': len(lines),
            'Suggestions': self._generate_suggestions(code,complexity_score),
            'code metrics': self._calculate_metrics(code),
            'potential issues': self._identify_issues(code),
            'best practices': self._check_best_practices(code)
        }
        #Return the Dictionary
        return analysis_result
    #Caculate different metrics of the code such as the number of lines, number of blank lines, number of comments and number of functions
    def _calculate_metrics(self, code:str) -> Dict:
        #Split the Code among each newline
        lines = code.split('\n')
        return{
            #Return total amoung of lines
            'total lines': len(lines),
            #Strip every single in and then return every line thats not full of code
            'blank lines': len([l for l in lines if not l.strip()]),
            #Add every single line that starts with #
            'comment lines': len([l for l in lines if l.strip().startswith('#')]),
            #Searches through code and finds the number of instances in the code that matches this pattern
            'function count': len(re.findall(r'def\s+\w+\s*\(', code))      
        }
    #This Function Gets ever single issue with the given code
    def _identify_issues(self,code: str) ->List[Dict]:
        issues =[]
        #Serches for every single code in this specfi formate
        functions = re.finditer(r'def\s+(\w+)\s*\(([^)]*)\):', code)
        for func in functions:
            #Gets the first group which is usually the name of the funciton after the def
            func_name = func.group(1)
            #Extracts body of the function
            func_body = self._extract_function_body(code,func.start())
            # If the lenght of the body greater than the max function lenght then append this to the issues
            if len(func_body.split('\n')) > self.max_function_length:
                issues.append({'type': 'long Function', 'name': func_name,'message': f'Has Too Many Lines: ({len(func_body.split("\n"))} lines)'})
        # if the nesting depth is more than the max nested depth then append this error to message
        if self._check_nesting_depth(code) > self.max_nested_depth:
            issues.append({
                    'type': 'deep neesting',
                    'message' : f'Code Contains deep nesting'
                })
        #function call finds the duplicates in the and adds error message if it does look similar
        duplicates = self._find_duplicate_code(code)
        if duplicates:
            issues.append({
                'type':'code duplicaiton',
                'message': f'Found {len(duplicates)} that look similar'
            })
        return issues
    #Checks the capitilzaiton in the code and if it is missiing documentation
    def _check_best_practices(self,code:str) ->List[Dict]:
        practices = []
        #Searches through the code for the classes
        classes = re.findall(r'class\s+([A-Z]\w*)', code)
        #Finds if the first leter is capital and the second is lower case. If this is not the case then append the issue
        if not all(cls[0].isupper() and cls[1:].islower() for cls in classes):
            practices.append({
                'type': 'naming_convention',
                'message':'Class names should use the proper CapWords Convnetion'
            })
        functions = re.finditer(r'def\s+\w+\s*\([^)]*\):', code)
        for func in functions:
            #Extracts the body from the code given 
            func_body = self._extract_function_body(code,func.start())
            #Searches the code for the documentation tag. If not present then it appends the code
            if '"""' not in func_body[:func_body.find('\n')]:
                practices.append({
                    'type': 'missing documentation',
                    'message': 'Funcitons are missing documentation'
                })
        return practices
    def _generate_suggestions(self, code:str , complexity_score: float) ->List[str]:
        suggestions = []
        #if complictyu score is lower then where the complexity threshold then append the suggestion
        if complexity_score > self.complexity_threshold:
            suggestions.append("Functions are too complex consider breaking it down")
        #Idtifies the issue and then adds it ot the issues variable
        issues = self._identify_issues(code)
        #Cheks the best practices and adds it to the practices variable
        practices = self._check_best_practices(code)
        # For every issue in issues append it to the suggestion with the message
        for issue in issues:
            suggestions.append(issue['message'])
        #Samthing for practices
        for practice in practices:
            suggestions.append(practice['message'])
        return suggestions
    def _extract_function_body(self,code:str,start_pos: int) ->str:
        #Starts from the first postion and splits every line by a /n
        lines = code[start_pos:].split('\n')
        body = []
        indent = None
        #skips the first line becuas that is the function definiton
        for line in lines[1:]:
            #if the line is empty the skip it 
            if not line.strip():
                continue
            #Find out the current index
            current_indent = len(line) - len(line.lstrip())
            #if the indent has not been set then set it
            if indent is None:
                indent = current_indent
                body.append(line)
            #if current _indent is greater than ident add the line to the body
            elif current_indent >= indent:
                body.append(line)
            #Else if the current indent is less and not equal to the ident then break
            else:
                break
        return '\n'.join(body)
    def _check_nesting_depth(self,code: str) ->int:
        #Splits the code up
        lines = code.split('\n')
        max_dept = 0
        current_dept = 0
        for line in lines:
            #takes away the whitspaces
            stripped = line.strip()
            #if it starts with a conditional statmen then increase current dept by 1
            if stripped.startswith(('if ', 'for ', 'while ', 'def ', 'class ')):
                current_dept +=1
                max_dept = max(max_dept,current_dept)
            #if there is a return break or continue statment then change the current dept by decresing by one unless its already at 0
            elif stripped.startswith(('return','break','continue')):
                current_dept = max(0,current_dept-1)
        return max_dept
    #Finds duplicate code, This could be better becuase it only searches in a block of size 3 which isn't nessesary efficent
    def _find_duplicate_code(self, code:str) -> List[Tuple[str,List[int]]]:
        #splits the code by every newline
        lines = code.split('\n')
        duplicates = []
        #Size of the code blocks to check
        block_size = 3 
        #Goes through ever single line
        for i in range(len(lines) - block_size+1):
            #Create the block
            block = '\n'.join(lines[i:i + block_size])
            matches = []
            #Check the rest of the code to see if it identical to the rest of the code
            for j in range(i+1, len(lines)-block_size+1):
                compare_block = '\n'.join(lines[j:j + block_size])
                #If the block and compare block are the same then add it to the matches list
                if block == compare_block:
                    matches.append(j)
            #if matches is not empty then append it to duplicates with the block and matches
            if matches:
                duplicates.append((block,[i]+matches))
        return duplicates