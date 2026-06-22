
# Label Taxonomy

This is given in planning.md under Labeling




# Fine-Tuning Pipeline

1. Base Model and Training Platform:

Base Model: The base model used for fine-tuning is distilbert-base-uncased from the Hugging Face Transformers library.
Training Platform: The training is conducted in a Google Colab environment, leveraging its GPU capabilities (as indicated by "Using GPU: Tesla T4").
2. Key Training Decisions and Justification:

Class Weighting: A crucial training decision implemented in this notebook is the use of class weighting. This was introduced to address the significant class imbalance observed in the dataset, particularly the underrepresentation of labels like 'sports-news'. By computing and applying class_weights to the loss function via a CustomTrainer, the model is encouraged to pay more attention to the minority classes during training, which helps prevent them from being overlooked and improves their classification metrics (e.g., precision, recall, F1-score).
Number of Epochs (num_train_epochs=3): This value is a common starting point for fine-tuning pre-trained language models on relatively small datasets. With limited data, a lower number of epochs helps to prevent overfitting to the training set while still allowing the model to adapt to the specific task and dataset characteristics.

# Results (Evaluation Report and Error Analysis):

first run accuracy metrics:
sample size:
40 rows written — sports-news: 13, educative: 12, entertaining: 15.

{
    "accuracy": 0.5,
    "precision": {
        "educative": 1.0,
        "entertaining": 0.0,
        "sports-news": 0.4
    },
    "recall": {
        "educative": 0.5,
        "entertaining": 0.0,
        "sports-news": 1.0
    },
    "f1": {
        "educative": 0.6666666666666666,
        "entertaining": 0.0,
        "sports-news": 0.5714285714285714
    },
    "overall_accuracy": 0.5
}

![Confusion Matrix (Fine-tuned Model)](result.png)

1. Specific Wrong Predictions & Analysis:

Prediction 1: True Label 'entertaining', Predicted 'sports-news'

Text (original index 27): "168 years ago today, Paul Morphy arrived in Eu..."
Explanation: This text describes a historical event involving a famous chess player. While it could be viewed as 'entertaining' due to its narrative quality, the model likely associated the mention of "Paul Morphy" and the historical context of a notable chess figure with 'sports-news'. This suggests the model over-prioritizes the 'sports' aspect of chess over the 'narrative/historical' aspect that leans towards 'entertaining', possibly due to a limited understanding of nuanced content types within the chess domain.
Prediction 2: True Label 'educative', Predicted 'sports-news'

Text (original index 17): "Venting about the Catalan\n\nChess is such a b..."
Explanation: This text directly discusses a chess opening ("Catalan") and a user's experience with it, which is fundamentally 'educative' content related to strategy and learning. The model incorrectly classified it as 'sports-news'. This is a clear instance of the model associating generic chess-related terms with 'sports-news', failing to distinguish between discussion/instructional content and actual news reporting about events.
Prediction 3: True Label 'entertaining', Predicted 'sports-news'

Text (original index 30): "Magnus Carlsen signs an autograph as Fabiano C..."
Explanation: This text describes an informal, anecdotal interaction between chess grandmasters (Magnus Carlsen, Fabiano Caruana) and includes casual commentary. While it involves figures from the sports world, the content itself is lighthearted and social, fitting 'entertaining'. The model again defaulted to 'sports-news', indicating a strong tendency to classify any mention of prominent chess players or related activities as news, irrespective of the conversational or informal tone of the text.
2. Reflection on the Gap and Specific Failure Pattern:

Specific Failure Pattern: Over-generalization of 'sports-news' for chess-related content.

The most prominent failure pattern observed is the model's consistent tendency to misclassify content belonging to 'educative' or 'entertaining' as 'sports-news' when the topic involves chess. This suggests a significant gap between what the model captured and what was intended:

What the model captured: The model primarily learned to associate keywords and entities like "chess," "Magnus Carlsen," "Paul Morphy," and names of chess openings (e.g., "Catalan") strongly with the 'sports-news' label. It successfully identified the topic of the texts as being related to chess/sports figures.

What was intended: The intention was for the model to differentiate the purpose or genre of the text beyond just the topic. For example, a discussion about chess strategy should be 'educative', a historical anecdote about a chess player should be 'entertaining', and only reports about current matches, tournaments, or results should be 'sports-news'.

This specific failure pattern indicates that the model has not adequately learned the subtle contextual and stylistic cues that distinguish between different types of chess-related content. It struggles to understand the nuanced 'label boundaries' between categories that share a common overarching subject (chess) but differ in their informational or emotional intent. This could be exacerbated by the small dataset, where the model might lack sufficient diverse examples within the 'educative' and 'entertaining' classes to form distinct decision boundaries away from the dominant 'sports-news' feature space.


# Improvements:

steps taken to improve the metrics:
1. get training data set to 210 rows
2. make sure no class imballance or no significant class imballance exists
3. synthetically generate 15% more data
4. add more crucial data from the reddit raw json


further more sophiticated/complex steps which are less practical:
1. Class Weighting to recitify class imballance
2. Hyperparameter Tuning
3. Cross-Validation
4. Different Model Architectures
5. try to annotonate the edge cases and include more data from the raw data that could help place the edge cases accurately. 
6. playing around with the comments: change the comments limit, add a text limit for each comment


# AI Usage and Spec Reflection

## Instance 1

Initial prompt: use the reddit api to create a raw data set. 
Overrode: overrode multiple attempts to accomplish the task to no avail. There was no such reddit api that is easily accessible and so the AI was just generate code that looked that it could work.

## Instance 2
Intial prompt: create a training data set from the raw data.
Overrode: Realising that a training dataset is not useful if certain conditions are not met I kept a 10 file limit for each label/class in the training data set. If the raw data does not have the 10 file limit we error out side such a training dataset will not be useful. 

Note: the annotation was done without use of AI. I might use it to generate synthetic data but that is an improvement task that I only might do. 



# Baseline Comparison

1. Baseline Approach Description:

Approach: The baseline uses a zero-shot classification approach via the Groq API (powered by the llama-3.3-70b-versatile LLM).
Prompt Used: The classification prompt template is:
You are an expert text classifier. Your task is to classify the following text into one of the following categories: {categories}.

Output ONLY the label name. Do not include any other text, punctuation, or explanations.

Text: {text_to_classify}
Label:
The {categories} placeholder is dynamically filled with educative, entertaining, sports-news, and {text_to_classify} is filled with the text from the test set. The temperature parameter for the Groq API call is set to 0.0 to ensure deterministic output.
How Results Were Collected: Each text sample from the test set (X_test) is sent to the Groq API with the formatted prompt. The API's response (which is expected to be only the label name) is collected as the prediction. Unparseable responses are handled, and a classification report is then generated based on these predictions against the actual labels.
2. Evaluation Report Shows Performance Metrics for Both Fine-Tuned Model and Baseline on the Same Test Set:

Same Test Set: Yes, both the fine-tuned model and the baseline model are evaluated on the exact same test set. This test set is created in Section 2: Dataset Split and Tokenization (cell c1668f6a) using X_test and y_test after a stratified split.
Performance Metrics:
The baseline model's performance metrics (Overall Accuracy and Classification Report) are printed directly in the output of Section 5: Baseline with Groq API (cell 5ead0f82).
The fine-tuned model's performance metrics (Overall Accuracy and Classification Report) are printed in the output of Section 4: Evaluate Fine-Tuned Model (cell b2c06a66). This section also explicitly saves these results to evaluation_results.json and a confusion matrix to confusion_matrix.png.