#!/usr/bin/env python3
"""
Panama Field Reports Streamlit App

A Streamlit application to display and interact with Panama field reports analysis results
from the Primer API.
"""

import streamlit as st
import json
import pandas as pd
import os
from pathlib import Path
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Import base64 image data
try:
    from entity_base64_images_simple import entity_base64_images_simple as entity_base64_images_complete
except ImportError:
    try:
        from entity_base64_images_complete import entity_base64_images_complete
    except ImportError:
        # Fallback if the file doesn't exist
        entity_base64_images_complete = {}

# Page configuration
st.set_page_config(
    page_title="Panama Field Reports Analysis",
    page_icon="🇵🇦",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_sentiment_data():
    """Load sentiment analysis results"""
    # Try multiple possible paths for the file
    possible_paths = [
        "panama_sentiment_results.json",
        "./panama_sentiment_results.json",
        "data/panama_sentiment_results.json"
    ]
    
    for file_path in possible_paths:
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                st.success(f"✅ Successfully loaded sentiment data from {file_path}")
                return data
        except FileNotFoundError:
            continue
        except json.JSONDecodeError as e:
            st.error(f"❌ Error parsing JSON from {file_path}: {e}")
            continue
    
    # If we get here, no file was found
    st.error("""
    ❌ **Sentiment results file not found!**
    
    **Possible solutions:**
    1. Make sure `panama_sentiment_results.json` is included in your GitHub repository
    2. Run the analysis scripts first: `python analyze_panama_reports.py`
    3. Check that the file is in the correct location
    
    **For Streamlit Cloud deployment:**
    - Ensure all data files are committed to your Git repository
    - The files should be in the root directory of your repository
    """)
    return None

def load_document_set_id():
    """Load document set ID"""
    # Try multiple possible paths for the file
    possible_paths = [
        "panama_document_set_id.txt",
        "./panama_document_set_id.txt",
        "data/panama_document_set_id.txt"
    ]
    
    for file_path in possible_paths:
        try:
            with open(file_path, "r") as f:
                doc_id = f.read().strip()
                st.success(f"✅ Successfully loaded document set ID from {file_path}")
                return doc_id
        except FileNotFoundError:
            continue
    
    st.warning("⚠️ Document set ID file not found. Some features may be limited.")
    return None

def extract_entities_from_sentiment_data(data):
    """Extract and organize entities from sentiment data"""
    if not data:
        return []
    
    # Define government roles for each entity
    entity_roles = {
        "José Raúl Mulino": "President of Panama",
        "Ana Rojas": "Defense Chief",
        "Carlos Méndez": "Minister of the Interior",
        "Marta Linares": "Vice President"
    }
    
    entities = []
    documents = data.get('documents', [])
    
    for doc in documents:
        doc_entities = doc.get('entities', {})
        for entity_id, entity_data in doc_entities.items():
            entity_name = entity_data.get('entity_name', 'Unknown')
            sentiment = entity_data.get('sentiment', 'neutral')
            entity_type = entity_data.get('entity_type', 'Unknown')
            
            # Get the government role for this entity
            government_role = entity_roles.get(entity_name, "Unknown Role")
            
            # Check if entity already exists
            existing_entity = next((e for e in entities if e['name'] == entity_name), None)
            
            if existing_entity:
                existing_entity['mention_count'] += 1
                # Update sentiment if different
                if sentiment != existing_entity['sentiment']:
                    existing_entity['sentiment'] = 'mixed'
            else:
                entities.append({
                    'name': entity_name,
                    'type': entity_type,
                    'sentiment': sentiment,
                    'mention_count': 1,
                    'government_role': government_role
                })
    
    return entities

def create_entity_dataframe(entities):
    """Create a pandas DataFrame from entities"""
    if not entities:
        return pd.DataFrame()
    
    df = pd.DataFrame(entities)
    df = df.sort_values('mention_count', ascending=False)
    return df

def display_entities_page():
    """Display the entities page"""
    st.title("🇵🇦 Panama Field Reports Analysis")
    st.markdown("---")
    
    # Load data
    sentiment_data = load_sentiment_data()
    doc_set_id = load_document_set_id()
    
    if not sentiment_data:
        st.error("No analysis data found. Please run the analysis scripts first.")
        return
    
    # Document set info
    if doc_set_id:
        st.info(f"**Document Set ID:** {doc_set_id}")
    
    # Extract entities
    entities = extract_entities_from_sentiment_data(sentiment_data)
    
    if not entities:
        st.warning("No entities found in the analysis results.")
        return
    
    # Create DataFrame
    df = create_entity_dataframe(entities)
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Entities", len(entities))
    
    with col2:
        negative_count = len([e for e in entities if e['sentiment'] == 'negative'])
        st.metric("Negative Sentiment", negative_count)
    
    with col3:
        positive_count = len([e for e in entities if e['sentiment'] == 'positive'])
        st.metric("Positive Sentiment", positive_count)
    
    with col4:
        total_mentions = sum(e['mention_count'] for e in entities)
        st.metric("Total Mentions", total_mentions)
    
    st.markdown("---")
    
    # Entity table
    st.subheader("📋 Identified Entities")
    st.markdown("**Table showing all government officials and entities identified in the Panama field reports with their sentiment analysis results.**")
    
    # Add a divider for better visual separation
    st.markdown("---")
    
    # Add sentiment color coding
    def color_sentiment(val):
        if val == 'negative':
            return 'background-color: #ffebee'
        elif val == 'positive':
            return 'background-color: #e8f5e8'
        else:
            return 'background-color: #f5f5f5'
    
    # Display styled table with title
    styled_df = df.style.map(color_sentiment, subset=['sentiment'])
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "name": st.column_config.TextColumn("Entity Name", width="medium"),
            "type": st.column_config.TextColumn("Entity Type", width="small"),
            "sentiment": st.column_config.TextColumn("Sentiment", width="small"),
            "mention_count": st.column_config.NumberColumn("Mention Count", width="small"),
            "government_role": st.column_config.TextColumn("Government Role", width="large")
        }
    )
    
    # Add caption below the table
    st.caption("💡 **Note**: All entities shown have negative sentiment, indicating criticism in the field reports. Color coding: 🔴 Negative sentiment, 🟢 Positive sentiment, ⚪ Neutral sentiment")
    
    # Entity type breakdown
    st.subheader("📊 Entity Type Distribution")
    
    type_counts = df['type'].value_counts()
    fig_type = px.pie(
        values=type_counts.values,
        names=type_counts.index,
        title="Entities by Type"
    )
    fig_type.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_type, use_container_width=True)
    
    # Sentiment distribution
    st.subheader("😊 Sentiment Distribution")
    
    sentiment_counts = df['sentiment'].value_counts()
    fig_sentiment = px.bar(
        x=sentiment_counts.index,
        y=sentiment_counts.values,
        title="Entities by Sentiment",
        color=sentiment_counts.index,
        color_discrete_map={
            'negative': '#ff6b6b',
            'positive': '#51cf66',
            'neutral': '#868e96',
            'mixed': '#ffd43b'
        }
    )
    fig_sentiment.update_layout(xaxis_title="Sentiment", yaxis_title="Count")
    st.plotly_chart(fig_sentiment, use_container_width=True)
    
    # Mention count visualization
    st.subheader("📈 Top Entities by Mention Count")
    
    top_entities = df.head(10)
    fig_mentions = px.bar(
        data_frame=top_entities,
        x='name',
        y='mention_count',
        color='sentiment',
        title="Top 10 Entities by Mention Count",
        color_discrete_map={
            'negative': '#ff6b6b',
            'positive': '#51cf66',
            'neutral': '#868e96',
            'mixed': '#ffd43b'
        }
    )
    fig_mentions.update_layout(
        xaxis_title="Entity Name",
        yaxis_title="Mention Count",
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig_mentions, use_container_width=True)
    
    # Detailed entity information
    st.subheader("🔍 Entity Details")
    
    selected_entity = st.selectbox(
        "Select an entity to view details:",
        options=df['name'].tolist(),
        index=0
    )
    
    if selected_entity:
        entity_info = next((e for e in entities if e['name'] == selected_entity), None)
        if entity_info:
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                # Display portrait image if available
                portrait_filename = f"{selected_entity.lower().replace(' ', '_').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')}_realistic.jpg"
                portrait_path = f"entity_images/{portrait_filename}"
                
                if os.path.exists(portrait_path):
                    st.image(portrait_path, caption=f"Portrait of {selected_entity}", use_column_width=True)
                else:
                    st.info("Portrait image not available")
            
            with col2:
                st.write(f"**Name:** {entity_info['name']}")
                st.write(f"**Type:** {entity_info['type']}")
                st.write(f"**Mention Count:** {entity_info['mention_count']}")
            
            with col3:
                sentiment_color = {
                    'negative': '🔴',
                    'positive': '🟢',
                    'neutral': '⚪',
                    'mixed': '🟡'
                }
                st.write(f"**Sentiment:** {sentiment_color.get(entity_info['sentiment'], '⚪')} {entity_info['sentiment'].title()}")
                st.write(f"**Government Role:** {entity_info['government_role']}")
                
            # Add disclaimer about portraits
            st.caption("💡 **Note**: Portrait images are AI-generated hypothetical representations for demonstration purposes only.")

def display_baseball_cards_page():
    """Display the baseball cards page with 3D flip animation"""
    st.title("🏟️ Panama Government Officials - Baseball Cards")
    st.markdown("---")
    
    # Instructions
    st.info("💡 **Click to flip any card for more information.**")
    
    # Load data
    sentiment_data = load_sentiment_data()
    if not sentiment_data:
        return
    
    # Extract entities
    entities = extract_entities_from_sentiment_data(sentiment_data)
    if not entities:
        st.warning("No entities found in the analysis data.")
        return
    
    # Instructions removed
    
    # Define additional entity information for baseball cards
    entity_details = {
        "José Raúl Mulino": {
            "department": "Executive Branch",
            "responsibilities": "Head of State, Chief Executive, Commander-in-Chief",
            "description": "President of Panama with executive authority over government operations"
        },
        "Ana Rojas": {
            "department": "Ministry of Defense",
            "responsibilities": "National Security, Military Operations, Defense Strategy",
            "description": "Defense Chief responsible for national security and military affairs"
        },
        "Carlos Méndez": {
            "department": "Ministry of the Interior",
            "responsibilities": "Domestic Affairs, Public Security, Law Enforcement",
            "description": "Minister of the Interior overseeing domestic affairs and public security"
        },
        "Marta Linares": {
            "department": "Executive Branch",
            "responsibilities": "Deputy Head of State, Executive Support",
            "description": "Vice President of Panama supporting executive functions"
        }
    }
    
    # Map entity names to realistic portrait filenames
    portrait_mapping = {
        "José Raúl Mulino": "jose_raul_mulino_realistic.jpg",
        "Ana Rojas": "ana_rojas_realistic.jpg",
        "Carlos Méndez": "carlos_mendez_realistic.jpg",
        "Marta Linares": "marta_linares_realistic.jpg"
    }
    
    # Create the HTML component with all cards
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
        .baseball-card {
            width: 280px;
            height: 380px;
            perspective: 1000px;
            margin: 15px;
            display: inline-block;
            vertical-align: top;
        }
        
        .card-inner {
            position: relative;
            width: 100%;
            height: 100%;
            text-align: center;
            transition: transform 0.8s;
            transform-style: preserve-3d;
            cursor: pointer;
        }
        
        .baseball-card.flipped .card-inner {
            transform: rotateY(180deg);
        }
        
        .card-front, .card-back {
            position: absolute;
            width: 100%;
            height: 100%;
            backface-visibility: hidden;
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 20px;
            box-sizing: border-box;
        }
        
        .card-front {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            border: 3px solid #1a252f;
        }
        
        .card-back {
            background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
            color: white;
            transform: rotateY(180deg);
            border: 3px solid #1a252f;
        }
        
        .card-portrait {
            width: 120px;
            height: 140px;
            object-fit: cover;
            border-radius: 8px;
            border: 2px solid white;
            margin-bottom: 12px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.2);
        }
        
        .card-name {
            font-size: 1.4em;
            font-weight: bold;
            margin-bottom: 8px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .card-role {
            font-size: 1.1em;
            opacity: 0.9;
            font-style: italic;
        }
        
        .card-stats {
            display: flex;
            justify-content: space-around;
            width: 100%;
            margin-top: 15px;
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-value {
            font-weight: bold;
            font-size: 1.2em;
        }
        
        .stat-label {
            font-size: 0.8em;
            opacity: 0.8;
        }
        
        .card-info {
            text-align: left;
            width: 100%;
            font-size: 0.9em;
        }
        
        .info-row {
            margin-bottom: 8px;
            padding: 3px 0;
            border-bottom: 1px solid rgba(255,255,255,0.2);
        }
        
        .info-label {
            font-weight: bold;
            font-size: 0.8em;
            color: #bdc3c7;
        }
        
        .info-value {
            font-size: 0.75em;
            margin-top: 2px;
        }
        
        .sentiment-badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 15px;
            font-size: 0.7em;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .sentiment-negative {
            background: #8b0000;
            color: white;
        }
        
        .sentiment-positive {
            background: #006400;
            color: white;
        }
        
        .sentiment-neutral {
            background: #696969;
            color: white;
        }
        
        .sentiment-mixed {
            background: #8b4513;
            color: white;
        }
        
        .card-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 15px;
            padding: 15px;
        }
        
        .flip-instruction {
            text-align: center;
            color: #7f8c8d;
            font-style: italic;
            margin: 20px 0;
            font-size: 1.1em;
        }
        </style>
    </head>
    <body>

        <div class="card-container">
    """
    
    # Generate cards HTML
    for i, entity in enumerate(entities):
        sentiment_emoji = {
            'negative': '🔴',
            'positive': '🟢',
            'neutral': '⚪',
            'mixed': '🟡'
        }.get(entity['sentiment'], '⚪')
        
        entity_detail = entity_details.get(entity['name'], {})
        
        # Use base64 image data if available, otherwise use placeholder
        portrait_src = entity_base64_images_complete.get(entity['name'], "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTUwIiBoZWlnaHQ9IjE4MCIgdmlld0JveD0iMCAwIDE1MCAxODAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxNTAiIGhlaWdodD0iMTgwIiBmaWxsPSIjYmRjM2M3Ii8+Cjx0ZXh0IHg9Ijc1IiB5PSI5MCIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjE0IiBmaWxsPSIjNjc3Nzc3IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj5Qb3J0cmFpdDwvdGV4dD4KPC9zdmc+")
        
        html_content += f"""
        <div class="baseball-card" id="card-{i}" onclick="flipCard({i})">
            <div class="card-inner">
                <!-- Front of card -->
                <div class="card-front">
                    <img src="{portrait_src}" alt="{entity['name']}" class="card-portrait">
                    <div class="card-name">{entity['name']}</div>
                    <div class="card-role">{entity['government_role']}</div>
                    <div class="card-stats">
                        <div class="stat-item">
                            <div class="stat-value">{entity['mention_count']}</div>
                            <div class="stat-label">Mentions</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{sentiment_emoji}</div>
                            <div class="stat-label">Sentiment</div>
                        </div>
                    </div>
                </div>
                
                <!-- Back of card -->
                <div class="card-back">
                    <div class="card-name">{entity['name']}</div>
                    <div class="card-info">
                        <div class="info-row">
                            <div class="info-label">Government Role</div>
                            <div class="info-value">{entity['government_role']}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">Department</div>
                            <div class="info-value">{entity_detail.get('department', 'Unknown')}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">Responsibilities</div>
                            <div class="info-value">{entity_detail.get('responsibilities', 'Unknown')}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">Mention Count</div>
                            <div class="info-value">{entity['mention_count']} times</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">Sentiment Analysis</div>
                            <div class="info-value">
                                <span class="sentiment-badge sentiment-{entity['sentiment']}">
                                    {sentiment_emoji} {entity['sentiment'].title()}
                                </span>
                            </div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">Description</div>
                            <div class="info-value">{entity_detail.get('description', 'No description available')}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
    
    html_content += """
        </div>
        <script>
        function flipCard(cardId) {
            const card = document.getElementById('card-' + cardId);
            card.classList.toggle('flipped');
        }
        </script>
    </body>
    </html>
    """
    
    # Display the HTML component with dynamic height
    st.components.v1.html(html_content, height=800, scrolling=True)
    
    # Disclaimer
    st.markdown("---")
    st.caption("""
    💡 **Note**: These are interactive baseball card-style representations of government officials identified in the Panama field reports analysis. 
    Portrait images are AI-generated hypothetical representations for demonstration purposes only.
    """)

def main():
    """Main function"""
    # Sidebar
    st.sidebar.title("🇵🇦 Panama Analysis")
    st.sidebar.markdown("---")
    
    # Navigation
    page = st.sidebar.selectbox(
        "Select a page:",
        ["Baseball Cards", "Entities", "Documents", "Analysis"],
        index=0  # Default to Baseball Cards (first option)
    )
    
    if page == "Baseball Cards":
        display_baseball_cards_page()
    elif page == "Entities":
        display_entities_page()
    elif page == "Documents":
        st.title("📄 Documents")
        st.write("Document analysis page - coming soon!")
    elif page == "Analysis":
        st.title("📊 Analysis")
        st.write("Advanced analysis page - coming soon!")

if __name__ == "__main__":
    main() 