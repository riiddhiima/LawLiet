# from bert_score import score
# import numpy as np

# class ChatbotEvaluator:
#     def __init__(self):
#         pass
    
#     def exact_match(self, predicted, ground_truth):
#         return 1 if predicted.strip().lower() == ground_truth.strip().lower() else 0
    
#     def semantic_similarity(self, predicted, ground_truth):
#         P, R, F1 = score([predicted], [ground_truth], lang="en", model_type='roberta-large' ,verbose=False)
#         # P, R, F1 = score([predicted], [ground_truth], lang="en", model_type='bert-base-uncased', verbose=False)
#         return {
#             "precision": float(P.mean()),
#             "recall": float(R.mean()),
#             "f1": float(F1.mean())
#         }
    
#     def evaluate_response(self, predicted, ground_truth):
#         return {
#             "exact_match": self.exact_match(predicted, ground_truth),
#             "semantic_similarity": self.semantic_similarity(predicted, ground_truth)
#         }

#************************************************************************

from bert_score import score as bert_score
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, confusion_matrix

class ChatbotEvaluator:
    def __init__(self, semantic_threshold=0.85):
        self.semantic_threshold = semantic_threshold
        self.predicted_classes = []
        self.true_classes = []

    def exact_match(self, predicted, ground_truth):
        return 1 if predicted.strip().lower() == ground_truth.strip().lower() else 0

    def semantic_similarity(self, predicted, ground_truth):
        P, R, F1 = bert_score([predicted], [ground_truth], lang="en", model_type='roberta-large', verbose=False)
        return {
            "precision": float(P.mean()),
            "recall": float(R.mean()),
            "f1": float(F1.mean())
        }

    def classify_by_semantic_score(self, actual_reply, expected_reply):
    # If expected reply is a rejection message, then it's a non-legal question
        if "I am sorry but my sources do not address this question. I am an AI chatbot that answers questions only about Indian legal documents." in expected_reply or "do not address this question" in expected_reply:
            return "non_legal"
    # Otherwise, if the answer is similar enough, it's legal
        return "legal" if self.semantic_similarity(actual_reply, expected_reply)['f1'] >= self.semantic_threshold else "non_legal"

    def evaluate_response(self, predicted, ground_truth, true_label):
        semantic = self.semantic_similarity(predicted, ground_truth)
        predicted_class = self.classify_by_semantic_score(predicted, ground_truth)

        self.predicted_classes.append(predicted_class)
        self.true_classes.append(true_label)

        return {
            "exact_match": self.exact_match(predicted, ground_truth),
            "semantic_similarity": semantic
        }

    def compute_metrics(self):
        labels = ["legal", "non_legal"]
        return {
            "accuracy": accuracy_score(self.true_classes, self.predicted_classes),
            "precision": precision_score(self.true_classes, self.predicted_classes, labels=labels, average='macro', zero_division=0),
            "recall": recall_score(self.true_classes, self.predicted_classes, labels=labels, average='macro', zero_division=0),
            "f1_score": f1_score(self.true_classes, self.predicted_classes, labels=labels, average='macro', zero_division=0),
            "confusion_matrix": confusion_matrix(self.true_classes, self.predicted_classes, labels=labels),
            "labels": labels
        }
