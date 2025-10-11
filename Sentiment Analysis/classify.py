#!/usr/bin/env python3
"""
Emotion Classification using Hugging Face Transformers
Model: MODEL_NAME = "bhadresh-savani/distilroberta-base-go-emotions"
"""

import argparse
import json
import sys
from typing import List, Dict, Any
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import warnings

warnings.filterwarnings('ignore')


class EmotionClassifier:
    """Emotion classifier using pretrained GoEmotions model"""
    
    MODEL_NAME = "bhadresh-savani/distilroberta-base-go-emotions"
    
    # GoEmotions label mapping
    EMOTION_LABELS = [
        'admiration', 'amusement', 'anger', 'annoyance', 'approval', 'caring',
        'confusion', 'curiosity', 'desire', 'disappointment', 'disapproval',
        'disgust', 'embarrassment', 'excitement', 'fear', 'gratitude', 'grief',
        'joy', 'love', 'nervousness', 'optimism', 'pride', 'realization',
        'relief', 'remorse', 'sadness', 'surprise', 'neutral'
    ]
    
    # Map GoEmotions to simplified emotions for playlist matching
    EMOTION_MAPPING = {
        'joy': 'happy',
        'amusement': 'happy',
        'excitement': 'excited',
        'optimism': 'excited',
        'approval': 'happy',
        'admiration': 'happy',
        'gratitude': 'happy',
        'love': 'happy',
        'pride': 'excited',
        'relief': 'happy',
        'sadness': 'sad',
        'grief': 'sad',
        'disappointment': 'sad',
        'remorse': 'sad',
        'embarrassment': 'sad',
        'nervousness': 'sad',
        'fear': 'sad',
        'anger': 'sad',
        'annoyance': 'sad',
        'disapproval': 'sad',
        'disgust': 'sad',
        'neutral': 'neutral',
        'realization': 'neutral',
        'confusion': 'neutral',
        'curiosity': 'neutral',
        'surprise': 'excited',
        'desire': 'excited',
        'caring': 'happy'
    }
    
    def __init__(self, model_name: str = None, device: str = None):
        """
        Initialize the emotion classifier
        
        Args:
            model_name: Hugging Face model name (default: GoEmotions)
            device: Device to run inference on ('cuda', 'cpu', or None for auto)
        """
        self.model_name = model_name or self.MODEL_NAME
        
        # Determine device
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
        
        print(f"Loading model: {self.model_name}", file=sys.stderr)
        print(f"Using device: {self.device}", file=sys.stderr)
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name
        ).to(self.device)
        self.model.eval()
        
        print("Model loaded successfully!", file=sys.stderr)
    
    def classify(self, text: str, top_k: int = 3, threshold: float = 0.1) -> Dict[str, Any]:
        """
        Classify emotions in text
        
        Args:
            text: Input text to classify
            top_k: Number of top emotions to return
            threshold: Minimum score threshold for emotions
            
        Returns:
            Dictionary with raw emotions, simplified emotions, and scores
        """
        # Tokenize input
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        ).to(self.device)
        
        # Run inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)[0]
        
        # Get top emotions
        scores, indices = torch.topk(probs, k=min(top_k, len(probs)))
        
        raw_emotions = []
        simplified_emotions = set()
        
        for score, idx in zip(scores.tolist(), indices.tolist()):
            if score >= threshold:
                emotion_label = self.EMOTION_LABELS[idx]
                raw_emotions.append({
                    'emotion': emotion_label,
                    'score': round(score, 4)
                })
                
                # Map to simplified emotion
                simplified = self.EMOTION_MAPPING.get(emotion_label, 'neutral')
                simplified_emotions.add(simplified)
        
        return {
            'text': text,
            'raw_emotions': raw_emotions,
            'simplified_emotions': sorted(list(simplified_emotions)),
            'dominant_emotion': raw_emotions[0]['emotion'] if raw_emotions else 'neutral',
            'confidence': raw_emotions[0]['score'] if raw_emotions else 0.0
        }
    
    def batch_classify(self, texts: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Classify multiple texts
        
        Args:
            texts: List of input texts
            **kwargs: Additional arguments passed to classify()
            
        Returns:
            List of classification results
        """
        return [self.classify(text, **kwargs) for text in texts]


def main():
    parser = argparse.ArgumentParser(
        description='Classify emotions in text using GoEmotions model'
    )
    parser.add_argument(
        '--text',
        type=str,
        help='Text to classify'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='File containing text to classify (one per line)'
    )
    parser.add_argument(
        '--top-k',
        type=int,
        default=3,
        help='Number of top emotions to return (default: 3)'
    )
    parser.add_argument(
        '--threshold',
        type=float,
        default=0.1,
        help='Minimum score threshold (default: 0.1)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )
    parser.add_argument(
        '--device',
        type=str,
        choices=['cuda', 'cpu'],
        help='Device to use for inference'
    )
    
    args = parser.parse_args()
    
    # Validate input
    if not args.text and not args.file:
        parser.error("Either --text or --file must be provided")
    
    # Initialize classifier
    classifier = EmotionClassifier(device=args.device)
    
    # Get texts to classify
    texts = []
    if args.text:
        texts.append(args.text)
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            texts.extend([line.strip() for line in f if line.strip()])
    
    # Classify
    results = []
    for text in texts:
        result = classifier.classify(
            text,
            top_k=args.top_k,
            threshold=args.threshold
        )
        results.append(result)
    
    # Output results
    if args.json:
        if len(results) == 1:
            print(json.dumps(results[0], indent=2))
        else:
            print(json.dumps(results, indent=2))
    else:
        for result in results:
            print(f"\nText: {result['text']}")
            print(f"Dominant: {result['dominant_emotion']} ({result['confidence']:.2%})")
            print(f"Simplified emotions: {', '.join(result['simplified_emotions'])}")
            print("Raw emotions:")
            for emotion in result['raw_emotions']:
                print(f"  - {emotion['emotion']}: {emotion['score']:.2%}")


if __name__ == '__main__':
    main()
