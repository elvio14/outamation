import fitz
import pandas as pd
import json
import re

doc = fitz.open("lender.pdf")
page = doc[0]

full_text = page.get_text()

with open('gettext.txt', 'w') as f:
    f.write(full_text)

def take_last_line(text):
    return text.split('\n')[-1]

def extract_value_by_label_position(page, label_text):
    """
    Find label position and extract text in the same row or nearby area
    Works even when text order is scrambled
    """
    # Find the label
    label_instances = page.search_for(label_text)
    
    if not label_instances:
        print(f"Label '{label_text}' not found")
        return None
    
    # Use first instance
    label_rect = label_instances[0]
    print(f"Label '{label_text}' found at: {label_rect}")
    
    # Strategy A: Extract text to immediate right 
    value_rect = fitz.Rect(
        label_rect.x1 + 5,          # Start 5 points after label ends
        label_rect.y0 - 2,          # Slightly above (for tolerance)
        label_rect.x1 + 150,        # Extend 300 points to the right
        label_rect.y1 + 2           # Slightly below (for tolerance)
    )
    
    value = page.get_text("text", clip=value_rect).strip()
    
    if value:
        print(f"Found value to the right: '{value}'")
        return take_last_line(value)
    
    # Strategy B: Extract text far right
    value_rect = fitz.Rect(
        label_rect.x0 + 150,              # Same left position
        label_rect.y1 + 2,          # Start below label
        label_rect.x1 + 450,        # Extend right
        label_rect.y1 + 50          # Check 50 points down
    )
    
    value = page.get_text("text", clip=value_rect).strip()
    
    if value:
        print(f"Found value below: '{value}'")
        return take_last_line(value)

    # Strategy C: Extract text below label (if nothing to the right)
    value_rect = fitz.Rect(
        label_rect.x0,              # Same left position
        label_rect.y1 + 2,          # Start below label
        label_rect.x1 + 300,        # Extend right
        label_rect.y1 + 50          # Check 50 points down
    )
    
    value = page.get_text("text", clip=value_rect).strip()
    
    if value:
        print(f"Found value below: '{value}'")
        return take_last_line(value)
    
    return None

def extract_with_regex(text, pattern, group=1):
    """Extract field using regex pattern"""
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(group)
    return None

# Define patterns for your specific fields
patterns = {
    'applicants': r'Applicants\s*[:\s]+([A-Z0-9-]+)',
}

extracted_fields = {}
for field_name, pattern in patterns.items():
    value = extract_with_regex(full_text, pattern)
    extracted_fields[field_name] = value


def safe_write_json(data, filename):
    """Write JSON with error handling and validation"""
    try:
        # Validate data is JSON serializable
        json.dumps(data)
        
        # Write to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        print(f"✓ Successfully wrote to {filename}")
        return True
        
    except TypeError as e:
        print(f"✗ Error: Data is not JSON serializable - {e}")
        return False
    except IOError as e:
        print(f"✗ Error writing file: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

# print("Extracted with regex:")
# for field, value in extracted_fields.items():
#     print(f"{field}: {value}")
# print()

print("Extracted with label position rect:")
applicant = extract_value_by_label_position(page, "Applicants")
loan_program = extract_value_by_label_position(page, "Loan Program")
purchase_price = extract_value_by_label_position(page, "Purchase Price (+)")
loan_amount = extract_value_by_label_position(page, "Loan Amount (-)")
estimated_funds = extract_value_by_label_position(page, "needed to close")
monthly_payment = extract_value_by_label_position(page, "Total Monthly Payment")

data = {
    "applicants": applicant,
    "loan_program": loan_program,
    "purchase_price": purchase_price,
    "loan_amount": loan_amount,
    "estimated_funds": estimated_funds,
    "monthly_payment": monthly_payment
}

safe_write_json(data, "output.json")

doc.close()