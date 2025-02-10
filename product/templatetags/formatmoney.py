from django import template

register = template.Library()

# def format_money(value):
#     try:
#         amount = float(value)
#
#     except ValueError:
#         return value
#
#     if int(amount) == amount:
#         amount = str(int(amount))
#         for i in range(len(amount)):
#             if i % 3 == 0 and i != 0:
#                 amount = amount[:i] + " " + amount[i:]
