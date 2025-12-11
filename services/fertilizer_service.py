import pickle

# Load model and encoder together
with open("models/fertilizer_model.pkl", "rb") as f:
    fertilizer_model, encode_ferti = pickle.load(f)


def recommend_fertilizer(N, P, K):
    features = [[N, P, K]]
    encoded_pred = fertilizer_model.predict(features)[0]
    decoded_pred = encode_ferti.inverse_transform([encoded_pred])[0]  # convert number → fertilizer name
    return decoded_pred
