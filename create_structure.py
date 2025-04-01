# import os


# files_to_create = [
#     "main.py",
#     "requirements.txt",
#     "README.md",
#     ".env",
#     "app/__init__.py",
#     "app/models/__init__.py",
#     "app/models/base.py",
#     "app/models/vendor.py",
#     "app/models/product.py",
#     "app/models/user.py",
#     "app/models/order.py",
#     "app/models/cart.py",
#     "app/models/payment.py",
#     "app/models/wishlist.py",  # Optional
#     "app/models/discount.py",   # Future feature
#     "app/services/__init__.py",
#     "app/services/db_manager.py",
#     "app/services/payment.py",
#     "app/routes/__init__.py",
#     "app/routes/vendor.py",
#     "app/routes/product.py",
#     "app/routes/order.py",
#     "app/routes/cart.py",
#     "app/routes/payment.py",
#     # Create placeholder files in empty directories
#     "app/templates/.keep",
#     "app/static/.keep",
#     "tests/unit/test_db_manager.py",
#     "tests/unit/test_routes.py",
#     "config/config.py",
# ]

# for file_path in files_to_create:
#     # Ensure the directory exists
#     directory = os.path.dirname(file_path)
#     if directory and not os.path.exists(directory):
#         os.makedirs(directory, exist_ok=True)
#     # Create the file if it does not exist
#     if not os.path.exists(file_path):
#         with open(file_path, "w") as f:
#             # Optionally, you can add a comment or leave it empty
#             f.write("# " + os.path.basename(file_path) + "\n")
            
# print("Project structure created successfully.")

import os
finalt = ""
for file in os.listdir("app/models"):
    if file.endswith('.py'):
        with open(os.path.join('app/models',file)) as f:
            text = f.readlines()
            fullt = "\n".join(text)

            finalt += f"\n{file}={fullt}"
print(finalt)
