import axios from "axios";

export const loginUser = async (email, password) => {
  const response = await axios.post("/api/login", { email, password });
  return response.data;
};

export const signupUser = async (username, email, password) => {
  const response = await axios.post("/api/signup", { username, email, password });
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await axios.get("/api/current_user");
  return response.data;
};

export const logoutUser = async () => {
  await axios.post("/api/logout");
};
