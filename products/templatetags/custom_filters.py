from django import template

register = template.Library()

# Custom filter to multiply the value by the rate
@register.filter
def multiply(value, arg):
    try:
        result = float(value) * float(arg)
        return f"{result:.2f}"  # Format result to 2 decimal places
    except (ValueError, TypeError):
        return "0.00"  # Return default value in case of error
