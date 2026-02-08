const BASE_URL = "http://127.0.0.1:5000";

export async function predictFertilizer(data) {
  const response = await fetch(`${BASE_URL}/predict`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(data)
  });

  if (!response.ok) {
    throw new Error("Predict request failed");
  }

  return response.json();
}

export async function submitFertilizerData(data) {
  const response = await fetch(`${BASE_URL}/submit-data`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(data)
  });

  if (!response.ok) {
    throw new Error("Submit request failed");
  }

  return response.json();
}

export async function fetchHistory(userId = 1, limit = 10) {
  const response = await fetch(
    `${BASE_URL}/history?user_id=${userId}&limit=${limit}`
  );

  if (!response.ok) {
    throw new Error("History request failed");
  }

  return response.json();
}
