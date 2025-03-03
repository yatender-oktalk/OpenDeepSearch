import re
from typing import List, Tuple
import fasttext
from huggingface_hub import hf_hub_download

# Load the model
model = fasttext.load_model(hf_hub_download("kenhktsui/llm-data-textbook-quality-fasttext-classifer-v2", "model.bin"))

def clean_markdown_links(text: str, min_quality_score: float = 0.2) -> Tuple[str, float]:
    """
    Clean markdown links and filter low-quality content.
    Returns tuple of (cleaned_text, quality_score)
    """
    # Split by double newlines to preserve paragraph structure
    paragraphs = text.split('\n\n')
    
    cleaned_paragraphs = []
    for paragraph in paragraphs:
        # Preserve code blocks by checking if paragraph contains ``` tags
        if '```' in paragraph:
            cleaned_paragraphs.append(paragraph)
            continue
            
        lines = paragraph.split('\n')
        filtered_lines = []
        for line in lines:
            line = line.strip()
            # Keep headers regardless of length
            if re.match(r'^#{1,6}\s+', line):
                filtered_lines.append(line)
                continue
            
            # Skip common UI/navigation elements
            if re.match(r'^(Share|Trade|More|Buy|Sell|Download|Menu|Home|Back|Next|Previous|\d+\s*(BTC|USD|EUR|GBP)|\w{3}-\w{1,3}|Currency:.*|You (Buy|Spend|Receive)|≈|\d+\.\d+)', line, re.IGNORECASE):
                continue
                
            # Count words before removing markdown
            word_count = len(re.sub(r'\[.*?\]\(.*?\)|!\[.*?\]\(.*?\)|<.*?>', '', line).split())
            
            # Increase minimum word threshold to 12
            if word_count < 12:
                # Check if line only contains markdown patterns or appears to be a currency/trading related line
                cleaned_line = re.sub(r'\[!\[.*?\]\(.*?\)\]\(.*?\)|\[.*?\]\(.*?\)|!\[.*?\]\(.*?\)|<.*?>|\d+(\.\d+)?%?|\$\d+(\.\d+)?', '', line).strip()
                if not cleaned_line or len(cleaned_line.split()) < 8:  # If nothing substantial remains, skip this line
                    continue
            
            filtered_lines.append(line)
        
        # Only add paragraph if it has any lines left
        if filtered_lines:
            cleaned_paragraphs.append('\n'.join(filtered_lines))
    
    # Rejoin with double newlines
    cleaned_text = '\n\n'.join(cleaned_paragraphs)
    
    # Get quality score
    quality_score = predict_educational_value([cleaned_text])[0]
    
    return cleaned_text, quality_score

def filter_quality_content(text: str, min_quality_score: float = 0.2) -> str:
    """
    Filter content based on quality and returns concatenated quality content
    """
    # Split text into paragraphs
    paragraphs = text.split('\n\n')
    
    # Process each paragraph
    quality_content = []
    for paragraph in paragraphs:
        if not paragraph.strip():  # Skip empty paragraphs
            continue
            
        cleaned_text, quality_score = clean_markdown_links(paragraph, min_quality_score)
        if cleaned_text and quality_score >= min_quality_score:
            quality_content.append((cleaned_text, quality_score))
    
    # Debug print
    print(f"Found {len(quality_content)} quality paragraphs out of {len(paragraphs)} total")
    
    if quality_content:
        return "\n\n".join(text for text, _ in quality_content)
    return text  # Return original text if no quality content found

def replace_newlines(text: str) -> str:
    """Replace multiple newlines with a single space."""
    return re.sub("\n+", " ", text)

score_dict = {
    '__label__': 0, 
    '__label__Low': 0, 
    '__label__Mid': 1,
    '__label__High': 2
}

def predict_educational_value(text_list: List[str]) -> List[float]:
    """
    Predict educational value scores for a list of texts.
    Returns a list of scores between 0 and 2.
    """
    text_list = [replace_newlines(text) for text in text_list]
    pred = model.predict(text_list, k=-1)
    score_list = []
    for l, s in zip(*pred):
        score = 0
        for _l, _s in zip(l, s):
            score += score_dict[_l] * _s
        score_list.append(float(score))
    return score_list
