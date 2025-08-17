from core.sandbox_image.execute import run_instruction
import os, json
INSTRUCTION_FILE='core/instructions/demo.json'
TARGET_FILE='core/module.py'

os.makedirs('core/instructions', exist_ok=True)
with open(INSTRUCTION_FILE,'w', encoding='utf-8') as f:
    json.dump({'action':'replace','target':TARGET_FILE,'patch':'def new_logic(): pass'}, f)
with open(TARGET_FILE,'w', encoding='utf-8') as f:
    f.write('def old_logic(): pass')

print('BEFORE->', open(TARGET_FILE,'r', encoding='utf-8').read())
run_instruction(INSTRUCTION_FILE)
print('AFTER->', open(TARGET_FILE,'r', encoding='utf-8').read())
