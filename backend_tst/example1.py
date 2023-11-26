import random
import re


user_id = '7'
if not str(user_id).isdigit():
    print("Message: login in again, statusCode: 600")

email = 1
if email:
    print('yes')

gender_choice = ['Male', 'Female', 'Transgender']
choice = random.randint(0,2)

# print(gender_choice[choice])

x = 'amani-nation-Cr77aOsFmS0-unsplash.jpg'
pattern = r'([^\.]*)\.jpg'
replacement = r''+str(choice)+".jpg"
html = re.sub(pattern, replacement, x)
print(html)
print(re.sub(r'(\_a)?\.([^\.]*)$' , r'_suff.\2',"long.file.name.jpg"))

