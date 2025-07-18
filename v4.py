import streamlit as st
import pandas as pd
import base64
from openai import OpenAI
import openai
import os
from dotenv import load_dotenv

st.set_page_config(page_title="Acne Detection & Solution", layout="centered")



st.markdown(
    """
    <style>
    /* Apply gradient background to the entire app */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(325deg, rgba(13,13,103,1) 0%, rgba(0,77,117,1) 60%, rgba(0,172,222,1) 82%, rgba(3,202,250,1) 88%, rgba(0,205,255,1) 93%, rgba(19,187,221,1) 100%);
    }

    /* Apply light blue gradient to the sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(90deg, rgba(180, 220, 255, 1) 0%, rgba(140, 200, 255, 1) 50%, rgba(100, 180, 255, 1) 100%);
        color: black; /* Ensure text is readable */
    }

    /* Remove black top menu bar */
    header, [data-testid="stHeader"] {
        background: transparent;
    }
    </style>
    """,
    unsafe_allow_html=True
)



api_key = st.secrets["general"]["OPENAI_API_KEY"]

# Initialize OpenAI client
client = OpenAI(api_key=api_key)




CREDENTIALS_FILE = "user_credentials.csv"


def load_credentials():
    try:
        return pd.read_csv(CREDENTIALS_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["username", "email", "password", "security_question", "security_answer"])


def save_credentials(username, email, password, security_question, security_answer):
    credentials = load_credentials()
    new_user = pd.DataFrame({
        "username": [username], "email": [email],
        "password": [password],
        "security_question": [security_question],
        "security_answer": [security_answer]
    })
    updated_credentials = pd.concat([credentials, new_user], ignore_index=True)
    updated_credentials.to_csv(CREDENTIALS_FILE, index=False)


def authenticate_user(username, password):
    credentials = load_credentials()
    user = credentials[(credentials['username'] == username) & (credentials['password'] == password)]
    return not user.empty


def recover_password(email, security_answer):
    credentials = load_credentials()
    user = credentials[(credentials['email'] == email) & (credentials['security_answer'] == security_answer)]
    if not user.empty:
        return user['password'].values[0]
    return None


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def sign_up():
    st.title("Sign-Up")
    username = st.text_input("Enter your username")
    email = st.text_input("Enter your email")
    password = st.text_input("Enter your password", type="password")
    security_question = st.selectbox("Select a security question", [
        "What is your pet's name?", "What is your mother's maiden name?", "What is your favorite book?"])
    security_answer = st.text_input("Answer to security question")
    if st.button("Sign Up"):
        if username and email and password and security_answer:
            credentials = load_credentials()
            if "username" in credentials.columns and username in credentials["username"].values:
                st.error("Username already exists! Please choose another.")
            else:
                save_credentials(username, email, password, security_question, security_answer)
                st.success("Sign-Up Successful! Please proceed to login.")
        else:
            st.warning("Please fill in all fields.")


def login():
    st.title("Login")
    username = st.text_input("Enter your username")
    password = st.text_input("Enter your password", type="password")
    if st.button("Login"):
        if username and password:
            if authenticate_user(username, password):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success(f"Welcome back, {username}!")
            else:
                st.error("Invalid username or password!")
        else:
            st.warning("Please fill in all fields.")


def password_recovery():
    st.title("Password Recovery")
    email = st.text_input("Enter your registered email")
    security_answer = st.text_input("Answer to your security question")
    if st.button("Recover Password"):
        recovered_password = recover_password(email, security_answer)
        if recovered_password:
            st.success(f"Your password is: {recovered_password}")
        else:
            st.error("Incorrect email or security answer.")




def profile_setup():
    st.title("Profile Setup Page")

    if "profile_data" not in st.session_state:
        st.session_state["profile_data"] = None

    # Display saved profile data at the top
    if st.session_state["profile_data"]:
        st.subheader("Your Saved Profile")
        profile_data = st.session_state["profile_data"]
        st.write(f"**Name:** {profile_data['first_name']} {profile_data['last_name']}")
        st.write(f"**Age:** {profile_data['age']} ({profile_data['dob']})")
        st.write(f"**Gender:** {profile_data['gender']}")
        if profile_data["email"]:
            st.write(f"**Email:** {profile_data['email']}")
        st.write(f"**Skin Type:** {profile_data['skin_type']}")
        st.write(f"**Breakout Frequency:** {profile_data['acne_frequency']}")
        st.write(f"**Skin Concerns:** {', '.join(profile_data['concerns'])}")
        st.write(f"**Sensitive Skin:** {profile_data['sensitive_skin']}")
        st.write(f"**Skincare Routine:** {profile_data['skincare_routine']}")
        st.write(f"**Makeup Usage:** {profile_data['makeup_usage']}")
        if profile_data["allergies"]:
            st.write(f"**Allergies:** {profile_data['allergies']}")
        st.write(f"**Diet:** {profile_data['diet']}")
        st.write(f"**Water Intake:** {profile_data['water_intake']}")
        st.write(f"**Sleep Hours:** {profile_data['sleep_hours']}")
        st.markdown("---")

    # Profile setup form
    st.subheader("Basic Information")
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    age = st.number_input("Age", min_value=10, max_value=100, step=1)
    dob = st.date_input("Date of Birth")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    email = st.text_input("Email (Optional)")

    st.subheader("Skin-related Questions")
    skin_type = st.selectbox("What is your skin type?", ["Oily", "Dry", "Combination", "Sensitive", "Normal"])
    acne_frequency = st.selectbox("How often do you experience breakouts?", ["Rarely", "Occasionally", "Frequently", "Always"])
    concerns = st.multiselect("Do you have any specific skin concerns?", ["Acne", "Redness", "Dark Spots", "Large Pores", "Blackheads/Whiteheads"])
    sensitive_skin = st.radio("Is your skin prone to sensitivity?", ["Yes", "No"])
    skincare_routine = st.selectbox("What is your current skincare routine?", ["None", "Basic", "Extensive"])
    makeup_usage = st.selectbox("How often do you wear makeup?", ["Never", "Occasionally", "Daily"])
    allergies = st.text_area("Are there any known allergies or sensitivities to skincare products? (Optional)")

    st.subheader("Lifestyle Questions")
    diet = st.selectbox("How would you describe your diet?", ["Healthy", "Moderate", "Unhealthy"])
    water_intake = st.selectbox("On average, how much water do you drink daily?", ["Less than 1L", "1-2L", "More than 2L"])
    sleep_hours = st.selectbox("How many hours of sleep do you get per night?", ["Less than 5", "5-7", "More than 7"])

    if st.button("Save Profile"):
        st.session_state["profile_data"] = {
            "first_name": first_name,
            "last_name": last_name,
            "age": age,
            "dob": str(dob),
            "gender": gender,
            "email": email,
            "skin_type": skin_type,
            "acne_frequency": acne_frequency,
            "concerns": concerns,
            "sensitive_skin": sensitive_skin,
            "skincare_routine": skincare_routine,
            "makeup_usage": makeup_usage,
            "allergies": allergies,
            "diet": diet,
            "water_intake": water_intake,
            "sleep_hours": sleep_hours
        }
        st.success("Profile information saved successfully!")
        st.rerun()  # Refresh the page to display saved data at the top





def about_page():
    st.title("About Page")
    st.write("""
        This app provides AI-powered skincare analysis. Upload an image of your face, and our AI will analyze acne severity and recommend treatments based on your skin type and concerns.

        **AI Acne Detection & Solution**  
        The AI Acne Detection & Solution app is an intelligent, AI-powered skincare assistant designed to help users analyze and manage acne-related concerns with precision and accuracy. By leveraging cutting-edge image processing and deep learning algorithms, the app detects various types of acne, assesses their severity, and provides personalized skincare recommendations tailored to each user’s unique skin profile.

        **How It Works**  
        Users begin by uploading a clear image of their face, which the AI processes to identify acne types such as blackheads, whiteheads, papules, pustules, nodules, or cysts. The system also determines the stage of acne development, ranging from mild to severe. Based on this analysis, the app generates targeted skincare advice, recommending suitable products, skincare routines, and lifestyle modifications to improve overall skin health.

        **Personalized Experience**  
        To enhance accuracy and ensure recommendations align with individual needs, users can set up their **Profile Setup Page** by inputting details such as skin type (oily, dry, combination), frequency of breakouts, specific concerns (acne scars, blackheads, sensitivity), and age. This information allows the AI to refine its suggestions, ensuring a highly personalized approach to skincare management.

        **Educational Insights & AI-Powered Analysis**  
        Beyond acne detection, the app serves as an educational platform, helping users understand the factors contributing to their skin issues. It explains how different acne types develop, the impact of diet and lifestyle, and how specific ingredients in skincare products can either improve or worsen acne conditions. The **About Page** further elaborates on the AI-powered analysis process, breaking down how the model interprets facial features, detects acne severity, and generates expert-backed skincare solutions.

        **Seamless User Experience**  
        With a user-friendly interface and secure login system, the app ensures seamless navigation. Users can sign up, log in, and recover their passwords effortlessly. The AI-powered chatbot feature further enhances the experience by allowing users to ask skincare-related queries and receive instant, AI-generated responses.

        By combining state-of-the-art AI technology with dermatological insights, the **AI Acne Detection & Solution** app empowers users to take control of their skincare journey. Whether dealing with occasional breakouts or persistent acne, the app provides scientifically backed solutions to help users achieve healthier, clearer skin.
    """)





def privacy_policy():
    st.title("Privacy Policy")
    st.write("""
        **Introduction**  
        Welcome to our Privacy Policy page. Your privacy is critically important to us. This policy explains how we collect, use, and protect your personal information when using our application.

        **Data Collection**  
        - We collect personal information such as name, email, and contact details when you sign up.  
        - Usage data, such as device type, IP address, and interactions within the app, may also be recorded.  
        - Cookies and similar tracking technologies may be used to enhance your experience.

        **Data Usage**  
        - Your data is used to improve our services, provide customer support, and personalize user experience.  
        - We do not sell your personal data to third parties.  
        - Data may be shared with trusted partners for analytics and security purposes.

        **Data Storage & Security**  
        - Your information is securely stored using industry-standard encryption methods.  
        - We implement strict security measures to prevent unauthorized access.  

        **User Rights**  
        - You can request access, modification, or deletion of your personal data at any time.  
        - You can opt out of certain data collection practices by adjusting your app settings.  

        **Contact Information**  
        If you have any concerns about privacy, please contact us at support@example.com.  
    """)


def terms_and_conditions():
    st.title("Terms and Conditions")
    st.write("""
        **1. Introduction**  
        By using this application, you agree to comply with and be bound by the following terms and conditions.

        **2. User Responsibilities**  
        - You must be at least 18 years old to use the app.  
        - You agree not to use the app for illegal activities, including fraud, hacking, or spamming.  
        - You are responsible for maintaining the security of your account and credentials.  

        **3. Intellectual Property**  
        - All content within the application is protected by copyright laws.  
        - You may not reproduce, distribute, or modify any part of the app without permission.  

        **4. Limitation of Liability**  
        - We are not responsible for any data loss, service interruptions, or technical issues.  
        - The app is provided "as-is," and we do not guarantee uninterrupted service.  

        **5. Account Termination**  
        - We reserve the right to suspend or terminate your account if you violate any terms.  
        - Users may delete their accounts at any time by contacting support.  

        **6. Updates to Terms**  
        - These terms may be updated periodically. Continued use of the app signifies your acceptance of any changes.  

        **7. Contact Information**  
        For questions regarding these terms, please email us at support@example.com.  
    """)


def contact_us():
    st.title("Contact Us")
    st.write("""
        We are here to help! If you have any inquiries, concerns, or support requests, please reach out to us.  

        **Contact Details:**  
        - 📧 Email: support@example.com  
        - 📞 Phone: +92--------  
        - 📍 Address: ----Pakistan  

        Alternatively, you can use the form below to send us a direct message.
    """)

    email = st.text_input("Your Email")
    message = st.text_area("Your Message")

    if st.button("Submit"):
        if email and message:
            st.success("Your message has been submitted successfully! We will get back to you soon.")
        else:
            st.error("Please fill in all fields before submitting.")


def faq_page():
    st.title("Frequently Asked Questions (FAQ)")
    st.write("""
        Below are some common questions about our application.  

        **1. How do I create an account?**  
        - You can sign up using your email address on the registration page. Follow the prompts to complete the setup.  

        **2. What should I do if I forget my password?**  
        - Click on "Forgot Password" on the login page and follow the instructions to reset your password.  

        **3. How can I contact customer support?**  
        - You can email us at support@example.com or use the Contact Us form to submit a query.  

        **4. Is my data safe?**  
        - Yes, we use encryption and secure storage to protect your personal information.  

        **5. Can I delete my account?**  
        - Yes, you can request account deletion by contacting support@example.com.  

        **6. How often is the app updated?**  
        - We release updates regularly to improve functionality and security.  

        If you have a question that is not listed here, feel free to contact us.
    """)


def acne_analysis():
    st.title("📸 AI Acne Analyzer")
    st.write("Upload an image of your face, and our AI will analyze your acne and provide personalized skincare advice.")
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image_path = "uploaded_image.png"
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.image(image_path, caption="Uploaded Image", use_container_width=True)
        base64_image = encode_image(image_path)

        if st.button("Analyze Acne 🧴"):
            with st.spinner("Analyzing... Please wait."):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system",
                         "content": "You are an AI skincare assistant. Analyze acne severity based on the image and provide personalized skincare, dietary, and lifestyle recommendations."
                                    "you response should contain first the type of acne of specific part of face that you identified it. do not include in the image etc in your response"
                                    "you must provide the stage of the acne as well."
                                    "after that you should provide the solution."
                                    "Please note you only entertain the images that  have human face or have acne. you will not entertain any other images."},
                        {"role": "user", "content": [
                            {"type": "text", "text": "Here is the image."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                        ]},
                    ],
                )
                st.success("Analysis Complete!")
                st.subheader("AI Diagnosis & Skincare Advice:")
                st.write(response.choices[0].message.content)


# AI Dermatologist Page
def ai_dermatologist():
    st.title("🩺 Ask Anything to AI Dermatologist")

    # Initialize OpenAI client only once
    if "openai_client" not in st.session_state:
        st.session_state["openai_client"] = OpenAI(api_key=api_key)

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Display only user and assistant messages (not system message)
    for message in st.session_state["messages"]:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # User input field (should now be visible)
    user_input = st.chat_input("Ask your skin-related question...")

    if user_input:
        st.session_state["messages"].append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.spinner("Thinking..."):
            response = st.session_state["openai_client"].chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an AI Dermatologist. Answer skin-related questions accurately and professionally.you will not entertain any other question at all."},
                    *st.session_state["messages"]
                ],
                temperature=0.5,
                max_tokens=400
            )

        ai_response = response.choices[0].message.content
        st.session_state["messages"].append({"role": "assistant", "content": ai_response})

        with st.chat_message("assistant"):
            st.markdown(ai_response)



import streamlit as st

def main():
    st.sidebar.title("Navigation")

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if st.session_state["logged_in"]:
        # Logout button
        if st.sidebar.button("Logout 🚪"):
            st.session_state["logged_in"] = False
            st.rerun()

        # Page Navigation
        page = st.sidebar.radio("Select Page", ["Acne Analysis", "Profile Setup", "AI Dermatologist", "About Page",
                                                "Privacy Policy", "Terms and Conditions",
                                                "Contact Us", "FAQs"])
        if page == "Acne Analysis":
            acne_analysis()
        elif page == "Profile Setup":
            profile_setup()
        elif page == "AI Dermatologist":
            ai_dermatologist()
        elif page == "About Page":
            about_page()
        elif page == "Privacy Policy":
            privacy_policy()
        elif page == "Terms and Conditions":
            terms_and_conditions()
        elif page == "Contact Us":
            contact_us()
        elif page == "FAQs":
            faq_page()
    else:
        choice = st.sidebar.radio("Go to", ["Login", "Sign-Up", "Password Recovery"])
        if choice == "Login":
            login()
        elif choice == "Sign-Up":
            sign_up()
        else:
            password_recovery()


if __name__ == "__main__":
    main()
