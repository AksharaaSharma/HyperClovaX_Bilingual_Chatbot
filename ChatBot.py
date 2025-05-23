import streamlit as st
import requests
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

add_custom_css()

def display_liked_book_card(book, index):    
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
    client = st.session_state.db_client  # Already set in login.py
    db = client["Login_Credentials"]
    return db["user_libraries"]

def like_book_for_user(username, book_info):
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
    user_library = get_user_library_collection()
    doc = user_library.find_one({"username": username})
    return doc.get("liked_books", []) if doc else []

def unlike_book_for_user(username, isbn):
    user_library = get_user_library_collection()
    user_library.update_one(
        {"username": username},
        {"$pull": {"liked_books": {"isbn13": isbn}}}
    )

def display_message(message):
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
    """Helper function to call HyperCLOVA API"""
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

# --- Load only DTL_KDC JSON file ---
@st.cache_resource
def load_dtl_kdc_json():
    with open("dtl_kdc.json", encoding="utf-8") as f:
        dtl_kdc_dict = json.load(f)
    return dtl_kdc_dict

# --- Enhanced HyperCLOVA API Integration for Korean prompts ---
def extract_keywords_and_find_code_with_hyperclova(user_input, api_key):
    """Extract keywords and find best matching DTL_KDC code using HyperCLOVA for Korean prompts"""
    if not api_key:
        return None, None, None
    
    # Load DTL_KDC dictionary
    dtl_kdc_dict = load_dtl_kdc_json()
    
    # Create a formatted list of available categories for the prompt
    categories_text = "\n".join([f"- {label}" for label in dtl_kdc_dict.values()])
    
    prompt = f"""
사용자의 도서 요청을 분석하여 가장 적합한 도서 분류를 찾아주세요.

사용자 입력: "{user_input}"

다음은 사용할 수 있는 도서 분류 목록입니다:
{categories_text}

사용자가 요청한 내용을 분석하여:
1. 핵심 키워드를 추출하고
2. 위 분류 목록에서 가장 적합한 분류를 하나만 선택해주세요

답변 형식:
키워드: [추출된 핵심 키워드들]
분류: [선택된 분류명]

예시:
- "추리소설 추천해주세요" → 키워드: 추리, 소설 / 분류: 추리소설
- "역사에 관한 책이 궁금해요" → 키워드: 역사 / 분류: 한국사
- "아이들이 읽을 만한 책" → 키워드: 아동, 어린이 / 분류: 아동문학

정확히 위 형식으로만 답변해주세요.
"""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messages": [
            {
                "role": "system",
                "content": "당신은 한국어 도서 분류 전문가입니다. 사용자의 자연스러운 한국어 요청을 분석하여 가장 적합한 도서 분류를 찾아주는 역할을 합니다. 주어진 분류 목록에서만 선택하고, 정확한 형식으로 답변해야 합니다."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "maxTokens": 200,
        "temperature": 0.3,
        "topP": 0.8,
    }
    
    try:
        response = requests.post(
            "https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['result']['message']['content'].strip()
            
            # Parse the AI response
            keywords = ""
            selected_category = ""
            
            lines = ai_response.split('\n')
            for line in lines:
                if line.startswith('키워드:'):
                    keywords = line.replace('키워드:', '').strip()
                elif line.startswith('분류:'):
                    selected_category = line.replace('분류:', '').strip()
            
            # Find the DTL_KDC code for the selected category
            dtl_code = None
            for code, label in dtl_kdc_dict.items():
                if selected_category in label or label in selected_category:
                    dtl_code = code
                    break
            
            # If exact match not found, try fuzzy matching
            if not dtl_code:
                best_score = 0
                for code, label in dtl_kdc_dict.items():
                    score = SequenceMatcher(None, selected_category.lower(), label.lower()).ratio()
                    if score > best_score and score > 0.5:
                        best_score = score
                        dtl_code = code
                        selected_category = label
            
            return keywords, dtl_code, selected_category
            
        else:
            st.warning(f"HyperCLOVA API error: {response.status_code}")
            return None, None, None
            
    except Exception as e:
        st.warning(f"Keyword extraction failed: {e}")
        return None, None, None

# --- Modified function to use only DTL_KDC ---
def get_dtl_kdc_code(user_query, api_key=None):
    """Get DTL_KDC code using HyperCLOVA for natural language understanding"""
    
    if api_key:
        keywords, dtl_code, dtl_label = extract_keywords_and_find_code_with_hyperclova(user_query, api_key)
        
        if dtl_code and dtl_label:
            # Display extracted information without showing the code number
            st.info(f"추출된 키워드: {keywords}")
            st.info(f"선택된 분류: {dtl_label}")
            return dtl_code, dtl_label
        else:
            st.warning("적절한 도서 분류를 찾지 못했습니다. 다른 키워드로 시도해보세요.")
            return None, None
    
    # Fallback: direct matching with DTL_KDC if no API key
    dtl_kdc_dict = load_dtl_kdc_json()
    best_score = 0
    best_code = None
    best_label = ""
    
    for code, label in dtl_kdc_dict.items():
        score = SequenceMatcher(None, user_query.lower(), label.lower()).ratio()
        if score > best_score:
            best_score = score
            best_code = code
            best_label = label
    
    if best_score > 0.3:
        return best_code, best_label
    else:
        return None, None

# --- Modified API call function ---
def get_books_by_dtl_kdc(dtl_kdc_code, auth_key, page_no=1, page_size=10):
    """Get books using only DTL_KDC code"""
    url = "http://data4library.kr/api/loanItemSrch"
    params = {
        "authKey": auth_key,
        "startDt": "2000-01-01",
        "endDt": datetime.now().strftime("%Y-%m-%d"),
        "format": "json",
        "pageNo": page_no,
        "pageSize": page_size,
        "dtl_kdc": dtl_kdc_code  # Only use DTL_KDC
    }
    
    try:
        r = requests.get(url, params=params)
        if r.status_code == 200:
            response_data = r.json()
            
            if "response" in response_data:
                docs = response_data["response"].get("docs", [])
                
                if isinstance(docs, dict):
                    docs = [docs]
                elif not isinstance(docs, list):
                    return []
                
                books = []
                for doc in docs:
                    if "doc" in doc:
                        book_data = doc["doc"]
                    else:
                        book_data = doc
                    
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

# --- Main function ---
def main():

    # --- Initialize all session state variables before use ---
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
    if "library_api_key" not in st.session_state:
        st.session_state.library_api_key = ""
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "system",
            "content": (
                "You are a friendly AI assistant specializing in book recommendations. "
                "Start by greeting and asking about favorite books/authors/genres/age. "
                "For EVERY response, answer in BOTH English and Korean. "
                "First provide complete English answer, then '한국어 답변:' with Korean translation."
            )
        }]
    if "app_stage" not in st.session_state:
        st.session_state.app_stage = "welcome"
    if "books_data" not in st.session_state:
        st.session_state.books_data = []

    if "user_genre" not in st.session_state:
        st.session_state.user_genre = ""
    if "user_age" not in st.session_state:
        st.session_state.user_age = ""
    if "selected_book" not in st.session_state:
        st.session_state.selected_book = None
    if "showing_books" not in st.session_state:
        st.session_state.showing_books = False

    setup_sidebar()

    st.markdown("<h1 style='text-align:center;'>📚 Book Wanderer / 책방랑자</h1>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;'>Discover your next favorite read with AI assistance in English and Korean</div>", unsafe_allow_html=True)
    st.markdown("---")

    # --- Chat history ---
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            display_message(msg)

    # --- App stages ---
    if st.session_state.app_stage == "welcome":
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Hello! Tell me about your favourite books, author, genre, or age group. You can describe what you're looking for in natural language.\n\n한국어 답변: 안녕하세요! 좋아하는 책, 작가, 장르 또는 연령대에 대해 말씀해 주세요. 자연스러운 언어로 원하는 것을 설명해 주시면 됩니다."
        })
        st.session_state.app_stage = "awaiting_user_input"
        st.rerun()

    elif st.session_state.app_stage == "awaiting_user_input":
        user_input = st.text_input("Tell me about your favorite genre, author, or book (in Korean or English):", key="user_open_input")
        if st.button("Send", key="send_open_input"):
            if user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})
                st.session_state.app_stage = "process_user_input"
                st.rerun()

    elif st.session_state.app_stage == "process_user_input":
        user_query = st.session_state.messages[-1]["content"]
        dtl_code, dtl_label = get_dtl_kdc_code(user_query, st.session_state.api_key)
        if not kdc_code:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Sorry, I could not find a matching KDC code for your query. Please try describing your preferred genre more specifically (e.g., '소설', '역사', '과학', '자기계발').\n\n한국어 답변: 죄송합니다. 입력하신 내용과 일치하는 KDC 코드를 찾지 못했습니다. 원하시는 장르를 더 구체적으로 설명해 주세요 (예: '소설', '역사', '과학', '자기계발')."
            })
            st.session_state.app_stage = "awaiting_user_input"
            st.rerun()
        if st.session_state.library_api_key:
            books = get_books_by_dtl_kdc(dtl_code, st.session_state.library_api_key)
            if books:
                st.session_state.books_data = books
                intro_msg = (f"선택하신 '{dtl_label}' 분류의 인기 도서를 찾았습니다.\n\n"
                             f"I found popular books for the '{dtl_label}' category.")
                st.session_state.messages.append({"role": "assistant", "content": intro_msg})
                st.session_state.app_stage = "show_recommendations"
            else:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Sorry, no books found for {kdc_type.upper()} code '{kdc_code}' ({kdc_label}). Try a different genre or keyword.\n\n한국어 답변: {kdc_type.upper()} 코드 '{kdc_code}' ({kdc_label})에 해당하는 도서를 찾을 수 없습니다. 다른 장르나 키워드로 시도해 주세요."
                })
                st.session_state.app_stage = "awaiting_user_input"
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Library API key required. Please check sidebar.\n\n한국어 답변: 라이브러리 API 키가 필요합니다. 사이드바를 확인해 주세요."
            })
            st.session_state.app_stage = "awaiting_user_input"
        st.rerun()

    elif st.session_state.app_stage == "show_recommendations":
        add_vertical_space(2)
        st.markdown(
            """
            <h2 style='text-align: center; font-size: 2.2em; font-weight: bold;'>
                📚 Recommended Books
            </h2>
            """,
            unsafe_allow_html=True
        )

        for i, book in enumerate(st.session_state.books_data):
            display_book_card(book, i)
            
        follow_up = st.text_input("Ask about these books, or tell me another genre/author (in Korean or English):", key="follow_up_input")
        if st.button("Send", key="send_follow_up"):
            if follow_up:
                st.session_state.messages.append({"role": "user", "content": follow_up})
                st.session_state.app_stage = "process_user_input"
                st.rerun()

    elif st.session_state.app_stage == "show_liked_books":
        add_vertical_space(2)  # Adds two lines of vertical space above

        st.markdown(
            """
            <h2 style='text-align: center; font-size: 2.2em; font-weight: bold; margin-bottom: 0.5em;'>
                 ❤️ My Liked Books
            </h2>
            """,
            unsafe_allow_html=True
        )
        liked_books = get_liked_books(st.session_state.username)
        if liked_books:
            for i, book in enumerate(liked_books):
                display_liked_book_card(book, i)
        else:
            st.info("You have not liked any books yet. Start exploring recommendations to build your library!")
        if st.button("Back to Recommendations"):
            st.session_state.app_stage = "show_recommendations"
            st.rerun()


    elif st.session_state.app_stage == "discuss_book":
        if st.session_state.selected_book:
            book = st.session_state.selected_book
            st.subheader(f"📖 About: {book.get('bookname', 'Unknown Title')}")
            
            # Display detailed book information
            col1, col2 = st.columns([1, 2])
            with col1:
                if book.get("bookImageURL"):
                    st.image(book["bookImageURL"], width=200)
            with col2:
                st.write(f"**Author:** {book.get('authors', 'Unknown')}")
                st.write(f"**Publisher:** {book.get('publisher', 'Unknown')}")
                st.write(f"**Year:** {book.get('publication_year', 'Unknown')}")
                st.write(f"**ISBN:** {book.get('isbn13', book.get('isbn', 'N/A'))}")
                
            st.markdown("---")
            
            # Chat about the book
            discussion_input = st.text_input("Ask me anything about this book:", key="book_discussion")
            if st.button("Ask", key="ask_about_book"):
                if discussion_input:
                    # Here you could integrate with HyperCLOVA for book discussions
                    response = f"I'd be happy to discuss '{book.get('bookname')}' with you! This book by {book.get('authors')} seems interesting. What specifically would you like to know about it?\n\n한국어 답변: '{book.get('bookname')}'에 대해 기꺼이 이야기해 드리겠습니다! {book.get('authors')}의 이 책은 흥미로워 보입니다. 구체적으로 무엇을 알고 싶으신가요?"
                    st.write(response)
            
            if st.button("Back to Recommendations"):
                st.session_state.app_stage = "show_recommendations"
                st.rerun()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align:center; color: #888; font-size:0.9em;'>
        This application provides book recommendations based on your preferences using AI assistance.<br>
        All recommendations are available in both English and Korean.<br>
        Powered by Streamlit • Korean Library API • HyperCLOVA X
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
