# scripts/generate_test_data.py
"""Generate test data files for all tiers"""
import os
import json


def generate_tier_a():
    """Generate simple test files"""
    os.makedirs("tests/test_data/tier_a", exist_ok=True)
    
    # Simple text with key-value
    with open("tests/test_data/tier_a/simple.txt", "w") as f:
        f.write("""Name: Alice Smith
Email: alice@example.com
Age: 28
Department: Engineering

Additional notes: This is a sample employee record.
""")
    
    # JSON in markdown
    with open("tests/test_data/tier_a/simple.md", "w") as f:
        f.write("""# Employee Record

```json
{
  "employee_id": 1001,
  "name": "Bob Johnson",
  "position": "Senior Developer",
  "salary": 95000
}
```

## Notes
This employee started in 2020.
""")


def generate_tier_b():
    """Generate mixed format files"""
    os.makedirs("tests/test_data/tier_b", exist_ok=True)
    
    with open("tests/test_data/tier_b/mixed.txt", "w") as f:
        f.write("""Mixed Format Document

JSON Data:
{"id": 1, "status": "active"}

HTML Table:
<table>
  <tr><th>Product</th><th>Price</th></tr>
  <tr><td>Widget</td><td>$10.99</td></tr>
  <tr><td>Gadget</td><td>$25.50</td></tr>
</table>

CSV-like data:
Product,Quantity,Price
Apple,10,1.50
Banana,5,0.75
""")


if __name__ == "__main__":
    print("Generating test data...")
    generate_tier_a()
    generate_tier_b()
    print("Test data generated successfully!")