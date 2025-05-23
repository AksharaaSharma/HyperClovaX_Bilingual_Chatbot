def display_liked_book_card(book, index):
  from streamlit_extras.colored_header import colored_header
  import base64
  from Frontend import add_custom_css
  from pymongo.errors import DuplicateKeyError
  import streamlit as st
  import requests
  import json
  from datetime import datetime
  from difflib import SequenceMatcher
  from streamlit_extras.add_vertical_space import add_vertical_space

    """Display a liked book card with a remove (cross) button using MongoDB."""
    info = book if isinstance(book, dict) else book.get("doc", {})
    with st.container():
        st.markdown('<div class="book-card" style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px;">', unsafe_allow_html=True)
        cols = st.columns([1, 3])
        with cols[0]:
            image_url = info.get("bookImageURL", "")
            if image_url:
                st.image(image_url, width=120)
            else:
                st.markdown("""
                <div style="width: 100px; height: 150px; background: linear-gradient(135deg, #2c3040, #363c4e); 
                            display: flex; align-items: center; justify-content: center; border-radius: 5px;">
                    <span style="color: #b3b3cc;">No Image</span>
                </div>
                """, unsafe_allow_html=True)
        with cols[1]:
            title = info.get('bookname') or info.get('bookName', '제목 없음')
            authors = info.get('authors') or info.get('author', '저자 없음')
            publisher = info.get('publisher', '출판사 없음')
            year = info.get('publication_year') or info.get('publicationYear', '연도 없음')
            loan_count = info.get('loan_count') or info.get('loanCount', 0)
            isbn13 = info.get('isbn13') or info.get('isbn', 'unknown')
            st.markdown(f"""
            <div style="padding-left: 10px;">
                <div style="font-size: 1.2em; font-weight: bold; color: #333; margin-bottom: 8px;">{title}</div>
                <div style="margin-bottom: 4px;"><strong>Author:</strong> {authors}</div>
                <div style="margin-bottom: 4px;"><strong>Publisher:</strong> {publisher}</div>
                <div style="margin-bottom: 4px;"><strong>Year:</strong> {year}</div>
                <div style="margin-bottom: 8px;"><strong>Loan Count:</strong> {loan_count}</div>
            </div>
            """, unsafe_allow_html=True)
            btn_col1, btn_col2 = st.columns([3, 1])
            with btn_col1:
                if st.button(f"Tell me more about this book", key=f"details_liked_{isbn13}_{index}"):
                    st.session_state.selected_book = info
                    st.session_state.app_stage = "discuss_book"
                    st.rerun()
            with btn_col2:
                # Remove (cross) button
                if st.button("❌", key=f"remove_{isbn13}_{index}", help="Remove from My Library"):
                    unlike_book_for_user(st.session_state.username, isbn13)
                    st.success("Removed from your library!")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

  # Add after MongoDB client initialization
def get_user_library_collection():
  from streamlit_extras.colored_header import colored_header
  import base64
  from Frontend import add_custom_css
  from pymongo.errors import DuplicateKeyError
  import streamlit as st
  import requests
  import json
  from datetime import datetime
  from difflib import SequenceMatcher
  from streamlit_extras.add_vertical_space import add_vertical_space

    client = st.session_state.db_client  # Already set in login.py
    db = client["Login_Credentials"]
    return db["user_libraries"]

def like_book_for_user(username, book_info):
  from streamlit_extras.colored_header import colored_header
  import base64
  from Frontend import add_custom_css
  from pymongo.errors import DuplicateKeyError
  import streamlit as st
  import requests
  import json
  from datetime import datetime
  from difflib import SequenceMatcher
  from streamlit_extras.add_vertical_space import add_vertical_space

    user_library = get_user_library_collection()
    isbn = book_info.get("isbn13")
    if not isbn:
        return False
    # First, try to add to existing document
    result = user_library.update_one(
        {"username": username},
        {"$addToSet": {"liked_books": book_info}}
    )
    # If no document was modified, create one with an empty array and add the book
    if result.matched_count == 0:
        user_library.update_one(
            {"username": username},
            {"$set": {"liked_books": [book_info], "username": username}},
            upsert=True
        )
    return True

def get_liked_books(username):
  from streamlit_extras.colored_header import colored_header
  import base64
  from Frontend import add_custom_css
  from pymongo.errors import DuplicateKeyError
  import streamlit as st
  import requests
  import json
  from datetime import datetime
  from difflib import SequenceMatcher
  from streamlit_extras.add_vertical_space import add_vertical_space

    user_library = get_user_library_collection()
    doc = user_library.find_one({"username": username})
    return doc.get("liked_books", []) if doc else []

def unlike_book_for_user(username, isbn):
  from streamlit_extras.colored_header import colored_header
  import base64
  from Frontend import add_custom_css
  from pymongo.errors import DuplicateKeyError
  import streamlit as st
  import requests
  import json
  from datetime import datetime
  from difflib import SequenceMatcher
  from streamlit_extras.add_vertical_space import add_vertical_space

    user_library = get_user_library_collection()
    user_library.update_one(
        {"username": username},
        {"$pull": {"liked_books": {"isbn13": isbn}}}
    )

def display_message(message):
  from streamlit_extras.colored_header import colored_header
  import base64
  from Frontend import add_custom_css
  from pymongo.errors import DuplicateKeyError
  import streamlit as st
  import requests
  import json
  from datetime import datetime
  from difflib import SequenceMatcher
  from streamlit_extras.add_vertical_space import add_vertical_space

    if message["role"] != "system":
        if message["role"] == "assistant":
            avatar = "AI"
            avatar_class = "assistant-avatar"
            message_class = "assistant-message"
            
            if "한국어 답변:" in message["content"]:
                parts = message["content"].split("한국어 답변:", 1)
                english_part = parts[0].strip()
                korean_part = parts[1].strip() if len(parts) > 1 else ""
                
                st.markdown(f"""
                <div class="message-with-avatar">
                    <div class="message-avatar {avatar_class}">{avatar}</div>
                    <div class="chat-message {message_class}">
                        {english_part}
                        <div class="korean-text">
                            <span class="korean-label">한국어 답변:</span><br>
                            {korean_part}
                        </div>
                        <div class="message-timestamp">Now</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="message-with-avatar">
                    <div class="message-avatar {avatar_class}">{avatar}</div>
                    <div class="chat-message {message_class}">
                        {message["content"]}
                        <div class="message-timestamp">Now</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            avatar = "You"
            avatar_class = "user-avatar"
            message_class = "user-message"
            
            st.markdown(f"""
            <div class="message-with-avatar">
                <div class="message-avatar {avatar_class}">{avatar}</div>
                <div class="chat-message {message_class}">
                    {message["content"]}
                    <div class="message-timestamp">Now</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def call_hyperclova_api(messages, api_key):
  from streamlit_extras.colored_header import colored_header
  import base64
  from Frontend import add_custom_css
  from pymongo.errors import DuplicateKeyError
  import streamlit as st
  import requests
  import json
  from datetime import datetime
  from difflib import SequenceMatcher
  from streamlit_extras.add_vertical_space import add_vertical_space

    """Helper function to call HyperCLOVA API with correct headers"""
    try:
        endpoint = "https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": messages,
            "maxTokens": 1024,
            "temperature": 0.7,
            "topP": 0.8,
        }
        
        response = requests.post(endpoint, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return result['result']['message']['content']
        else:
            st.error(f"Error connecting to HyperCLOVA API: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error connecting to HyperCLOVA API: {e}")
        return None

def display_book_card(book, index):
  from streamlit_extras.colored_header import colored_header
  import base64
  from Frontend import add_custom_css
  from pymongo.errors import DuplicateKeyError
  import streamlit as st
  import requests
  import json
  from datetime import datetime
  from difflib import SequenceMatcher
  from streamlit_extras.add_vertical_space import add_vertical_space

    """Display a book card with like functionality, using MongoDB for liked books."""
    # Handle both old format (direct keys) and new format (nested in 'doc')
    if "doc" in book:
        info = book["doc"]
    else:
        info = book

    with st.container():
        st.markdown('<div class="book-card" style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px;">', unsafe_allow_html=True)
        cols = st.columns([1, 3])
        with cols[0]:
            image_url = info.get("bookImageURL", "")
            if image_url:
                st.image(image_url, width=120)
            else:
                st.markdown("""
                <div style="width: 100px; height: 150px; background: linear-gradient(135deg, #2c3040, #363c4e); 
                            display: flex; align-items: center; justify-content: center; border-radius: 5px;">
                    <span style="color: #b3b3cc;">No Image</span>
                </div>
                """, unsafe_allow_html=True)
        with cols[1]:
            title = info.get('bookname') or info.get('bookName', '제목 없음')
            authors = info.get('authors') or info.get('author', '저자 없음')
            publisher = info.get('publisher', '출판사 없음')
            year = info.get('publication_year') or info.get('publicationYear', '연도 없음')
            loan_count = info.get('loan_count') or info.get('loanCount', 0)
            isbn13 = info.get('isbn13') or info.get('isbn', 'unknown')

            st.markdown(f"""
            <div style="padding-left: 10px;">
                <div style="font-size: 1.2em; font-weight: bold; color: #333; margin-bottom: 8px;">{title}</div>
                <div style="margin-bottom: 4px;"><strong>Author:</strong> {authors}</div>
                <div style="margin-bottom: 4px;"><strong>Publisher:</strong> {publisher}</div>
                <div style="margin-bottom: 4px;"><strong>Year:</strong> {year}</div>
                <div style="margin-bottom: 8px;"><strong>Loan Count:</strong> {loan_count}</div>
            </div>
            """, unsafe_allow_html=True)

            btn_col1, btn_col2 = st.columns([3, 1])
            with btn_col1:
                if st.button(f"Tell me more about this book", key=f"details_{isbn13}_{index}"):
                    st.session_state.selected_book = info
                    st.session_state.app_stage = "discuss_book"
                    st.rerun()
            with btn_col2:
                # Check if this book is already liked
                liked_books = get_liked_books(st.session_state.username)
                already_liked = any((b.get("isbn13") or b.get("isbn")) == isbn13 for b in liked_books)
                if already_liked:
                    st.button("❤️", key=f"liked_{isbn13}_{index}", help="Already in My Library", disabled=True)
                else:
                    if st.button("❤️", key=f"like_{isbn13}_{index}", help="Add to My Library"):
                        # Store the book in MongoDB with consistent ISBN field
                        book_data = info.copy()
                        book_data['isbn13'] = isbn13
                        like_book_for_user(st.session_state.username, book_data)
                        st.success("Added to your library!")
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- Load JSON files ---
@st.cache_resource
def load_dtl_kdc_json():
  from streamlit_extras.colored_header import colored_header
  import base64
  from Frontend import add_custom_css
  from pymongo.errors import DuplicateKeyError
  import streamlit as st
  import requests
  import json
  from datetime import datetime
  from difflib import SequenceMatcher
  from streamlit_extras.add_vertical_space import add_vertical_space

    """Load only the detailed KDC JSON file"""
    with open("dtl_kdc.json", encoding="utf-8") as f:
        dtl_kdc_dict = json.load(f)
    return dtl_kdc_dict

dtl_kdc_dict = load_dtl_kdc_json()

# --- Enhanced HyperCLOVA API Integration ---
def extract_keywords_with_hyperclova(user_input, api_key, dtl_kdc_dict):
  from streamlit_extras.colored_header import colored_header
  import base64
  from Frontend import add_custom_css
  from pymongo.errors import DuplicateKeyError
  import streamlit as st
  import requests
  import json
  from datetime import datetime
  from difflib import SequenceMatcher
  from streamlit_extras.add_vertical_space import add_vertical_space

    """Extract and match the most appropriate DTL KDC code using HyperCLOVA with two-step process"""
    if not api_key:
        return find_best_dtl_code_fallback(user_input, dtl_kdc_dict)
    
    # First attempt - exact keyword matching
    categories_list = []
    for code, label in dtl_kdc_dict.items():
        categories_list.append(f"- {code}: {label}")
    
    categories_text = "\n".join(categories_list)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # First prompt - look for exact keywords
    prompt_exact = f"""
다음은 전체 도서 분류 코드 목록입니다:
{categories_text}

사용자 입력: "{user_input}"

위의 전체 목록에서 사용자 입력과 정확히 일치하는 키워드나 분류명을 찾아주세요.
예를 들어:
- "영문학" → 영미문학 관련 코드
- "역사" → 역사 관련 코드  
- "소설" → 소설 관련 코드
- "철학" → 철학 관련 코드

정확한 일치가 있으면 해당 코드번호만 반환하세요. 정확한 일치가 없으면 "NO_EXACT_MATCH"를 반환하세요.
"""
    
    data_exact = {
        "messages": [
            {
                "role": "system",
                "content": "당신은 도서 분류 전문가입니다. 전체 분류 목록에서 정확한 키워드 일치를 찾아 코드번호만 반환합니다."
            },
            {
                "role": "user", 
                "content": prompt_exact
            }
        ],
        "maxTokens": 50,
        "temperature": 0.1,
        "topP": 0.5,
    }
    
    try:
        # First API call - exact matching
        response = requests.post(
            "https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003",
            headers=headers,
            json=data_exact,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            extracted_code = result['result']['message']['content'].strip()
            extracted_code = extracted_code.replace('"', '').replace("'", '').strip()
            
            # If exact match found and exists in dictionary
            if extracted_code != "NO_EXACT_MATCH" and extracted_code in dtl_kdc_dict:
                return extracted_code, dtl_kdc_dict[extracted_code]
            
            # If no exact match, try second attempt with similarity
            prompt_similar = f"""
사용자 입력: "{user_input}"

다음은 사용할 수 있는 도서 분류 코드들입니다:
{categories_text}

정확한 일치가 없으므로, 사용자 입력의 의미와 가장 유사한 분류 코드를 찾아주세요.
의미상 연관성을 고려하여 가장 적절한 코드를 선택하세요.

예를 들어:
- "책 추천" → 일반적인 문학이나 총류 관련 코드
- "경제 관련" → 경제학 관련 코드
- "건강" → 의학이나 건강 관련 코드
- "요리" → 요리, 음식 관련 코드

가장 유사한 코드번호만 반환하세요.
"""
            
            data_similar = {
                "messages": [
                    {
                        "role": "system",
                        "content": "당신은 도서 분류 전문가입니다. 의미적 유사성을 바탕으로 가장 적절한 분류 코드를 찾아 반환합니다."
                    },
                    {
                        "role": "user", 
                        "content": prompt_similar
                    }
                ],
                "maxTokens": 50,
                "temperature": 0.3,
                "topP": 0.7,
            }
            
            # Second API call - similarity matching
            response2 = requests.post(
                "https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003",
                headers=headers,
                json=data_similar,
                timeout=30
            )
            
            if response2.status_code == 200:
                result2 = response2.json()
                similar_code = result2['result']['message']['content'].strip()
                similar_code = similar_code.replace('"', '').replace("'", '').strip()
                
                if similar_code in dtl_kdc_dict:
                    return similar_code, dtl_kdc_dict[similar_code]
                else:
                    # Try to find partial matches
                    return find_best_dtl_code_fallback(user_input, dtl_kdc_dict, similar_code)
            else:
                return find_best_dtl_code_fallback(user_input, dtl_kdc_dict)
        else:
            st.warning(f"HyperCLOVA API error: {response.status_code}")
            return find_best_dtl_code_fallback(user_input, dtl_kdc_dict)
            
    except Exception as e:
        st.warning(f"Keyword extraction failed: {e}")
        return find_best_dtl_code_fallback(user_input, dtl_kdc_dict)

def find_best_dtl_code_fallback(user_query, dtl_kdc_dict, ai_suggested_code=None):
  from streamlit_extras.colored_header import colored_header
  import base64
  from Frontend import add_custom_css
  from pymongo.errors import DuplicateKeyError
  import streamlit as st
  import requests
  import json
  from datetime import datetime
  from difflib import SequenceMatcher
  from streamlit_extras.add_vertical_space import add_vertical_space

    """Fallback method to find the best matching DTL KDC code"""
    best_score = 0
    best_code = None
    best_label = ""
    
    # If AI suggested a code but it wasn't exact, try to find similar codes
    if ai_suggested_code:
        for code, label in dtl_kdc_dict.items():
            if ai_suggested_code in code or code in ai_suggested_code:
                return code, label
    
    # Original similarity matching
    for code, label in dtl_kdc_dict.items():
        # Check similarity with the label
        score = SequenceMatcher(None, user_query.lower(), label.lower()).ratio()
        
        # Also check if any word from user query is in the label
        user_words = user_query.lower().split()
        for word in user_words:
            if len(word) > 1 and word in label.lower():
                score += 0.3  # Boost score for word matches
        
        if score > best_score:
            best_score = score
            best_code = code
            best_label = label
    
    return best_code, best_label if best_score > 0.2 else (None, None)

def get_dtl_kdc_code(user_query, api_key=None):
  from streamlit_extras.colored_header import colored_header
  import base64
  from Frontend import add_custom_css
  from pymongo.errors import DuplicateKeyError
  import streamlit as st
  import requests
  import json
  from datetime import datetime
  from difflib import SequenceMatcher
  from streamlit_extras.add_vertical_space import add_vertical_space

    """Get DTL KDC code using HyperCLOVA or fallback method"""
    if api_key:
        try:
            code, label = extract_keywords_with_hyperclova(user_query, api_key, dtl_kdc_dict)
            if code and label:
                st.info(f"Found category: {label} (Code: {code})")
                return code, label
        except Exception as e:
            st.warning(f"HyperCLOVA extraction failed, using fallback: {e}")
    
    # Fallback to similarity matching
    code, label = find_best_dtl_code_fallback(user_query, dtl_kdc_dict)
    if code and label:
        st.info(f"Found category: {label} (Code: {code})")
        return code, label
    
    return None, None

# --- Query library API for books by DTL KDC code ---
def get_books_by_dtl_kdc(dtl_kdc_code, auth_key, page_no=1, page_size=10):
  from streamlit_extras.colored_header import colored_header
  import base64
  from Frontend import add_custom_css
  from pymongo.errors import DuplicateKeyError
  import streamlit as st
  import requests
  import json
  from datetime import datetime
  from difflib import SequenceMatcher
  from streamlit_extras.add_vertical_space import add_vertical_space

    """Get books using DTL KDC code"""
    url = "http://data4library.kr/api/loanItemSrch"
    params = {
        "authKey": auth_key,
        "startDt": "2000-01-01",
        "endDt": datetime.now().strftime("%Y-%m-%d"),
        "format": "json",
        "pageNo": page_no,
        "pageSize": page_size,
        "dtl_kdc": dtl_kdc_code  # Use dtl_kdc parameter
    }
    
    try:
        r = requests.get(url, params=params)
        if r.status_code == 200:
            response_data = r.json()
            
            # Check if response has the expected structure
            if "response" in response_data:
                docs = response_data["response"].get("docs", [])
                
                # Handle case where docs might be a single dict instead of list
                if isinstance(docs, dict):
                    docs = [docs]
                elif not isinstance(docs, list):
                    return []
                
                # Extract and clean book data
                books = []
                for doc in docs:
                    # Handle nested 'doc' structure if it exists
                    if "doc" in doc:
                        book_data = doc["doc"]
                    else:
                        book_data = doc
                    
                    # Extract book information with fallback values
                    book_info = {
                        "bookname": book_data.get("bookname", book_data.get("bookName", "Unknown Title")),
                        "authors": book_data.get("authors", book_data.get("author", "Unknown Author")),
                        "publisher": book_data.get("publisher", "Unknown Publisher"),
                        "publication_year": book_data.get("publication_year", book_data.get("publicationYear", "Unknown Year")),
                        "isbn13": book_data.get("isbn13", book_data.get("isbn", "")),
                        "loan_count": int(book_data.get("loan_count", book_data.get("loanCount", 0))),
                        "bookImageURL": book_data.get("bookImageURL", "")
                    }
                    books.append(book_info)
                
                # Sort by loan count (descending)
                books = sorted(books, key=lambda x: x["loan_count"], reverse=True)
                return books
            else:
                st.error(f"Unexpected API response structure: {response_data}")
                return []
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return []
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse API response: {e}")
        return []
    except Exception as e:
        st.error(f"Error processing API response: {e}")
        return []
    
    return []

# --- Sidebar (as provided) ---
def setup_sidebar():
  from streamlit_extras.colored_header import colored_header
  import base64
  from Frontend import add_custom_css
  from pymongo.errors import DuplicateKeyError
  import streamlit as st
  import requests
  import json
  from datetime import datetime
  from difflib import SequenceMatcher
  from streamlit_extras.add_vertical_space import add_vertical_space
    with st.sidebar:
        if st.button("My Liked Books"):
            st.session_state.app_stage = "show_liked_books"
            st.rerun()

        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h3 style="background: linear-gradient(90deg, #3b2314, #221409);
                      -webkit-background-clip: text;
                      -webkit-text-fill-color: transparent;
                      font-weight: 700;">
                API Configuration
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # API Keys section
        with st.container():
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            
            # HyperCLOVA API Key
            hyperclova_api_key = st.text_input("Enter your HyperCLOVA API Key", 
                                              type="password", 
                                              value=st.session_state.api_key)
            st.session_state.api_key = hyperclova_api_key
            
            # Library API Key
            library_api_key = st.text_input("Enter Library API Key", 
                                            type="password", 
                                            value=st.session_state.library_api_key)
            st.session_state.library_api_key = library_api_key
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Reset button
        if st.button("Start Over 💫"):
            st.session_state.messages = [
                {"role": "system", "content": "You are a helpful AI assistant specializing in book recommendations. For EVERY response, you must answer in BOTH English and Korean. First provide the complete answer in English, then provide '한국어 답변:' followed by the complete Korean translation of your answer."}
            ]
            st.session_state.app_stage = "welcome"
            st.session_state.user_genre = ""
            st.session_state.user_age = ""
            st.session_state.selected_book = None
            st.session_state.showing_books = False
            st.rerun()
        
        st.markdown("""
        <div style="text-align: center; margin-top: 30px; padding: 10px;">
            <p style="color: #b3b3cc; font-size: 0.8rem;">
                Powered by HyperCLOVA X & Korean Library API
            </p>
        </div>
        """, unsafe_allow_html=True)

# --- Process follow-up questions with HyperCLOVA ---
def process_followup_with_hyperclova(user_input, api_key):
  from streamlit_extras.colored_header import colored_header
  import base64
  from Frontend import add_custom_css
  from pymongo.errors import DuplicateKeyError
  import streamlit as st
  import requests
  import json
  from datetime import datetime
  from difflib import SequenceMatcher
  from streamlit_extras.add_vertical_space import add_vertical_space
  
    """Process follow-up questions using HyperCLOVA API"""
    if not api_key:
        return "Please provide your HyperCLOVA API key in the sidebar to get detailed responses.\n\n한국어 답변: 자세한 답변을 받으려면 사이드바에서 HyperCLOVA API 키를 제공해 주세요."
    
    # Create context from previous messages
    conversation_context = ""
    recent_messages = st.session_state.messages[-5:]  # Get last 5 messages for context
    for msg in recent_messages:
        if msg["role"] != "system":
            conversation_context += f"{msg['role']}: {msg['content']}\n"
    
    prompt = f"""
이전 대화 내용:
{conversation_context}

사용자의 새로운 질문: "{user_input}"

위의 맥락을 고려하여 사용자의 질문에 대해 도움이 되는 답변을 해주세요. 
만약 새로운 도서 추천을 요청하는 것 같다면, 구체적인 장르나 주제를 제시해주세요.

답변은 영어와 한국어 모두로 제공하되, 먼저 영어로 완전한 답변을 하고, 
그 다음 "한국어 답변:" 이후에 한국어 번역을 제공하세요.
"""
    
    messages = [
        {
            "role": "system",
            "content": "당신은 도서 추천 전문가입니다. 사용자와의 대화 맥락을 이해하고 도움이 되는 답변을 제공합니다. 항상 영어와 한국어로 답변하세요."
        },
        {
            "role": "user", 
            "content": prompt
        }
    ]
    
    return call_hyperclova_api(messages, api_key)

def generate_book_introduction(book, api_key):
  from streamlit_extras.colored_header import colored_header
  import base64
  from Frontend import add_custom_css
  from pymongo.errors import DuplicateKeyError
  import streamlit as st
  import requests
  import json
  from datetime import datetime
  from difflib import SequenceMatcher
  from streamlit_extras.add_vertical_space import add_vertical_space

    """Generate an introduction about the book when first selected"""
    title = book.get('bookname') or book.get('bookName', 'Unknown Title')
    authors = book.get('authors') or book.get('author', 'Unknown Author')
    publisher = book.get('publisher', 'Unknown Publisher')
    year = book.get('publication_year') or book.get('publicationYear', 'Unknown Year')
    loan_count = book.get('loan_count') or book.get('loanCount', 0)
    
    if not api_key:
        return f"Let's discuss '{title}' by {authors}! This book was published by {publisher} in {year} and has been borrowed {loan_count} times, showing its popularity. What would you like to know about this book - its themes, plot, writing style, or would you like similar recommendations?\n\n한국어 답변: {authors}의 '{title}'에 대해 이야기해 봅시다! 이 책은 {year}년에 {publisher}에서 출간되었으며 {loan_count}번 대출되어 인기를 보여줍니다. 이 책에 대해 무엇을 알고 싶으신가요 - 주제, 줄거리, 문체, 아니면 비슷한 추천을 원하시나요?"
    
    book_context = f"Book: {title} by {authors}, published by {publisher} in {year}, with {loan_count} loans"
    
    messages = [
        {
            "role": "system",
            "content": "You are a knowledgeable book expert. For EVERY response, answer in BOTH English and Korean. First provide complete English answer, then '한국어 답변:' with Korean translation. Provide an engaging introduction about the book."
        },
        {
            "role": "user", 
            "content": f"Please provide an engaging introduction about this book: {book_context}. Talk about what makes this book interesting, its potential themes, and invite the user to ask questions about it. Keep it conversational and welcoming."
        }
    ]
    
    response = call_hyperclova_api(messages, api_key)
    if response:
        return response
    else:
        # Fallback if API fails
        return f"Let's explore '{title}' by {authors}! This book from {publisher} ({year}) has {loan_count} loans, indicating its appeal to readers. I'm here to discuss anything about this book - from plot details to thematic analysis. What aspect interests you most?\n\n한국어 답변: {authors}의 '{title}'을 탐험해 봅시다! {publisher}({year})의 이 책은 {loan_count}번의 대출로 독자들에게 어필하고 있음을 보여줍니다. 줄거리 세부사항부터 주제 분석까지 이 책에 대한 모든 것을 논의할 준비가 되어 있습니다. 어떤 측면에 가장 관심이 있으신가요?"

def process_book_question(book, question, api_key, conversation_history):
  from streamlit_extras.colored_header import colored_header
  import base64
  from Frontend import add_custom_css
  from pymongo.errors import DuplicateKeyError
  import streamlit as st
  import requests
  import json
  from datetime import datetime
  from difflib import SequenceMatcher
  from streamlit_extras.add_vertical_space import add_vertical_space

    """Process specific questions about a book using HyperCLOVA with improved context handling"""
    if not api_key:
        return "Please provide your HyperCLOVA API key in the sidebar to get detailed responses about this book.\n\n한국어 답변: 이 책에 대한 자세한 답변을 받으려면 사이드바에서 HyperCLOVA API 키를 제공해 주세요."
    
    title = book.get('bookname') or book.get('bookName', 'Unknown Title')
    authors = book.get('authors') or book.get('author', 'Unknown Author')
    publisher = book.get('publisher', 'Unknown Publisher')
    year = book.get('publication_year') or book.get('publicationYear', 'Unknown Year')
    loan_count = book.get('loan_count') or book.get('loanCount', 0)
    
    # Build comprehensive conversation context
    context_string = ""
    if conversation_history:
        # Include more context - last 6 messages for better continuity
        recent_history = conversation_history[-6:] if len(conversation_history) >= 6 else conversation_history
        for msg in recent_history:
            role = "사용자" if msg["role"] == "user" else "AI"
            context_string += f"{role}: {msg['content']}\n\n"
    
    book_info = f"제목: '{title}', 저자: {authors}, 출판사: {publisher}, 출간년도: {year}, 인기도: {loan_count}회 대출"
    
    # Enhanced prompt with better context integration
    enhanced_prompt = f"""
현재 논의 중인 도서 정보:
{book_info}

이전 대화 내용:
{context_string}

사용자의 새로운 질문: "{question}"

위의 도서와 이전 대화 맥락을 모두 고려하여 사용자의 질문에 대해 상세하고 도움이 되는 답변을 제공해주세요.

답변 지침:
1. 이전 대화의 맥락을 참고하여 연속성 있는 답변을 제공하세요
2. 책의 내용, 주제, 등장인물, 문체, 문화적 배경 등에 대해 구체적으로 설명하세요
3. 필요시 유사한 책 추천도 포함하세요
4. 영어로 완전한 답변을 먼저 제공하고, 그 다음 "한국어 답변:" 이후에 한국어 번역을 제공하세요

답변은 상세하고 통찰력 있게 작성해주세요.
"""
    
    messages = [
        {
            "role": "system",
            "content": f"당신은 '{title}' by {authors}에 대해 논의하는 지식이 풍부한 도서 전문가입니다. 이전 대화의 맥락을 기억하고 연속성 있는 답변을 제공합니다. 모든 답변은 영어와 한국어 모두로 제공하며, 먼저 영어로 완전한 답변을 하고 그 다음 '한국어 답변:'으로 한국어 번역을 제공합니다. 도서의 주제, 줄거리 요소, 등장인물 분석, 문체, 문화적 맥락, 유사한 도서 추천 등을 포함한 상세하고 통찰력 있는 정보를 제공합니다."
        },
        {
            "role": "user",
            "content": enhanced_prompt
        }
    ]
    
    try:
        response = call_hyperclova_api(messages, api_key)
        if response:
            return response
        else:
            return f"I'd be happy to continue our discussion about '{title}', but I'm having trouble connecting to the AI service right now. Could you try asking your question again?\n\n한국어 답변: '{title}'에 대한 논의를 계속하고 싶지만 지금 AI 서비스에 연결하는 데 문제가 있습니다. 질문을 다시 해보시겠어요?"
    except Exception as e:
        st.error(f"Error processing question: {e}")
        return f"I encountered an error while processing your question about '{title}'. Please try rephrasing your question or check your API connection.\n\n한국어 답변: '{title}'에 대한 질문을 처리하는 중 오류가 발생했습니다. 질문을 다시 표현하거나 API 연결을 확인해 주세요."
