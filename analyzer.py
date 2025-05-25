import re
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Set
from pathlib import Path

class TextAnalyzer:
    """Advanced text analysis for notes"""
    
    STOP_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'as', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do',
        'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must',
        'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
        'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our',
        'their', 'myself', 'yourself', 'himself', 'herself', 'itself', 'ourselves',
        'yourselves', 'themselves'
    }
    
    def __init__(self, include_stop_words: bool = False):
        self.include_stop_words = include_stop_words
    
    def analyze_word_frequency(self, content: str, min_length: int = 3, top_n: int = 20) -> List[Tuple[str, int]]:
        """Analyze word frequency in content"""
        # Clean and tokenize
        words = re.findall(r'\b[a-zA-Z]{%d,}\b' % min_length, content.lower())
        
        # Filter stop words if needed
        if not self.include_stop_words:
            words = [w for w in words if w not in self.STOP_WORDS]
        
        # Count frequencies
        word_counts = Counter(words)
        return word_counts.most_common(top_n)
    
    def find_key_phrases(self, content: str, min_words: int = 2, max_words: int = 4, top_n: int = 10) -> List[Tuple[str, int]]:
        """Extract key phrases (n-grams) from content"""
        # Clean content
        clean_content = re.sub(r'[^\w\s]', ' ', content.lower())
        words = clean_content.split()
        
        # Filter stop words
        words = [w for w in words if w not in self.STOP_WORDS and len(w) >= 3]
        
        phrases = []
        
        # Generate n-grams
        for n in range(min_words, max_words + 1):
            for i in range(len(words) - n + 1):
                phrase = ' '.join(words[i:i+n])
                phrases.append(phrase)
        
        # Count phrase frequencies
        phrase_counts = Counter(phrases)
        return phrase_counts.most_common(top_n)
    
    def analyze_readability(self, content: str) -> Dict[str, float]:
        """Calculate readability metrics"""
        # Basic text statistics
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        words = re.findall(r'\b\w+\b', content)
        syllables = sum(self._count_syllables(word) for word in words)
        
        if not sentences or not words:
            return {'sentences': 0, 'words': 0, 'avg_words_per_sentence': 0, 'avg_syllables_per_word': 0}
        
        avg_words_per_sentence = len(words) / len(sentences)
        avg_syllables_per_word = syllables / len(words)
        
        # Flesch Reading Ease Score
        flesch_score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
        flesch_score = max(0, min(100, flesch_score))  # Clamp between 0-100
        
        return {
            'sentences': len(sentences),
            'words': len(words),
            'syllables': syllables,
            'avg_words_per_sentence': round(avg_words_per_sentence, 2),
            'avg_syllables_per_word': round(avg_syllables_per_word, 2),
            'flesch_reading_ease': round(flesch_score, 1)
        }
    
    def _count_syllables(self, word: str) -> int:
        """Estimate syllable count in a word"""
        word = word.lower()
        if len(word) <= 3:
            return 1
        
        # Count vowel groups
        vowels = 'aeiouy'
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        # Handle silent e
        if word.endswith('e'):
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def analyze_sentiment_indicators(self, content: str) -> Dict[str, int]:
        """Find words that might indicate sentiment"""
        positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome',
            'love', 'like', 'enjoy', 'happy', 'pleased', 'satisfied', 'excited',
            'success', 'successful', 'achievement', 'accomplish', 'complete', 'done'
        }
        
        negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 'angry', 'upset',
            'frustrated', 'annoyed', 'disappointed', 'fail', 'failure', 'problem',
            'issue', 'bug', 'error', 'broken', 'difficult', 'hard', 'challenging'
        }
        
        urgent_words = {
            'urgent', 'asap', 'immediately', 'critical', 'important', 'priority',
            'deadline', 'due', 'emergency', 'fix', 'resolve', 'address'
        }
        
        words = re.findall(r'\b\w+\b', content.lower())
        
        return {
            'positive_indicators': len([w for w in words if w in positive_words]),
            'negative_indicators': len([w for w in words if w in negative_words]),
            'urgent_indicators': len([w for w in words if w in urgent_words])
        }
    
    def generate_text_insights(self, content: str) -> Dict:
        """Generate comprehensive text insights"""
        insights = {}
        
        # Word frequency
        word_freq = self.analyze_word_frequency(content, top_n=15)
        insights['top_words'] = word_freq
        
        # Key phrases
        key_phrases = self.find_key_phrases(content, top_n=8)
        insights['key_phrases'] = key_phrases
        
        # Readability
        readability = self.analyze_readability(content)
        insights['readability'] = readability
        
        # Sentiment indicators
        sentiment = self.analyze_sentiment_indicators(content)
        insights['sentiment_indicators'] = sentiment
        
        return insights