import random
import re

def randomAvatar():
    num = random.randint(1, 8)
    return f"/static/images/avatar/{num}.svg"

def remove_consecutive_empty_lines(text):
    lines = [line for line in text.split("\n") if line.strip()]
    return "\n".join(lines)

def remove_br_tags(text):
    return re.sub(r'<br\s*/?>', '', text)