import json
import os
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from serpapi import GoogleSearch



SERPAPI_KEY = os.getenv("SERPAPI_KEY")
GOOGLE_CREDS_FILE = "product-support-463118-9cfaa594d984.json"
PREFERENCES_FILE = "preferences.json"

# Gemini Initialization (GPT imitation for text analysis)
# If you want to use a real Gemini API, uncomment the following lines
# and insert your API key. Otherwise, the built-in simulation will be used.
# try:
#     genai.configure(api_key="YOUR_GEMINI_API_KEY") # !!! Insert your Gemini API key here if you want to use it !!!
#     model = genai.GenerativeModel('gemini-pro')
# except Exception as e:
#     print(f"[WARN] Failed to initialize Gemini model: {e}. Using built-in simulation.")
#     model = None # Set to None if initialization failed

# Load saved user preferences
if os.path.exists(PREFERENCES_FILE):
    with open(PREFERENCES_FILE, "r", encoding="utf-8") as f:
        SAVED_PREFERENCES = json.load(f)
else:
    SAVED_PREFERENCES = {}

# ------------------------
# Helper Functions
# ------------------------
def prompt_yes_no(prompt):
    """Convenient 'yes/no' input."""
    while True:
        response = input(prompt + " (yes/no): ").strip().lower()
        if response in ["yes", "y"]:
            return True
        elif response in ["no", "n"]:
            return False
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

def simulate_llm_summarize(category, text_context=""):
    """
    Simulates text summarization using an LLM (e.g., Gemini/GPT).
    Adapted for different categories.
    """
    # If a real Gemini model is initialized (and uncommented above)
    # if 'model' in globals() and model:
    #     try:
    #         response = model.generate_content(f"Summarize the key features and trade-offs for a {category} based on this context: {text_context}")
    #         return response.text
    #     except Exception as e:
    #         print(f"[ERROR] LLM summarization failed: {e}. Using built-in simulation.")

    # Built-in simulation
    if category == "laptop":
        return """Key features and trade-offs (for laptops):
        When choosing a laptop, buyers often pay attention to:
        - **Processor (CPU)**: The heart of the laptop, affects overall performance.
        - **Random Access Memory (RAM)**: Important for multitasking and running "heavy" applications.
        - **Storage (SSD/HDD)**: Speed (SSD is much faster) and data storage capacity.
        - **Graphics Card (GPU)**: Critical for gaming, graphic design, and video editing.
        - **Display**: Size, resolution, panel type (IPS for better color reproduction), brightness.
        - **Battery Life**: How long the laptop can run on a single charge.
        - **Ports**: Availability of necessary connectors (USB-C, HDMI, Thunderbolt, etc.).
        - **Weight and Portability**: Important for those who often carry their laptop.
        - **Price**: Performance to cost ratio.
        - **Build Quality and Casing Materials**: Affects durability and appearance."""
    elif category == "smartphone":
        return """Key features and trade-offs (for smartphones):
        When choosing a smartphone, buyers often pay attention to:
        - **Camera**: Photo and video quality, number of modules, optical stabilization.
        - **Processor**: Speed of applications, games, and overall system responsiveness.
        - **Screen**: Size, type (AMOLED/LCD), resolution, refresh rate.
        - **Battery**: Capacity and operating time on a single charge, charging speed.
        - **Memory**: Built-in (for file storage) and RAM (for multitasking).
        - **Operating System**: Android or iOS.
        - **Design and Casing Materials**: Appearance, tactile feel, water protection.
        - **Network Support**: 5G availability.
        - **Price**: Ratio of characteristics to cost."""
    elif "composter" in category: # Includes "composter" and "kitchen composter"
         return """Key features and trade-offs (for composters):
        When choosing a composter, buyers often discuss the following aspects:
        - **Bin Size**: Affects the amount of waste that can be processed at once.
        - **Quietness**: Critical if the device is intended for indoor use.
        - **Cycle Time**: How long it takes to process a batch of waste.
        - **Odor Control**: One of the most important factors for home composters (filters, ventilation).
        - **Energy Use**: Long-term electricity costs with continuous use.
        - **Maintenance**: How easy it is to clean the device, change filters, or other consumables.
        - **Subscription Model**: Some devices require regular purchases of additives or filters via subscription."""
    else:
        return f"Key features and trade-offs (simulation for {category}): There are no specific details for this category. General aspects include performance, price, durability, and ease of use."

def simulate_llm_extract_features(product_title, description=""):
    """
    Simulates product feature extraction using an LLM (e.g., Gemini/GPT).
    Adapted for general and specific attributes.
    """
    # If a real Gemini model is initialized (and uncommented above)
    # if 'model' in globals() and model:
    #     try:
    #         response = model.generate_content(f"Extract key attributes and their values from this product title and description. Return as a JSON string with attribute: value pairs. Title: {product_title}. Description: {description}")
    #         return json.loads(response.text)
    #     except (json.JSONDecodeError, Exception) as e:
    #         print(f"[WARN] LLM returned invalid JSON or an error occurred: {e} for {product_title}. Using built-in simulation.")

    features = {}
    title_lower = product_title.lower()
    description_lower = description.lower()

    # General attributes
    if "electric" in title_lower or "электрический" in description_lower:
        features["electric"] = True
    if "quiet" in title_lower or "бесшумный" in description_lower or "silent" in description_lower:
        features["quietness"] = True
    if "wireless" in title_lower or "беспроводной" in description_lower:
        features["wireless"] = True
    if "waterproof" in title_lower or "водонепроницаемый" in description_lower:
        features["waterproof"] = True
    if "compact" in title_lower or "компактный" in description_lower:
        features["compact"] = True
    if "portable" in title_lower or "портативный" in description_lower:
        features["portable"] = True
    if "durable" in title_lower or "долговечный" in description_lower:
        features["durable"] = True
    
    # Attributes for laptops
    if any(cpu_brand in title_lower for cpu_brand in ["intel", "amd"]) and \
       any(cpu_model in title_lower for cpu_model in ["i3", "i5", "i7", "i9", "ryzen 3", "ryzen 5", "ryzen 7", "ryzen 9"]):
        if "i3" in title_lower: features["cpu"] = "intel i3"
        elif "i5" in title_lower: features["cpu"] = "intel i5"
        elif "i7" in title_lower: features["cpu"] = "intel i7"
        elif "i9" in title_lower: features["cpu"] = "intel i9"
        elif "ryzen 3" in title_lower: features["cpu"] = "amd ryzen 3"
        elif "ryzen 5" in title_lower: features["cpu"] = "amd ryzen 5"
        elif "ryzen 7" in title_lower: features["cpu"] = "amd ryzen 7"
        elif "ryzen 9" in title_lower: features["cpu"] = "amd ryzen 9"
        elif "ryzen" in title_lower: features["cpu"] = "amd ryzen"
        elif "intel" in title_lower: features["cpu"] = "intel"

    if "4gb ram" in title_lower or "4гб озу" in description_lower: features["ram"] = "4gb"
    elif "8gb ram" in title_lower or "8гб озу" in description_lower: features["ram"] = "8gb"
    elif "16gb ram" in title_lower or "16гб озу" in description_lower: features["ram"] = "16gb"
    elif "32gb ram" in title_lower or "32гб озу" in description_lower: features["ram"] = "32gb"

    if "128gb ssd" in title_lower or "128гб ssd" in description_lower: features["storage"] = "128gb ssd"
    elif "256gb ssd" in title_lower or "256гб ssd" in description_lower: features["storage"] = "256gb ssd"
    elif "512gb ssd" in title_lower or "512гб ssd" in description_lower: features["storage"] = "512gb ssd"
    elif "1tb ssd" in title_lower or "1тб ssd" in description_lower: features["storage"] = "1tb ssd"
    elif "hdd" in title_lower or "жесткий диск" in description_lower: features["storage_type"] = "hdd"

    if "nvidia" in title_lower or "geforce" in title_lower or "rtx" in title_lower or "radeon" in title_lower:
        features["gpu"] = "dedicated"
    elif "integrated graphics" in description_lower or "intel iris" in description_lower:
        features["gpu"] = "integrated"

    if "13 inch" in title_lower or "13\"" in title_lower: features["screen_size"] = "13 inch"
    elif "14 inch" in title_lower or "14\"" in title_lower: features["screen_size"] = "14 inch"
    elif "15 inch" in title_lower or "15\"" in title_lower: features["screen_size"] = "15 inch"
    elif "17 inch" in title_lower or "17\"" in title_lower: features["screen_size"] = "17 inch"
    if "touchscreen" in title_lower or "сенсорный экран" in description_lower: features["touchscreen"] = True
    if "4k" in title_lower or "uhd" in description_lower: features["resolution"] = "4k"
    elif "full hd" in title_lower or "fhd" in description_lower: features["resolution"] = "full hd"

    if "long battery life" in description_lower or "10+ hours" in description_lower: features["battery_life"] = "long"
    
    # Attributes for composters
    if "large capacity" in title_lower or "большая емкость" in description_lower or "10l" in description_lower:
        features["bin_size"] = "large"
    elif "compact" in title_lower or "маленький" in title_lower or "small" in title_lower:
        features["bin_size"] = "small"
    if "odor control" in title_lower or "контроль запаха" in description_lower or "odorless" in description_lower:
        features["odor_control"] = True
    if "no subscription" in title_lower or "без подписки" in description_lower:
        features["subscription_required"] = False
    
    return features

# ------------------------
# Search Products in Google Shopping
# ------------------------
def search_google_products(category, keywords=[], attributes={}):
    """
    Searches for products on Google Shopping, filtering by keywords and simulating attribute filtering.
    """
    search_term = category + " " + " ".join(keywords)
    params = {
        "engine": "google",
        "q": search_term.strip(),
        "tbm": "shop",  # Google Shopping
        "api_key": SERPAPI_KEY
    }

    print(f"\n[DEBUG] Performing search query: '{search_term}'")

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        print(f"\n[DEBUG] Raw SerpAPI Response: {json.dumps(results, indent=2, ensure_ascii=False)}")

        products = results.get("shopping_results", [])
        print(f"\n[DEBUG] Products found: {len(products)}")

        filtered = []
        for p in products:
            title = p.get("title", "")
            description = p.get("snippet", "") # Using snippet as description for attribute extraction

            # Check by main keywords
            if keywords:
                if not all(word.lower() in title.lower() or word.lower() in description.lower() for word in keywords):
                    continue

            # Simulate LLM product feature categorization and filtering
            product_attributes = simulate_llm_extract_features(title, description)
            
            # Check if product matches explicit user attributes
            match_attributes = True
            for attr_key, attr_value in attributes.items():
                if attr_key not in product_attributes or product_attributes[attr_key] != attr_value:
                    match_attributes = False
                    break
            if not match_attributes:
                continue

            filtered.append({
                "name": p.get("title"),
                "price": p.get("extracted_price", "N/A"),
                "url": p.get("link"),
                "source": p.get("source"),
                "image": p.get("thumbnail"),
                "attributes": product_attributes # Add extracted attributes for later use
            })

        print(f"[DEBUG] After filtering: {len(filtered)}")
        return filtered

    except Exception as e:
        print(f"[ERROR] Error during Google Shopping search: {e}")
        return []

# ------------------------
# Export to Google Sheets (Story A3, Story B5)
# ------------------------
def export_to_gsheet(data, sheet_name="Shopping Results"):
    """Exports data to a Google Sheet."""
    if not data:
        print("[!] No data to export.")
        return

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDS_FILE, scope)
    client = gspread.authorize(creds)

    try:
        # Check if a sheet with this name already exists
        spreadsheet = client.open(sheet_name)
        print(f"[ℹ️] Updating existing Google Sheet: {spreadsheet.url}")
    except gspread.exceptions.SpreadsheetNotFound:
        # If not, create a new one
        spreadsheet = client.create(sheet_name)
        print(f"[✔] New Google Sheet created: {spreadsheet.url}")
    
    sheet = spreadsheet.sheet1 # Get the first sheet
    sheet.clear() # Clear the sheet before writing new data

    # Prepare headers, including all unique attributes
    base_headers = ["name", "price", "url", "source", "image"]
    all_attributes_keys = set()
    for item in data:
        if "attributes" in item:
            all_attributes_keys.update(item["attributes"].keys())
    
    final_headers = base_headers + sorted(list(all_attributes_keys)) # Attributes in columns

    sheet.insert_row(final_headers, 1)

    # Populate data
    for row_data in data:
        row_values = []
        for header in final_headers:
            if header in row_data:
                row_values.append(str(row_data[header]))
            elif "attributes" in row_data and header in row_data["attributes"]:
                row_values.append(str(row_data["attributes"][header]))
            else:
                row_values.append("") # Empty string if attribute is missing
        sheet.append_row(row_values)

    print(f"[✔] Google Sheet successfully updated/created: {spreadsheet.url}")


# ------------------------
# Save User Preferences (Story M1, M3)
# ------------------------
def save_preferences(category, preferences, note=None):
    """Saves user preferences by category."""
    SAVED_PREFERENCES[category] = {
        "preferences": preferences,
        "timestamp": datetime.now().isoformat(),
        "note": note or ""
    }
    with open(PREFERENCES_FILE, "w", encoding="utf-8") as f:
        json.dump(SAVED_PREFERENCES, f, indent=2, ensure_ascii=False)
    print(f"[✔] Preferences for '{category}' saved.")

# ------------------------
# Load Old Preferences (Story M2)
# ------------------------
def load_previous_preferences(category):
    """Loads saved preferences for a given category and asks the user."""
    if category in SAVED_PREFERENCES:
        data = SAVED_PREFERENCES[category]
        print(f"\n🔁 Found saved preferences for '{category}':")
        print("Preferences:", json.dumps(data["preferences"], indent=2, ensure_ascii=False))
        if data["note"]:
            print("📝 Previous note:", data["note"])
        
        confirm = prompt_yes_no("Use them again?")
        if confirm:
            return data["preferences"], data["note"]
        else:
            new_note = input("Enter a new note (e.g., 'For this search, quietness is important due to a new baby.') (optional): ").strip()
            return None, new_note # User declined to use old ones, but can enter a new note
    return None, None # No saved preferences

# ------------------------
# Workflow A: Targeted Search (User Knows What They Want)
# ------------------------
def targeted_search_workflow():
    """Implements Workflow A: Targeted Search."""
    category = input("Enter the product (e.g., kitchen composter, laptop): ").strip().lower()
    
    # Story A1: Describe a Clear Goal
    print("Now specify the attributes that are important to you (e.g., electric:true, quietness:true, subscription_required:false).")
    print("Enter one attribute at a time in 'key:value' format, or press Enter to finish.")
    print("You can also enter general keywords without ':'.")
    
    attributes = {}
    keywords = []
    while True:
        attr_input = input("Attribute or keyword (Enter to finish): ").strip()
        if not attr_input:
            break
        
        if ":" in attr_input:
            key, value_str = attr_input.split(":", 1)
            key = key.strip().lower()
            value_str = value_str.strip().lower()
            
            # Convert string values to booleans or numbers
            if value_str == 'true':
                attributes[key] = True
            elif value_str == 'false':
                attributes[key] = False
            elif value_str.isdigit():
                attributes[key] = int(value_str)
            else:
                attributes[key] = value_str
        else:
            keywords.append(attr_input.lower())

    print(f"\nYou are searching for: {category}")
    if keywords:
        print(f"With keywords: {', '.join(keywords)}")
    if attributes:
        print(f"With attributes: {attributes}")

    # Story A2: Agent Filters Products Based on Criteria (via Google Shopping)
    results = search_google_products(category, keywords, attributes)

    print("\n🔍 Found products:")
    if results:
        # Show only top 3-5, as specified in Story A3 details
        for i, p in enumerate(results[:min(5, len(results))]): # Display max 5
            print(f" {i+1}. {p['name']} | Price: {p['price']} | Store: {p['source']}\n    Link: {p['url']}")
            if p['attributes']:
                print(f"    Detected attributes: {p['attributes']}")
        
        # Story A3: Optional Spreadsheet Export
        if len(results) > 5 or prompt_yes_no("More results found. Do you want to get the full list in Google Sheets for comparison or exploration?"):
            export_to_gsheet(results, sheet_name=f"{category.replace(' ', '_')}_Targeted_Results_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    else:
        print("❌ No products found matching your criteria. Try changing your query.")
    
    combined_preferences = {"keywords": keywords, "attributes": attributes}
    return category, combined_preferences # Return for saving in main

# ------------------------
# Workflow B: Exploratory Search (User Doesn't Know What Matters)
# ------------------------
def exploratory_search_workflow():
    """Implements Workflow B: Exploratory Search."""
    # Story B1: Initial Exploration Prompt
    category = input("Enter a general product need (e.g., composter, laptop): ").strip().lower()
    print(f"\n🚀 Exploratory search for category: '{category}'")

    # Story B2: Agent Explores the Domain
    print("Agent is exploring the domain to understand what matters to buyers...")
    
    # Simulate web search and article summarization
    major_features_summary = simulate_llm_summarize(category)
    print(f"\nKey features to consider when choosing a {category}:\n{major_features_summary}")

    # Simulate getting a list of attributes with approximate importance
    suggested_attributes = {}
    if category == "laptop":
        suggested_attributes = {
            "cpu": "processor (overall performance)",
            "ram": "RAM (multitasking)",
            "storage": "storage (capacity and speed)",
            "gpu": "graphics card (gaming/graphics)",
            "screen_size": "screen size",
            "battery_life": "battery life",
            "ports": "ports (availability of needed connectors)",
            "weight": "weight and portability",
            "price": "price"
        }
    elif "composter" in category:
        suggested_attributes = {
            "bin_size": "bin size (for waste volume)",
            "quietness": "quietness (if silence is important)",
            "cycle_time": "cycle time (processing speed)",
            "energy_use": "energy consumption",
            "odor_control": "odor control",
            "maintenance": "maintenance",
            "subscription_required": "subscription required"
        }
    elif category == "smartphone":
         suggested_attributes = {
            "camera": "camera (photo/video quality)",
            "processor": "processor (operating speed)",
            "screen_type": "screen type (AMOLED/LCD)",
            "battery_capacity": "battery capacity",
            "storage_gb": "built-in storage (GB)",
            "os": "operating system (Android/iOS)",
            "5g_support": "5G support"
        }
    else: # General attributes if category not recognized
        suggested_attributes = {
            "price": "price",
            "quality": "build quality",
            "durability": "durability",
            "ease_of_use": "ease of use"
        }

    # Story B3: Ask User to Rank Their Priorities
    print("\nPlease rate the importance of the following attributes on a scale of 1 (not important) to 5 (very important):")
    user_priorities = {}
    for attr, description in suggested_attributes.items():
        while True:
            try:
                rating = int(input(f"Importance of '{description}' ({attr}): "))
                if 1 <= rating <= 5:
                    user_priorities[attr] = rating
                    break
                else:
                    print("Please enter a number between 1 and 5.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    print("\nYour priorities:", user_priorities)

    # Story B4: Return Best Matches Based on Learned Preferences
    print("\nSearching for the best matches based on your preferences...")
    
    # Collect all products that might be relevant (broad search by category)
    all_found_products = search_google_products(category)

    # Simulate weighted scoring
    scored_products = []
    for product in all_found_products:
        score = 0
        product_attrs = simulate_llm_extract_features(product["name"], product.get("description", ""))
        
        for user_attr, user_rating in user_priorities.items():
            if user_attr in product_attrs and product_attrs[user_attr] is not False and product_attrs[user_attr] is not None:
                score += user_rating 
        
        scored_products.append((score, product))
    
    scored_products.sort(key=lambda x: x[0], reverse=True)
    best_matches = [p for score, p in scored_products[:min(5, len(scored_products))]] # Display max 5

    print("\n✨ Best matches:")
    if best_matches:
        for i, p in enumerate(best_matches):
            print(f" {i+1}. {p['name']} | Price: {p['price']} | Store: {p['source']}\n    Link: {p['url']}")
            if p['attributes']:
                print(f"    Detected attributes: {p['attributes']}")
        
        # Story B5: Auto-generate a Google Sheet if Results Are Plentiful
        if len(all_found_products) > 5 or prompt_yes_no("Many results found. Do you want to get the full list in Google Sheets for further exploration?"):
            export_to_gsheet(all_found_products, sheet_name=f"{category.replace(' ', '_')}_Exploratory_Results_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    else:
        print("❌ Could not find suitable products based on your preferences.")
    
    save_preferences(category, user_priorities)

# ------------------------
# Main Scenario
# ------------------------
def main():
    """Main function to run the Smart Shopping Concierge."""
    print("\n🤖 Welcome to Smart Shopping Concierge!")
    print("I can help you find products in two ways:")
    print("  1. Targeted Search (you know what you want and what attributes are important).")
    print("  2. Exploratory Search (you are unsure what matters and want to understand it).")

    while True:
        mode_choice = input("\nSelect mode (1 or 2, or 'exit' to quit): ").strip()

        if mode_choice == '1':
            category_input_for_recall = input("Enter the product category you want to search for (e.g., laptop, kitchen composter): ").strip().lower()
            
            reused_preferences, saved_note = load_previous_preferences(category_input_for_recall)
            
            if reused_preferences:
                print("✔ Using saved filters.")
                # Assume saved preferences for targeted search include 'keywords' and 'attributes'
                keywords_from_saved = reused_preferences.get("keywords", [])
                attributes_from_saved = reused_preferences.get("attributes", {})
                
                results = search_google_products(category_input_for_recall, keywords_from_saved, attributes_from_saved)
                
                if results:
                    print("\n🔍 Products found with saved filters:")
                    for i, p in enumerate(results[:min(5, len(results))]):
                        print(f" {i+1}. {p['name']} | Price: {p['price']} | Store: {p['source']}\n    Link: {p['url']}")
                        if p['attributes']:
                            print(f"    Detected attributes: {p['attributes']}")
                    if len(results) > 5 and prompt_yes_no("Export to Google Sheets?"):
                        export_to_gsheet(results, sheet_name=f"{category_input_for_recall.replace(' ', '_')}_Recalled_Results_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                else:
                    print("❌ No products found with saved filters. Perhaps the old criteria are too strict or the product is unavailable.")
                    if prompt_yes_no("Do you want to try a new targeted search for this category to update preferences?"):
                        category_from_new_search, new_preferences_from_search = targeted_search_workflow()
                        save_preferences(category_from_new_search, new_preferences_from_search, note=saved_note)
                    else:
                        print("Returning to main menu.")
            else: # If no saved preferences for the category or user declined them
                category_from_new_search, new_preferences_from_search = targeted_search_workflow()
                save_preferences(category_from_new_search, new_preferences_from_search, note=saved_note)
        
        elif mode_choice == '2':
            exploratory_search_workflow()
        
        elif mode_choice == 'exit':
            print("\n👋 Thank you for using Smart Shopping Concierge. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter '1', '2' or 'exit'.")

if __name__ == "__main__":
    main()