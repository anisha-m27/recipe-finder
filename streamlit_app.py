import streamlit as st
import requests
import pandas as pd
import os
import base64

# Set up the page with title and icon
st.set_page_config(page_title="Recipe Finder", page_icon="🍴")

# Function to save login data
def save_login_data(username, password):
    data = {"Username": [username], "Password": [password]}
    df = pd.DataFrame(data)
    if os.path.exists("login_data.csv"):
        df_existing = pd.read_csv("login_data.csv")
        df = pd.concat([df_existing, df], ignore_index=True)
    df.to_csv("login_data.csv", index=False)

# Function to verify login credentials
def verify_login(username, password):
    if os.path.exists("login_data.csv"):
        df = pd.read_csv("login_data.csv")
        user_match = df[(df["Username"] == username) & (df["Password"] == password)]
        return not user_match.empty
    return False

# Function to convert the image to Base64 for embedding in CSS
def convert_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Login page logic with background image
def login_page():
    # Path to the background image for the login page
    background_image_path = "loginpage.png"  # Update with the correct path to your background image
    
    if not os.path.exists(background_image_path):
        st.error("Login background image not found. Please ensure the image is in the correct path.")
        return

    # Encode the background image in Base64
    encoded_image = convert_image_to_base64(background_image_path)

    # Apply custom CSS with Base64 image
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("data:image/png;base64,{encoded_image}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            color: #fff;
            font-family: 'Arial', sans-serif;
        }}
        .title {{
            font-size: 3em;
            font-weight: bold;
            color: #fff;
            text-align: center;
            padding: 20px 0;
            text-shadow: 2px 2px 5px #000;
        }}
        .login-container {{
            text-align: center;
            margin-top: 50px;
            background-color: rgba(0, 0, 0, 0.5);
            padding: 20px;
            border-radius: 10px;
            width: 300px;
            margin-left: auto;
            margin-right: auto;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # Login form
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="title">🔐 Login</h1>', unsafe_allow_html=True)
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if verify_login(username, password):
            st.success("Login successful! Redirecting to Recipe Finder...")
            st.session_state.logged_in = True
        else:
            st.error("Invalid credentials. Please try again.")

    # Option for new users to register
    if st.button("Register"):
        if username and password:
            save_login_data(username, password)
            st.success("Registration successful! You can now log in.")
        else:
            st.warning("Please enter both username and password to register.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Recipe Finder page logic
def recipe_finder_page():
    # Encode the background image in Base64
    background_image_path = "recipe.png"  # Path to your uploaded image
    encoded_image = convert_image_to_base64(background_image_path)

    # Apply custom CSS with Base64 image
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("data:image/png;base64,{encoded_image}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            color: #000;
            font-family: 'Arial', sans-serif;
        }}
        .title {{
            font-size: 3em;
            font-weight: bold;
            color: #fff;
            text-align: center;
            padding: 20px 0;
            text-shadow: 2px 2px 5px #000;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<h1 class="title">🍴 Recipe Finder</h1>', unsafe_allow_html=True)

    def get_recipes(ingredients, diet):
        api_key = st.secrets["api_Key"]
        url = "https://api.spoonacular.com/recipes/complexSearch"
        params = {
            "apiKey": api_key,
            "includeIngredients": ingredients,
            "diet": diet if diet != "None" else None,
            "number": 20,
            "addRecipeInformation": True,
            "sort": "random",
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Error fetching recipes. Please try again.")
            return {"results": []}

    ingredients = st.text_input("Enter ingredients (comma-separated, e.g., chicken, rice, broccoli): ")
    diet = st.selectbox("Dietary preferences", ["None", "Vegetarian", "Vegan", "Gluten-Free", "Ketogenic"])
    desired_servings = st.number_input("Enter the number of servings you need:", min_value=1, value=4)

    if st.button("Find Recipes", key="find_recipes_button", help="Click to find recipes"):
        if ingredients:
            response = get_recipes(ingredients, diet)
            results = response.get("results", [])

            if len(results) == 0:
                st.write("No recipes found. Try different ingredients.")
            else:
                recipes = []
                for result in results:
                    adjusted_servings = result["servings"]
                    adjustment_ratio = desired_servings / adjusted_servings
                    recipe_link = f'<a href="{result["sourceUrl"]}" target="_blank" class="recipe-title">{result["title"]}</a>'
                    recipes.append([recipe_link, result["readyInMinutes"], adjusted_servings, round(adjustment_ratio, 2)])

                df = pd.DataFrame(recipes, columns=["Recipe", "Ready in Minutes", "Original Servings", "Servings Adjustment Ratio"])
                st.markdown('<div class="table-container">', unsafe_allow_html=True)
                st.write("Here are some recipes based on your ingredients:")
                st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("Please enter at least one ingredient.")

# Main app logic
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    recipe_finder_page()
else:
    login_page()