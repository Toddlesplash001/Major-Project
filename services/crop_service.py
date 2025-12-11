import pickle

# Load trained model
with open("models/crop_recommendation_model.pkl", "rb") as f:
    crop_model = pickle.load(f)

# Your same mapping
crop_dict = { 
    'rice': 1, 'maize': 2, 'jute': 3, 'cotton': 4, 'coconut': 5,
    'papaya': 6, 'orange': 7, 'apple': 8, 'muskmelon': 9, 'watermelon': 10,
    'grapes': 11, 'mango': 12, 'banana': 13, 'pomegranate': 14, 'lentil': 15,
    'blackgram': 16, 'mungbean': 17, 'mothbeans': 18, 'pigeonpeas': 19,
    'kidneybeans': 20, 'chickpea': 21, 'coffee': 22
}
inv_crop_dict = {v: k for k, v in crop_dict.items()}

def recommend_crop(N, P, K, temperature, humidity, ph, rainfall):
    features = [[N, P, K, temperature, humidity, ph, rainfall]]
    encoded_prediction = crop_model.predict(features)[0]  # e.g., 1, 2, 3
    decoded_prediction = inv_crop_dict[encoded_prediction]  # map to crop name
    return decoded_prediction
