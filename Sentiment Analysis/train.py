#!/usr/bin/env python3
"""
Fine-tuning script for emotion classification
Optional: Fine-tune the model on custom emotion data
"""

import argparse
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import numpy as np
import os


class EmotionDataset(Dataset):
    """Custom dataset for emotion classification"""
    
    def __init__(self, texts, labels, tokenizer, max_length=512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }


def load_data(csv_path):
    """Load training data from CSV"""
    df = pd.read_csv(csv_path)
    
    if 'text' not in df.columns or 'emotion' not in df.columns:
        raise ValueError("CSV must contain 'text' and 'emotion' columns")
    
    return df['text'].tolist(), df['emotion'].tolist()


def compute_metrics(eval_pred):
    """Compute accuracy metrics"""
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    accuracy = (predictions == labels).mean()
    return {'accuracy': accuracy}


def export_to_onnx(model, tokenizer, output_path, sample_text="I am happy"):
    """Export model to ONNX format"""
    print(f"Exporting model to ONNX: {output_path}")
    
    # Prepare dummy input
    inputs = tokenizer(
        sample_text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=512
    )
    
    # Export
    torch.onnx.export(
        model,
        (inputs['input_ids'], inputs['attention_mask']),
        output_path,
        input_names=['input_ids', 'attention_mask'],
        output_names=['logits'],
        dynamic_axes={
            'input_ids': {0: 'batch_size', 1: 'sequence_length'},
            'attention_mask': {0: 'batch_size', 1: 'sequence_length'},
            'logits': {0: 'batch_size'}
        },
        opset_version=14
    )
    
    print(f"Model exported successfully to {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Fine-tune emotion classification model')
    parser.add_argument(
        '--data',
        type=str,
        required=True,
        help='Path to training CSV (must have "text" and "emotion" columns)'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='bhadresh-savani/distilbert-base-uncased-go-emotions-student',
        help='Base model to fine-tune'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='./fine_tuned_model',
        help='Output directory for fine-tuned model'
    )
    parser.add_argument(
        '--epochs',
        type=int,
        default=3,
        help='Number of training epochs'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=16,
        help='Training batch size'
    )
    parser.add_argument(
        '--learning-rate',
        type=float,
        default=2e-5,
        help='Learning rate'
    )
    parser.add_argument(
        '--test-size',
        type=float,
        default=0.2,
        help='Proportion of data to use for testing'
    )
    parser.add_argument(
        '--export-onnx',
        action='store_true',
        help='Export model to ONNX format after training'
    )
    parser.add_argument(
        '--onnx-path',
        type=str,
        default='../onnx/emotion_model.onnx',
        help='Path for ONNX export'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Emotion Classification Fine-Tuning")
    print("=" * 60)
    
    # Load data
    print(f"\nLoading data from {args.data}...")
    texts, emotions = load_data(args.data)
    print(f"Loaded {len(texts)} samples")
    
    # Encode labels
    label_encoder = LabelEncoder()
    labels = label_encoder.fit_transform(emotions)
    num_labels = len(label_encoder.classes_)
    
    print(f"Number of emotion classes: {num_labels}")
    print(f"Classes: {list(label_encoder.classes_)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels,
        test_size=args.test_size,
        random_state=42,
        stratify=labels
    )
    
    print(f"Training samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")
    
    # Load tokenizer and model
    print(f"\nLoading model: {args.model}...")
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForSequenceClassification.from_pretrained(
        args.model,
        num_labels=num_labels
    )
    
    # Create datasets
    train_dataset = EmotionDataset(X_train, y_train, tokenizer)
    test_dataset = EmotionDataset(X_test, y_test, tokenizer)
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=args.output,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        weight_decay=0.01,
        logging_dir=f'{args.output}/logs',
        logging_steps=10,
        evaluation_strategy='epoch',
        save_strategy='epoch',
        load_best_model_at_end=True,
        metric_for_best_model='accuracy',
        greater_is_better=True,
        warmup_steps=100,
        fp16=torch.cuda.is_available(),
    )
    
    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
    )
    
    # Train
    print("\nStarting training...")
    trainer.train()
    
    # Evaluate
    print("\nEvaluating on test set...")
    results = trainer.evaluate()
    print(f"Test Accuracy: {results['eval_accuracy']:.4f}")
    
    # Save model
    print(f"\nSaving model to {args.output}...")
    trainer.save_model(args.output)
    tokenizer.save_pretrained(args.output)
    
    # Save label encoder
    label_mapping = {i: label for i, label in enumerate(label_encoder.classes_)}
    import json
    with open(os.path.join(args.output, 'label_mapping.json'), 'w') as f:
        json.dump(label_mapping, f, indent=2)
    
    print("Training complete!")
    
    # Export to ONNX if requested
    if args.export_onnx:
        os.makedirs(os.path.dirname(args.onnx_path), exist_ok=True)
        export_to_onnx(model, tokenizer, args.onnx_path)
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == '__main__':
    main()