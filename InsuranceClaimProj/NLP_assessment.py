from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import cv2
from ultralytics import YOLO

__model = None


# Preprocess function for text data (user description and labels)
def preprocess_text(text):
  tokens = word_tokenize(text.lower())
  stop_words = set(stopwords.words('english'))
  filtered_tokens = [token for token in tokens if token not in stop_words]
  return filtered_tokens
# Define model loading function (flexible for different models)
def load_model(model_path):
    global __model
    """Loads the specified object detection model.

    Args:
        model_path (str): Path to the pre-trained model weights.

    Returns:
        object: Loaded object detection model object (replace with your model's logic)
    """
    # Load the YOLOv8 model from the specified path
    __model = YOLO(model_path)
    return model  # Return the loaded YOLO model
# Function to detect damage and extract labels
def detect_damage(image_path, model):
    """Performs object detection and extracts labels from an image.

    Args:
        image_path (str): Path to the image.
        model (object): Loaded object detection model object.

    Returns:
        list, None: List of detected labels (if successful), None otherwise.
    """

    try:
        # Load the image
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"Image not found or unable to load: {image_path}")

        # Perform inference using the YOLO model
        results = model.predict(img)

        # Extract detected labels (modify based on your model's output structure)
        # Access the 'names' attribute of the model to get class labels
        labels = [model.names[int(result.boxes.cls[i])] for result in results for i in range(len(result.boxes.cls))] if results else None
        return labels

    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # Indicate error


# Function to match description and labels with confidence
def match_labels_nlp(user_description, image_name):
  
  detected_labels = detect_damage(image_name, model)

  if detected_labels is None:
    return "Error: Label extraction failed."
  elif not detected_labels:
    return "No damage detected."
  else:
    # Preprocess user description and labels
    user_description_tokens = preprocess_text(user_description)
    label_tokens = [preprocess_text(label) for label in detected_labels]

    # Calculate exact match score (already implemented)
    exact_match_score = 1 if user_description.lower() in [label.lower() for label in detected_labels] else 0

    # Calculate word overlap score
    word_overlap_score = sum(len(set(user_description_tokens).intersection(label_tokens)) for label_tokens in label_tokens)

    # (Optional) Calculate word embedding similarity using libraries like gensim

    # Combine scores and determine confidence level (adjust weights based on your needs)
    confidence = 0.7 * exact_match_score + 0.3 * word_overlap_score # + weight * word_embedding_similarity (if implemented)

    if confidence >= 0.5:
      return True
    else:
      return False
    # # Upload the image and run detection
# uploaded = google.colab.files.upload()
# model = load_model("/content/best.pt")  # Replace with your model path

# for image_name in uploaded.keys():
#     detected_labels = detect_damage(image_name, model)
#     match_message = match_labels_nlp(detected_labels, user_description=input("Enter damage description: "))
#     print(match_message)

model = load_model("/content/best.pt")
print("hi")